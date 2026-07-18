import os
import threading
import time
import telebot
import requests
import json
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "AI Bot Is Running 24/7 Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = "8833753095:AAFZzMUiSVybSDp9fWhzehHKSMrOt2lpcfw"
ADMIN_ID = "61592033909178"
GEMINI_API_KEY = "AIzaSyBGnXM7F8zCg_sYypqMGavROxevdTjhyV4"

bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_INSTRUCTION = """
မင်းက Htet Myat Ko Ko ရဲ့ Digital Service Shop က အချိုသာဆုံး၊ အကျဉ်းဆုံးနဲ့ လုပ်ငန်းကျွမ်းကျင်မှုအရှိဆုံး AI Customer Service ဖြစ်တယ်။ ဝယ်သူတွေကို သာယာပျော့ပျောင်းတဲ့ လေသံနဲ့ 'ခင်ဗျာ' သုံးပြီး ဖြေပေးပါ။

[ဈေးနှုန်းစာရင်း (Price List)]
- PayPal business us/uk region: 3000 kyats
- PayPal business ca region: 5000 kyats
- PayPal personal ca region: 8000 kyats
- PayPal limit error ဖြေရှင်းခ: 5000 kyats
- PayPal id error ဖြေရှင်းခ: 12000 kyats
- Japan TikTok account: 5000 kyats
- Faq error ဖြေရှင်းခ: 2000 kyats
- TikTok Monetization service: 32000 kyats
- Telegram bot(ai): 42000 kyats (2 ရက် စောင့်ရမည်)
- Telegram bot (ธรรมဒါ): 3000 kyats

[ငွေချေမှု စည်းကမ်းချက် (Payment Policy)]
- Error တက်တာတွေ ဖြေရှင်းခြင်း နှင့် Telegram Bot ဆောက်ခြင်း လုပ်ငန်းများအတွက် 'ငွေကြိုချေရမည်' ဖြစ်သည်။
- ကျန်ရှိသော အကောင့်အရောင်းများအတွက် 'อကောင့်ရမှ ငွေချေနိုင်သည်'။

[ငွေပေးချေမှု အချက်အလက်]
- Wave Money: 09682170021 (Account Name: Htetmyatkoko)
- Kpay သည် လက်ရှိတွင် လုံးဝ(လုံးဝ) အသုံးပြု၍ မရနိုင်သေးပါ။

[FAQ ဖြေရှင်းပေးရမည့် နည်းပညာများ]
- PayPal account/ Japan TikTok account များ ပျက်စီးခြင်း၊ အသုံးပြုနည်းများ၊ TikTok monetization အကြောင်းများနှင့် PayPal error များ တက်ပါက ဝယ်သူ စိတ်ကျေနပ်အောင် အကောင်းဆုံး ရှင်းပြပြီး ကူညီဖြေရှင်းပေးပါ။

[အရေးကြီးသော အမိန့်]
- ဝယ်သူက ပစ္စည်းတစ်ခုခုကို 'ဝယ်မယ်' ဟု အတိအကျ ပြောလာပါက သို့မဟုတ် Ngwe lwe မည်ဟု ပြောလာပါက လိုအပ်သော ငွေပမာဏနှင့် Wave Money အကောင့်ကို ညွှန်ပြပေးပြီး Admin ဆီကနေ ဆက်သွယ်ပေးမည့်အကြောင်း ပြောပါ။
"""

def ask_gemini_via_rest(user_name, user_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"ဝယ်သူအမည်: {user_name}\nမေးခွန်း: {user_text}"}]
        }],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API Error: {response.text}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 မင်္ဂလာပါခင်ဗျာ! Htet Myat Ko Ko ရဲ့ Digital Services Shop မှ ကြိုဆိုပါတယ်။\n\n"
        "✨ ကျွန်တော်ကတော့ လူကြီးမင်းတို့ကို အကောင်းဆုံး ဝန်ဆောင်မှုပေးမယ့် AI Assistant ဖြစ်ပါတယ်။\n\n"
        "📦 PayPal/Japan TikTok အကောင့်ဝယ်ယူခြင်း၊ TikTok Monetization ဝန်ဆောင်မှု နှင့် "
        "PayPal Error မျိုးစုံအတွက် သိလိုသည်များကို စာရိုက်ပြီး တိုက်ရိုက် မေးမြန်းနိုင်ပါတယ်ခင်ဗျာ။"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_text = message.text
    if not user_text: return
    
    first_name = message.from_user.first_name
    username = message.from_user.username or "Username မရှိပါ"
    user_id = message.from_user.id
    
    try:
        ai_reply = ask_gemini_via_rest(first_name, user_text)
        bot.reply_to(message, ai_reply)
        
        order_keywords = ["ဝယ်", "ယူမယ်", "လွှဲ", "ဈေး", "order", "buy", "ချင်လို့"]
        if any(keyword in user_text.lower() for keyword in order_keywords):
            admin_alert = (
                "🚨 **Order/Inquiry သတိပေးချက်!**\n\n"
                f"👤 **ဝယ်သူ:** {first_name} (@{username})\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"💬 **ပြောဆိုချက်:** {user_text}"
            )
            bot.send_message(ADMIN_ID, admin_alert, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "ခေတ္တစောင့်ဆိုင်းပေးပါခင်ဗျာ၊ စနစ်အတွင်း အနည်းငယ် ကြန့်ကြာမှု ဖြစ်ပေါ်နေလို့ပါ။")

def run_bot():
    print("🚀 AI Bot Polling Started...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"🔄 Reconnecting due to error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    run_bot()
  
