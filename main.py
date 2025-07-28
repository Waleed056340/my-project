import openai
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont
import os
import asyncio
import re
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import io

openai.api_key = os.getenv("OPENAI_API_KEY").strip()
api_id = 23738221
api_hash = 'db2b1d85e692194967e53f78310e3ad1'

source_channel = 'https://t.me/RITKCHART'
destination_channel = 'https://t.me/BOT_TOPSPX0'

client = TelegramClient('forwarder_session', api_id, api_hash)

social_media_texts = [
    "لمتابعتنا علي برامج التواصل الاجتماعي",
    "x.com/ritkchart",
    "tiktok.com/@ritkchart",
    "snapchat.com/@farisb3x"
]

REPLACEMENT_TEXT = """دخوووول سريع 🚀
💸 ربح محتمل يبدأ من 30$ وأكثر
🧠 لا تطمع…
📈 ارفع وقفك دائمًا

📊 تحليل فني دقيق وتنفيذ فوري

⚠ تنبيه مهم:
📌 قرار الدخول أو الخروج مسؤوليتك الشخصية
⛔ القناة غير مسؤولة عن أي نتائج مالية"""

def clean_text(text):
    text = re.sub(r'\b100\$', '30$ فقط', text)
    text = re.sub(r'القناة\s*لا\s*تتحمل\s*أي\s*مسؤولية\s*✨?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\+?100\$', 'أكثر من 25٪', text)
    text = re.sub(r'⚠ تنبيه هام:', '⚠ تذكر:', text)
    text = re.sub(r'حسب سياسة القناة.*', '', text)
    text = re.sub(r'اشترك.*', '', text)
    return text.strip()

def extract_option_info(text):
    match_type = re.search(r'\b(CALL|PUT)\b', text, re.IGNORECASE)
    if match_type:
        contract_type_en = match_type.group(1).upper()
        contract_type_ar = "شراء" if contract_type_en == "CALL" else "بيع"
        return f"🔻 نوع العقد: {contract_type_en} / {contract_type_ar}"
    return ""

def extract_date_info(text):
    match = re.search(r'\d{1,2}\s+\w+\s+\d{2,4}', text)
    if match:
        try:
            date_str = match.group()
            dt = datetime.strptime(date_str, "%d %b %y")
            day_name_en = dt.strftime("%A")
            day_name_ar = {
                'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين',
                'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء',
                'Thursday': 'الخميس', 'Friday': 'الجمعة'
            }[day_name_en]
            return f"📆 تاريخها: يوم {day_name_ar} {dt.day} يوليو"
        except:
            pass
    return ""

def extract_strike_price(text):
    patterns = [
        r'\bSPXW[-\s]*?(\d{4,5})[PC]?\b',
        r'\bStrike(?:Price)?[:\s\-]*?(\d{4,5})[PC]?\b',
        r'\bسعر التنفيذ[:\s\-]*?(\d{4,5})[PC]?\b',
        r'\b(\d{4,5})[PC]?\b\s*[–\-—]+\s*\d{1,2}\s+\w+\s+\d{2,4}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

async def rewrite_text_with_chatgpt(text):
    try:
        original = text.strip()

        if original == "القناة لا تتحمل أي مسؤولية":
            return ""

        if original.startswith("فرصة دخول بوت"):
            return REPLACEMENT_TEXT

        if "تم تجهيز قائمة مراقبة لعقود بوت" in original and "لا يتم التنفيذ حتى يتم التنبيه من البوت" in original:
            return """📋 تم تجهيز قائمة العقود بنجاح

🚫 لا تدخل حتى يصدر تنبيه دخول سريع من البوت"""

        if "جاري تجهيز قائمة لمراقبة العقود" in original:
            return """🤖 البوت الذكي يُجهّز قائمة العقود حاليًا…

🚫 لا تدخل حتى يصدر تنبيه دخول"""

        if "تم انشاء مجموعة ريتك" in original and "ما يتم طرحه في هذه القناة" in original:
            return "✨ بسم الله توكلنا على الله ✨🕌\n\nنبدأ باسم الله، ونتوكل عليه في كل أمر"

        if "BOT_TOPSPX1" in original or "بسم الله الرحمن الرحيم" in original:
            return text

        text = text.replace("🔻 النوع: Put", "🔻 النوع: Put / بيع")
        text = text.replace("🔻 النوع: Call", "🔻 النوع: Call / شراء")

        date_info = extract_date_info(text)
        cleaned = clean_text(text)

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "أعد صياغة النص بأسلوب محلل مالي محترف يدير قناة موثوقة على تيليجرام. اجعل الصياغة مقنعة، احترافية، جذابة ومختصرة، مع الحفاظ الكامل على الأرقام والتنسيق كما هي. إذا كان النص يحتوي على أكثر من جملة، اجعل الناتج في جملة واحدة فقط. وإذا كان النص عبارة عن جملة واحدة فقط، فأعد صياغتها بأساليب مختلفة في كل مرة لتفادي التكرار. في كل الحالات، يجب أن تبدأ الجملة برمز تعبيري مناسب يعكس مضمونها ويجعلها بصريًا جذابة."
                },
                {"role": "user", "content": cleaned.strip()}
            ],
            temperature=0.4
        )

        rewritten = response.choices[0].message.content.strip()

        if "📆 تاريخها" not in rewritten:
            rewritten = f"{date_info}\n{rewritten}"

        strike_number = extract_strike_price(text)
        if strike_number:
            rewritten = f"🔵 <b>Strike : {strike_number}</b>\n" + rewritten

        return rewritten.strip()

    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بـ ChatGPT: {e}")
        return text

def add_text_on_image(image_path, text="BOT_TOPSPX1"):
    image = Image.open(image_path).convert("RGBA")
    txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=56)
    except:
        font = ImageFont.load_default()
    x = int(image.width * 0.72)
    y = int(image.height * 0.45)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    combined = Image.alpha_composite(image, txt_layer)
    byte_io = io.BytesIO()
    combined.convert("RGB").save(byte_io, format='PNG')
    byte_io.name = 'watermarked.png'
    byte_io.seek(0)
    return byte_io

@client.on(events.NewMessage(chats=source_channel))
async def forward_handler(event):
    try:
        if not event.text and not event.photo:
            print("⛔ تم تجاهل رسالة غير مدعومة.")
            return

        original_text = event.text or ""

        if re.search(r'https?://\S+', original_text):
            print("⛔ حذف رسالة تحتوي على لينك.")
            return

        if any(forbidden.lower() in original_text.lower() for forbidden in social_media_texts):
            print("⛔ حذف رسالة تحتوي على محتوى محظور.")
            return

        if event.photo:
            file_path = await event.download_media()
            caption = await rewrite_text_with_chatgpt(original_text) if original_text.strip() else ""
            image_stream = add_text_on_image(file_path)
            await client.send_file(destination_channel, image_stream, caption=caption, parse_mode='html')
            await client.send_message(destination_channel, "───  BOT_TOPSPX1  ───")
            os.remove(file_path)
        else:
            modified_caption = await rewrite_text_with_chatgpt(original_text)
            await client.send_message(destination_channel, modified_caption, parse_mode='html')
            await client.send_message(destination_channel, "───  BOT_TOPSPX1  ───")

    except Exception as e:
        print(f"❌ خطأ أثناء التعامل مع الرسالة: {e}")

daily_message = """(بسم الله الرحمن الرحيم)

🤖 نظام إدارة مجموعة BOT_TOPSPX1

تُدار المجموعة بواسطة روبوت ذكي مبني على خوارزميات تحليل متقدمة،
وبإشراف مباشر من سبعة خبراء ماليين محترفين لضمان:
🔹 دقة الأداء
🔹 جودة التوصيات
🔹 اتخاذ القرارات الاستثمارية المثلى

📊 هدفنا: تمكين المتداول من اتخاذ قرارات مبنية على بيانات وتحليل احترافي

⚙ آلية اختيار العقود وتنفيذ الصفقات
اختيار العقد الأنسب يتم عبر تحليل شامل لـ:
    • 📊 حجم السيولة اليومية
    • 🌀 حركة السوق اللحظية (Volatility)
    • 📈 التحليل الفني الدقيق للعقد

قواعد تنفيذ الصفقة:
    • ✅ يتم طرح العقد عند مستوى دخول محسوب مسبقًا بدقة.
    • ⛔ يُمنع الدخول إذا ارتفع السعر أكثر من 20 دولار عن سعر الطرح ومحاولة إسراع في الدخول عند طرح العقد

استراتيجية الخروج من الصفقة:
    • 🎯 هدفنا تحقيق ربح 60 دولار أي 15٪ إلى 20٪ لتضمن الربح وتنمي محفظتك والاستمرار بقرارك، ويتم توضيح إذا هناك فرصة قوية لعقد في ارتفاع واستمرار
    • عند دخولك بأكثر من عقد يُنصح بالخروج إذا تم ربح 15‎% إلى 20‎%‎ من قيمة كل عقد

🎯 نظام المجموعة
    • لا نُكثر من الصفقات. نُركز على:
        - ✔ أقصى ربح ممكن
        - 🛡 أقل خسارة محتملة

📊 نظام تتبع الأداء
نقيس كفاءة الروبوت وفق:
    • 📈 أعلى ربح تم تحقيقه للعقد الواحد
    • 📉 أقصى خسارة مسجلة للعقد الواحد
    • 📆 تقارير أسبوعية وشهرية لأداء المجموعة (ربح / خسارة)

🔔 تنبيه مهم:
الأرقام المعروضة لا تمثل أداء كل متداول بدقة، إذ يختلف الأداء حسب:
    • 🔢 عدد العقود المنفذة
    • ⏱ توقيت الدخول والخروج

⚠ إخلاء مسؤولية ضروري
    • 🎓 هذه المجموعة تُستخدم لأغراض تعليمية فقط عبر الحسابات التجريبية.
    • 🧾 المعلومات المعروضة ليست توصيات.
    • ⚠ التداول يتم على مسؤوليتك الشخصية.

💎 الرسالة الجوهرية

“في عالم التداول، الروبوت هو الخريطة،
لكن القبطان الحقيقي هو قراراتك وانضباطك.”
✨ استثمر في المعرفة، تكن الأرباح حليفك.

⚖ استراتيجية ذكية + انضباط صارم = نجاح مستدام
"""
scheduler = AsyncIOScheduler(timezone="Asia/Riyadh")

@scheduler.scheduled_job('cron', hour=3, minute=0)
async def send_daily_info():
    await client.send_message(destination_channel, daily_message)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ الجلسة غير مصرح بها.")
        return
    print("✅ البوت متصل بـ Telegram")
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
