#!/usr/bin/env python3
import os
import sys
import time
import requests
import json
import math
from collections import Counter

# ✅ Auto install cfonts if missing
try:
    from cfonts import render
except ImportError:
    os.system('pip install python-cfonts')
    from cfonts import render

# --- TELEGRAM CONFIGURATION ---
BOT_TOKEN = "8647473510:AAHO_JOpe4iOPCiznS4RDhnIt66jD0-8GC8"
CHAT_ID = "-1003526718749"

# --- GLOBAL SETTINGS ---
TARGET_WINS = 15
CURRENT_WINS = 0
MAX_HISTORY_CHECK = 50  # Analyze last 50 rounds for deep learning

# --- HELPER FOR STYLING ---
def to_fancy_font(text):
    text = str(text).upper()
    num_map = {
        '0': '０', '1': '１', '2': '２', '3': '３', '4': '４',
        '5': '５', '6': '６', '7': '７', '8': '８', '9': '９'
    }
    for k, v in num_map.items():
        text = text.replace(k, v)
    text = text.replace("BIG", "ʙɪɢ").replace("SMALL", "ꜱᴍᴀʟʟ")
    text = text.replace("WIN", "ᴡɪɴ").replace("LOSS", "ʟᴏss")
    return text

# --- TELEGRAM FUNCTIONS ---
def send_prediction_to_telegram(period, prediction_display, pattern_name, confidence):
    global CURRENT_WINS
    short_period = period[-4:]
    period_styled = to_fancy_font(short_period)
    pred_styled = to_fancy_font(prediction_display)
    progress_styled = to_fancy_font(f"{CURRENT_WINS}/{TARGET_WINS}")
    
    text_to_send = (
        f"🔥 𝚃𝙴𝙰𝙼 𝚂𝙸𝙶𝙼𝙰 𝙰𝙸  🔥\n\n"
        f"📊 ᴘᴇʀɪᴏᴅ: **{period_styled}**\n\n"
        f"🎰 ᴘʀᴇᴅɪᴄᴛɪᴏɴ: **{pred_styled}**\n\n"
        f"🎯 ᴛᴀʀɢᴇᴛ: **{progress_styled}**\n\n"
        f"🧠 ʟᴏɢɪᴄ: `{pattern_name}`\n"
        f"⚡ ᴄᴏɴғɪᴅᴇɴᴄᴇ: {confidence}%\n\n"
        f"⏳ ᴡᴀɪᴛɪɴɢ ꜰᴏʀ ʀᴇꜱᴜʟᴛ...\n"
    )
    return send_text_only(text_to_send)

def send_text_only(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        resp_data = response.json()
        if resp_data.get("ok"):
             return resp_data["result"]["message_id"], "text"
    except requests.RequestException:
        pass 
    return None, None

def update_telegram_result(message_id, msg_type, period, prediction_display, win, result_val, is_jackpot):
    global CURRENT_WINS
    if not message_id: return
    
    short_period = period[-4:]
    period_styled = to_fancy_font(short_period)
    pred_styled = to_fancy_font(prediction_display)
    res_styled = to_fancy_font(result_val)
    
    status = "💎 ᴊᴀᴄᴋᴘᴏᴛ ᴡɪɴ 💎" if is_jackpot else ("✅ ᴡɪɴ 🏆" if win else "❌ ʟᴏss 💔")
    progress_styled = to_fancy_font(f"{CURRENT_WINS}/{TARGET_WINS}")

    new_text = (
        f"🔥 𝚃𝙴𝙰𝙼 𝚂𝙸𝙶𝙼𝙰 𝙰𝙸  🔥\n\n"
        f"📊 ᴘᴇʀɪᴏᴅ: **{period_styled}**\n\n"
        f"🎰 ᴘʀᴇᴅɪᴄᴛɪᴏɴ: **{pred_styled}**\n\n"
        f"🎯 ᴛᴀʀɢᴇᴛ: **{progress_styled}**\n\n"
        f"📝 ʀᴇꜱᴜʟᴛ ʀᴇᴘᴏʀᴛ\n\n"
        f"🎲 ʀᴇꜱᴜʟᴛ: **{res_styled}**\n\n"
        f"🏆 ꜱᴛᴀᴛᴜꜱ: {status}\n"
    )
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {"chat_id": CHAT_ID, "message_id": message_id, "text": new_text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception: pass

def send_stop_message():
    text = f"🛑 **SESSION FINISHED** 🛑\n\n🎯 ᴛᴀʀɢᴇᴛ ʀᴇᴀᴄʜᴇᴅ: **{TARGET_WINS}/{TARGET_WINS}** ✅"
    send_text_only(to_fancy_font(text))

# --- UTILS ---
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        render('TEAM SIGMA AI V2', colors=['red', 'yellow'], align='center')
    except: print("TEAM SIGMA AI V2")
    print(f"\n🔥 TARGET: {TARGET_WINS} | MODE: DEEP ANALYSIS (20+ LOGIC) 🔥\n")

# --- API ---
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts={}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Referer": "https://hgnice.biz"}

def get_big_small(number):
    return "BIG" if int(number) >= 5 else "SMALL"

def fetch_latest():
    try:
        ts = int(time.time() * 1000)
        response = requests.get(API_URL.format(ts), headers=HEADERS, timeout=10)
        data = response.json().get("data", {}).get("list", [])
        return data
    except requests.RequestException: return []

# --- 🧠 ADVANCED AI LOGIC FUNCTIONS ---

def calculate_rsi(data_points, period=14):
    """Calculates Relative Strength Index (RSI) to determine Overbought/Oversold"""
    if len(data_points) < period: return 50
    gains = []
    losses = []
    for i in range(1, period + 1):
        change = data_points[i-1] - data_points[i]
        if change > 0: gains.append(change)
        else: losses.append(abs(change))
    
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analyze_trend_pattern(type_history):
    """Detects patterns like Dragon (AAAA), PingPong (ABAB), Mirror (AABB)"""
    if len(type_history) < 6: return "RANDOM"
    
    recent = type_history[:6]
    
    # Dragon (Streak of 4+)
    if recent[0] == recent[1] == recent[2] == recent[3]:
        return "DRAGON STREAK"
    
    # ZigZag / PingPong (ABAB)
    if recent[0] != recent[1] and recent[1] != recent[2] and recent[2] != recent[3]:
        return "ZIGZAG 1-1"
        
    # Mirror (AABB)
    if recent[0] == recent[1] and recent[1] != recent[2] and recent[2] == recent[3]:
        return "MIRROR 2-2"
        
    # 2-1-2 Pattern (AABAA)
    if recent[0] == recent[1] and recent[1] != recent[2] and recent[2] != recent[3] and recent[3] == recent[4]:
        return "SANDWICH 2-1-2"

    return "VOLATILE"

def get_smart_prediction(history_list):
    print("\r⏳ ANALYZING 50+ DATA POINTS...", end="")
    sys.stdout.flush()
    time.sleep(1) 
    print("\r", end="")

    if not history_list or len(history_list) < 10:
        return "BIG 0", "BIG", "INITIALIZING", 0

    # --- 1. DATA PREPARATION ---
    nums = [int(x['number']) for x in history_list[:MAX_HISTORY_CHECK]]
    types = [get_big_small(x) for x in nums]
    
    score_big = 0
    score_small = 0
    active_logics = []

    # --- 2. PATTERN ANALYSIS (WEIGHTED VOTING) ---

    # Logic A: RSI (Reversion to Mean)
    # If numbers are consistently high, RSI is high -> Expect Drop (Small)
    rsi_val = calculate_rsi(nums, 14)
    if rsi_val > 70:
        score_small += 3
        active_logics.append("RSI OVERSOLD")
    elif rsi_val < 30:
        score_big += 3
        active_logics.append("RSI OVERBOUGHT")

    # Logic B: Streak Analysis (The "Cut" Logic)
    # If streak > 4, probability of break increases
    streak_count = 1
    for i in range(len(types)-1):
        if types[i] == types[i+1]: streak_count += 1
        else: break
    
    if streak_count >= 5:
        # Dangerous to bet against Dragon, but statistically likely to break soon
        if types[0] == "BIG": score_small += 4
        else: score_big += 4
        active_logics.append(f"STREAK BREAK ({streak_count})")
    elif streak_count <= 2:
        # Low streak, follow trend
        if types[0] == "BIG": score_big += 2
        else: score_small += 2
        active_logics.append("TREND FOLLOW")

    # Logic C: Pattern Matching
    pattern = analyze_trend_pattern(types)
    if pattern == "ZIGZAG 1-1":
        # Predict opposite of last
        if types[0] == "BIG": score_small += 3
        else: score_big += 3
        active_logics.append("ZIGZAG FLOW")
    elif pattern == "MIRROR 2-2":
        # If AA BB -> Expect AA next
        if types[0] == types[1]: # End of pair
            if types[0] == "BIG": score_small += 2 # Switch
            else: score_big += 2
            active_logics.append("MIRROR FLIP")
        else: # Start of pair
            if types[0] == "BIG": score_big += 2 # Match
            else: score_small += 2
            active_logics.append("MIRROR HOLD")

    # Logic D: Missing Number Recovery (Sum Modulo)
    # (Sum of last 3) % 10 -> indicates pressure
    sum_last_3 = sum(nums[:3])
    if sum_last_3 % 2 == 0: score_small += 1 # Even sums often trail small in this algo
    else: score_big += 1

    # --- 3. FINAL DECISION ---
    if score_big > score_small:
        final_type = "BIG"
        confidence = min(85 + (score_big - score_small) * 2, 98)
    elif score_small > score_big:
        final_type = "SMALL"
        confidence = min(85 + (score_small - score_big) * 2, 98)
    else:
        # Tie-breaker: Inverse of last result
        final_type = "SMALL" if types[0] == "BIG" else "BIG"
        confidence = 60
        active_logics.append("TIE BREAK")

    main_logic = active_logics[0] if active_logics else "HYBRID ANALYSIS"

    # --- 4. NUMBER SELECTION ---
    # Smart Number: Pick "Coldest" number in the target range (Big/Small)
    # But ensure it appeared at least once in last 30 (not dead)
    
    target_range = [5,6,7,8,9] if final_type == "BIG" else [0,1,2,3,4]
    
    history_30 = nums[:30]
    counts = Counter(history_30)
    
    # Sort by frequency (Ascending)
    sorted_candidates = sorted(target_range, key=lambda x: counts[x])
    
    # Pick the one that is "due" (Low frequency but not 0)
    best_number = sorted_candidates[0]
    for n in sorted_candidates:
        if counts[n] > 0: # Ensure it's active
            best_number = n
            break

    full_prediction = f"{final_type} {best_number}"
    
    return full_prediction, final_type, main_logic, int(confidence)

# --- MAIN LOOP ---
def print_prediction(period, prediction_display, pattern_name, confidence):
    is_big = "BIG" in prediction_display
    color = "\033[91m" if is_big else "\033[92m" # Red for Big, Green for Small
    reset = "\033[0m"
    
    print(f"[{CURRENT_WINS}/{TARGET_WINS}] 𝙿𝚎𝚛𝚒𝚘𝚍 ➞ {period}")
    print(f"𝙻𝚘𝚐𝚒𝚌 ➞ \033[96m{pattern_name}{reset}")
    print(f"𝙲𝚘𝚗𝚏𝚒𝚍𝚎𝚗𝚌𝚎 ➞ {confidence}%")
    print(f"𝙿𝚛𝚎ḍ𝚒𝚌𝚝𝚒𝚘𝚗 ➞ {color}{prediction_display}{reset}")
    sys.stdout.write("𝚁𝚎𝚜𝚞𝚕𝚝 ➞ ")
    sys.stdout.flush()
    return send_prediction_to_telegram(period, prediction_display, pattern_name, confidence)

def print_result(win, period, result_val, msg_id, msg_type, prediction_display, is_jackpot):
    if is_jackpot:
        sys.stdout.write("💎 JACKPOT WIN\n\n")
    else:
        sys.stdout.write("✅ WIN\n\n" if win else "❌ LOSS\n\n")
    sys.stdout.flush()
    
    update_telegram_result(msg_id, msg_type, period, prediction_display, win, result_val, is_jackpot)

def run_console():
    global CURRENT_WINS
    banner()
    seen_periods = set()
    prediction_info = None 

    while True:
        if CURRENT_WINS >= TARGET_WINS:
            print("\n🔥 TARGET ACHIEVED (15/15) - STOPPING SCRIPT 🔥")
            send_stop_message()
            break

        data = fetch_latest()
        if not data:
            time.sleep(2)
            continue

        latest = data[0]
        current_period = latest.get("issueNumber", "")
        result_number = latest.get("number", "")
        
        # ✅ CHECK PREVIOUS RESULT
        if prediction_info and prediction_info["period"] == current_period:
            real_result_type = get_big_small(result_number)
            win = prediction_info["logic_prediction"] == real_result_type
            real_result_display = f"{real_result_type} {result_number}"

            is_jackpot = False
            try:
                pred_parts = prediction_info["display_prediction"].split()
                if len(pred_parts) > 1 and win:
                    if int(pred_parts[1]) == int(result_number):
                        is_jackpot = True
            except: pass

            if win: CURRENT_WINS += 1

            print_result(
                win, current_period, real_result_display, 
                prediction_info["msg_id"], prediction_info["msg_type"],
                prediction_info["display_prediction"], is_jackpot
            )
            prediction_info = None

        # ✅ MAKE NEW PREDICTION
        if not prediction_info and current_period not in seen_periods and CURRENT_WINS < TARGET_WINS:
            seen_periods.add(current_period)
            
            if current_period.isdigit():
                next_period_full = str(int(current_period) + 1)
            else: continue

            # Uses NEW Pattern Logic
            display_pred, logic_pred, pat_name, conf = get_smart_prediction(data)

            msg_id, msg_type = print_prediction(next_period_full, display_pred, pat_name, conf)

            prediction_info = {
                "period": next_period_full,
                "display_prediction": display_pred,
                "logic_prediction": logic_pred,
                "msg_id": msg_id,
                "msg_type": msg_type
            }

        time.sleep(3)

if __name__ == "__main__":
    run_console()
 