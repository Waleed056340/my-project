import openai
from telethon import TelegramClient, events
from PIL import Image
import os
import asyncio
import re
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
openai.api_key = os.getenv("OPENAI_API_KEY")


#openai.api_key = "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"

api_id =  25671729

api_hash = '7a99f52526cd483c1d5abf27069d5e10'

source_channel = 'https://t.me/OPTION_Xn'
destination_channel = 'https://t.me/BOT_TOPSPX1'

client = TelegramClient('forwarder_session', api_id, api_hash)

def clean_text(text):
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
        if "BOT_TOPSPX1" in text or "بسم الله الرحمن الرحيم" in text:
            return text

        text = text.replace("🔻 النوع: Put", "🔻 النوع: Put / بيع")
        text = text.replace("🔻 النوع: Call", "🔻 النوع: Call / شراء")
        has_opton = "OPTON\u00a0X" in text
        text = text.replace("OPTON\u00a0X", "").replace("🔥", "").strip()
        date_info = extract_date_info(text)
        cleaned = clean_text(text)
        cleaned = re.sub(r'🔻 نوع الصفقة:.*', '', cleaned)
        cleaned = re.sub(r'🔻 نوع العقد:.*', '', cleaned)
        cleaned = re.sub(r'(📆)?\s*تاريخ الصفقة:.*', '', cleaned)
        cleaned = re.sub(r'(📆)?\s*تاريخها:.*', '', cleaned)
        cleaned = re.sub(r'(📆)?\s*التاريخ:.*', '', cleaned)
        cleaned = re.sub(r'⚠ تذكر:.*', '', cleaned)
        cleaned = re.sub(r'⚠ تنبيه:.*?(⸻)?', '', cleaned, flags=re.DOTALL)
        cleaned = cleaned.replace("⸻", "")

        if "الهدف الثاني" in cleaned:
            cleaned = re.split(r"• الهدف الثاني:.*", cleaned)[0].strip()
            cleaned += "\n• الهدف الثاني: يتم تنويه عنه لاحقًا\nBOT_TOPSPX1"

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
            strike_line = f"🔵 <b>Strike : {strike_number}</b>\n"
            rewritten = strike_line + rewritten

        final_text = rewritten.strip()
        return final_text

    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بـ ChatGPT: {e}")
        return text

def add_image_watermark(base_image_path, watermark_image_path, output_path, opacity=135):
    base_image = Image.open(base_image_path).convert("RGBA")
    watermark = Image.open(watermark_image_path).convert("RGBA")
    scale_factor = 0.75
    new_size = (int(base_image.width * scale_factor), int(base_image.height * scale_factor))
    watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
    alpha = watermark.getchannel("A")
    alpha = alpha.point(lambda p: int(p * (opacity / 255)))
    watermark.putalpha(alpha)
    x = (base_image.width - watermark.width) // 2
    y = (base_image.height - watermark.height) // 2
    transparent_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    transparent_layer.paste(watermark, (x, y), watermark)
    combined = Image.alpha_composite(base_image, transparent_layer)
    combined.convert("RGB").save(output_path, "JPEG")

@client.on(events.NewMessage(chats=source_channel))
async def forward_handler(event):
    try:
        # تجاهل الرسائل غير المدعومة
        if not event.text and not event.photo:
            print("⛔ تم تجاهل رسالة غير مدعومة (ليست نصًا أو صورة).")
            return

        original_text = event.text or ""

        if event.photo:
            file_path = await event.download_media()
            output_path = "watermarked.jpg"
            watermark_path = "watermark.png"
            caption = await rewrite_text_with_chatgpt(original_text) if original_text.strip() else ""
            add_image_watermark(file_path, watermark_path, output_path)
            await client.send_file(destination_channel, output_path, caption=caption, parse_mode='html')
            await client.send_message(destination_channel, "───  BOT_TOPSPX1  ───")
            os.remove(file_path)
            os.remove(output_path)
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
(بسم الله الرحمن الرحيم)

⚙ آلية اختيار العقود وتنفيذ الصفقات
اختيار العقد الأنسب يتم عبر تحليل شامل لـ:
    • 📊 حجم السيولة اليومية
    • 🌀 حركة السوق اللحظية (Volatility)
    • 📈 التحليل الفني الدقيق للعقد

قواعد تنفيذ الصفقة:
    • ✅ يتم طرح العقد عند مستوى دخول محسوب مسبقًا بدقة.
    • ⛔ يُمنع الدخول إذا ارتفع السعر أكثر من 20 دولار عن سعر الطرح ومحاولة إسراع في الدخول عند طرح العقد
    • 🛑 يتم تحديد مستوى وقف الخسارة بوضوح على الشارت قبل أي تنفيذ.

استراتيجية الخروج:
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
"""

scheduler = AsyncIOScheduler(timezone="Asia/Riyadh")

@scheduler.scheduled_job('cron', hour=3, minute=00)
async def send_daily_info():
    await client.send_message(destination_channel, daily_message)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ الجلسة غير مصرح بها. قم بتسجيل الدخول يدويًا أولاً.")
        return
    print("✅ البوت متصل بـ Telegram")
    scheduler.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
