import logging
import cloudscraper
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

# 1. توكن البوت
BOT_TOKEN = "8999239916:AAGhMetBKM0YFo1YvBynIpeuML-HRIAhyiM"

# 2. يوزر الأدمن الخاص بك
ADMIN_USERNAME = "QOT_YBA"

# متغيّر لحفظ آيدي الأدمن تلقائياً عند دخوله البوت
ADMIN_ID = None

scraper = cloudscraper.create_scraper()

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛡️ توليد نص بلاغ", callback_data="mode_report")],
        [InlineKeyboardButton("🔍 فحص يوزر عبر المنصات", callback_data="mode_check_user")]
    ]
    return InlineKeyboardMarkup(keyboard)

def platforms_menu():
    keyboard = [
        [InlineKeyboardButton("🎵 تيك توك", callback_data="platform_tiktok")],
        [InlineKeyboardButton("📸 انستغرام", callback_data="platform_insta")],
        [InlineKeyboardButton("✈️ تليجرام", callback_data="platform_tg")],
        [InlineKeyboardButton("▶️ يوتيوب", callback_data="platform_yt")],
        [InlineKeyboardButton("❌ تويتر / X", callback_data="platform_x")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def reason_menu(platform):
    keyboard = [
        [InlineKeyboardButton("👤 انتحال شخصية", callback_data=f"reason_{platform}_impersonation")],
        [InlineKeyboardButton("© انتهاك حقوق", callback_data=f"reason_{platform}_copyright")],
        [InlineKeyboardButton("🚫 محتوى ضار / إسيئة", callback_data=f"reason_{platform}_harassment")],
        [InlineKeyboardButton("⚠️ احتيال / سبام", callback_data=f"reason_{platform}_scam")],
        [InlineKeyboardButton("🔙 قائمة المنصات", callback_data="mode_report")]
    ]
    return InlineKeyboardMarkup(keyboard)

REPORTS_TEXT = {
    "impersonation": {
        "ar": "أود الإبلاغ عن هذا الحساب لقيامه بانتحال شخصيتي/جهة رسمية دون إذن، مما يسبب تضليلاً للمستخدمين ويخالف شروط الخدمة. أرجو مراجعة الحساب وإغلاقه.",
        "en": "I am reporting this account for impersonating me/an official entity without authorization. This violates safety guidelines. Please suspend this account."
    },
    "copyright": {
        "ar": "أبلغكم بأن هذا المحتوى ينتهك حقوق الملكية الفكرية الخاصة بي، حيث تم إعادة نشر مقاطعي/تصاميمي دون تصريح. يرجى إزالة المحتوى المخالف.",
        "en": "I am reporting this content for copyright infringement. This account re-uploaded my copyrighted materials without consent. Please remove it."
    },
    "harassment": {
        "ar": "هذا الحساب ينشر محتوى يتضمن مضايقات وتشهير وإساءة موجهة، مما يخالف قواعد المجتمع للسلامة. أطالب بالتأكد وتطبيق العقوبات.",
        "en": "This account is engaging in targeted harassment and defamation, violating community guidelines regarding safety and bullying. Please take action."
    },
    "scam": {
        "ar": "أصرح بأن هذا الحساب يمارس أنشطة احتيالية وتضليلية ونشر روابط وهمية لسرقة البيانات. يرجى حظر الحساب لحماية المستخدمين.",
        "en": "I am reporting this account for fraudulent activity and phishing scams. Please suspend this account to protect users."
    }
}

# --- إشعارات الدخول والخروج للأدمن @QOT_YBA ---
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    result = update.my_chat_member
    if not result:
        return

    user = result.from_user
    new_status = result.new_chat_member.status
    old_status = result.old_chat_member.status

    if ADMIN_ID is None:
        return

    # دخول مستخدم جديد
    if old_status in ["kicked", "left"] and new_status in ["member"]:
        msg = (
            f"📥 **مستخدم جديد دخل البوت!**\n\n"
            f"👤 **الاسم:** {user.full_name}\n"
            f"🆔 **الآيدي:** `{user.id}`\n"
            f"🔗 **اليوزر:** @{user.username if user.username else 'بدون يوزر'}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
        except Exception:
            pass

    # خروج أو حظر مستخدم للبوت
    elif old_status in ["member"] and new_status in ["kicked", "left"]:
        msg = (
            f"📤 **مستخدم قام بحظر/خروج البوت!**\n\n"
            f"👤 **الاسم:** {user.full_name}\n"
            f"🆔 **الآيدي:** `{user.id}`\n"
            f"🔗 **اليوزر:** @{user.username if user.username else 'بدون يوزر'}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
        except Exception:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    user = update.effective_user
    
    # حفظ آيدي الأدمن عند تفاعله مع البوت عبر اليوزر @QOT_YBA
    if user.username and user.username.lower() == ADMIN_USERNAME.lower():
        ADMIN_ID = user.id

    await update.message.reply_text(
        "أهلاً بك في **صانع البلاغات وفاحص الحسابات الاحترافي** 🛡️🔍\n\n"
        "اختر الخدمة التي تريدها من القائمة أدناه:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def check_username_all(username: str) -> str:
    platforms = {
        "تليجرام (Telegram)": f"https://t.me/{username}",
        "انستغرام (Instagram)": f"https://www.instagram.com/{username}/",
        "تيك توك (TikTok)": f"https://www.tiktok.com/@{username}",
        "يوتيوب (YouTube)": f"https://www.youtube.com/@{username}",
        "تويتر / X": f"https://x.com/{username}"
    }

    result_text = f"🔎 **نتائج البحث عن اليوزر:** `@{username}`\n━━━━━━━━━━━━━━━━━━━━\n\n"

    for name, url in platforms.items():
        try:
            res = scraper.get(url, timeout=5)
            if res.status_code == 200:
                result_text += f"✅ **{name}**: [موجود بالفعل]({url})\n"
            else:
                result_text += f"❌ **{name}**: لا يوجد حساب بهذه المنصة\n"
        except Exception:
            result_text += f"❌ **{name}**: لا يوجد حساب بهذه المنصة\n"

    result_text += "\n💡 *اضغط على رابط المنصة المتاحة للانتقال للحساب مباشرة.*"
    return result_text

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state = context.user_data.get("state")

    if user_state == "waiting_for_username":
        raw_text = update.message.text.strip().replace("@", "")
        msg = await update.message.reply_text("🔄 جاري فحص جميع المنصات، يرجى الانتظار ثوانٍ...")

        report = await check_username_all(raw_text)
        context.user_data["state"] = None

        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_main")]]
        await msg.edit_text(report, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("يرجى اختيار أحد الخيارات من القائمة عبر الضغط على /start")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_main":
        context.user_data["state"] = None
        await query.edit_message_text(
            "أهلاً بك في **صانع البلاغات وفاحص الحسابات الاحترافي** 🛡️🔍\n\n"
            "اختر الخدمة التي تريدها من القائمة أدناه:",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    elif data == "mode_report":
        await query.edit_message_text(
            "اختر المنصة التي تريد تقديم بلاغ ضد حساب أو قناة فيها:",
            reply_markup=platforms_menu()
        )
    elif data == "mode_check_user":
        context.user_data["state"] = "waiting_for_username"
        await query.edit_message_text(
            "🔍 **خدمة فحص اليوزرات:**\n\n"
            "أرسل لي الآن اسم المستخدم (اليوزر) فقط دون أية إضافات، مثال:\n`qutaiba` أو `@qutaiba`",
            parse_mode="Markdown"
        )
    elif data.startswith("platform_"):
        platform_name = data.split("_")[1].upper()
        await query.edit_message_text(
            f"منصة: **{platform_name}** 🎯\nاختر نوع البلاغ والمخالفة:",
            parse_mode="Markdown",
            reply_markup=reason_menu(platform_name)
        )
    elif data.startswith("reason_"):
        parts = data.split("_")
        platform = parts[1]
        reason_key = parts[2]

        report = REPORTS_TEXT.get(reason_key, {})
        text_ar = report.get("ar", "")
        text_en = report.get("en", "")

        response_msg = (
            f"📋 **صيغة بلاغ جاهزة لمنصة [{platform}]**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇸🇦 **[النص بالعربية]**:\n`{text_ar}`\n\n"
            f"🇬🇧 **[English Text]**:\n`{text_en}`\n\n"
            f"💡 *ملاحظة: يمكنك الضغط على النص لنسخه مباشرة.*"
        )

        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_main")]]
        await query.edit_message_text(response_msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

    print("🚀 البوت شغال الآن...")
    app.run_polling()
