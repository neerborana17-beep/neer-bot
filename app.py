import requests
import json
import time
import sys
import threading
import os
import random
from datetime import datetime

# 1. अपनी OpenRouter API Key यहाँ डालें
API_KEY = st.secrets["OPENROUTER_API_KEY"]
MEMORY_FILE = "neer_memory.json"

# --- UI Header Section (Clean White & Bold) ---
def print_header():
    # Screen clear karo
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Neer: Bold White | Online: Green
    # \033[1;37m se Bright White Bold hota hai
    name_style = """
 \033[1;37mN E E R\033[0m
 \033[32monline\033[0m
    """
    print(name_style)
    print("-" * 20)
    print("")

# --------------------------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: pass
    return [{
        "role": "system", 
        "content": "Tera naam Neer hai. Tu ek smart friend hai jo 'Mood Tracker' use karta hai. Important baatein yaad rakh. Hinglish use kar, short reh aur chill vibes de."
    }]

def save_memory(messages):
    important_messages = [messages[0]]
    for msg in messages[1:]:
        if len(msg['content']) > 10 or msg['role'] == 'assistant':
            important_messages.append(msg)
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(important_messages[-15:], f)

messages = load_memory()
last_message_time = time.time()
stop_threads = False
stop_typing = True

def typing_animation():
    chars = [".  ", ".. ", "...", "   "]
    i = 0
    while not stop_typing:
        sys.stdout.write(f"\rtyping{chars[i % 4]}\033[K")
        sys.stdout.flush()
        time.sleep(0.4)
        i += 1
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def get_neer_response(user_input, is_proactive=False):
    global stop_typing
    now = datetime.now()
    ctx = f"(Time {now.strftime('%I:%M %p')}). "
    
    if is_proactive:
        content = ctx + "Search for something specific or comment on user's recent mood. Be brief."
    else:
        content = ctx + f"User: {user_input}"
        
    messages.append({"role": "user", "content": content})

    stop_typing = False
    t = threading.Thread(target=typing_animation)
    t.start()
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": "google/gemini-2.0-flash-001", 
                "messages": messages,
                "max_tokens": 70,
                "tools": [{"type": "web_search"}]
            })
        )
        stop_typing = True
        t.join()
        
        reply = response.json()['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": reply})
        save_memory(messages)
        return reply
    except:
        stop_typing = True
        return None

def proactive_loop():
    global last_message_time, stop_threads
    while not stop_threads:
        time.sleep(30)
        if time.time() - last_message_time > 150: 
            jawab = get_neer_response("", is_proactive=True)
            if jawab:
                print(f"\nNeer: {jawab}")
                print("You: ", end="", flush=True)
                last_message_time = time.time()

# --- Main Program ---
print_header()

threading.Thread(target=proactive_loop, daemon=True).start()

try:
    while True:
        user_puchha = input("\033[KYou: ")
        last_message_time = time.time()
        if not user_puchha.strip(): continue
        if user_puchha.lower() in ["bye", "exit"]: break
            
        jawab = get_neer_response(user_puchha)
        if jawab: print(f"\rNeer: {jawab}")
except KeyboardInterrupt:
    pass
save_memory(messages)
    
