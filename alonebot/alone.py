
import asyncio
import logging
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BotCommand,
    ReplyKeyboardRemove,
)

# === SOZLAMALAR ===
TOKEN = "8692469958:AAH75IR4Wvo1fF4zxD1eH5P013KF72Y0cLY"
ADMIN_ID = 6650430442
ADMIN_PASSWORD = "alone"
CARD_NUMBER = "8600 1402 3999 1731"
CARD_HOLDER = "N.m"
MIN_TOPUP = 5000

# === STIKERLAR ===
STICKERS = {
    "main": "CAACAgIAAxkBAAER9fBqupiGfIbVkhas-99iIh30slYiFwAClmQAAoBKwEoF-PhllH7s0z0E",
    "topup": "CAACAgEAAxkBAAER9fRquplZXvIClUoY0Y-Q4Fcy2eUYrgACAwMAAoOo4EQ3ZTysFsteinT0E",
    "buy": "CAACAgEAAxkBAAER9fZqupmLvTzj6U3nF7XD_Nd_TIdzlAACTAUAAmT_sEfz8RU-1D-ilT0E",
    "profile": "CAACAgIAAxkBAAER9fhqupnu08NKiRCp9GUnQ-ybm7N-hwACyUoAAi7LQEvGM2FguGcKTT0E",
    "admin": "CAACAgIAAxkBAAER9fxquppgM0xdB3qFoeZcfXLiWcV0xwAC9wADVp29CgtyJB1I9A0wPQQ",
}

logging.basicConfig(level=logging.INFO)
router = Router()
bot_start_time = time.time()


# ==================== TILLAR ====================
TEXTS = {
    "uz": {
        "lang_name": "🇺🇿 O'zbekcha",
        "choose_lang": "🌐 **TILNI TANLANG**\n━━━━━━━━━━━━━━━━━━━━\n\nIltimos, o'zingizga qulay tilni tanlang:",
        "lang_changed": "✅ Til muvaffaqiyatli o'zgartirildi: **O'zbekcha**",
        "main_title": "✨ **ALONE PUBG SHOP** ✨",
        "main_hello": "👋 Salom, **{name}**! 💎",
        "main_desc": "🔥 **PUBG Mobile** va boshqa o'yin akkauntlari rasmiy do'koni.",
        "main_choose": "⚡️ Kerakli bo'limni tanlang va xarid qilishni boshlang!",
        "btn_shop": "🛍 Do'konni ochish",
        "btn_profile": "👤 Profil kabineti",
        "btn_topup": "💳 Balansni to'ldirish",
        "btn_about": "ℹ️ Bot haqida",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_admin": "⚙️ Admin boshqaruv paneli",
        "btn_back": "⬅️ Orqaga",
        "btn_cancel": "❌ Bekor qilish",
        "about_title": "ℹ️ **BOT HAQIDA**",
        "about_random_msg": "🔥 **SIZ BU YERDA RANDOM AKKOUNTLAR SOTIB OLISHINGIZ MUMKIN** 🔥",
        "about_services": "🛒 **Xizmatlar:**",
        "about_s1": "• 🎮 PUBG Mobile random akkauntlar",
        "about_s3": "• 🎁 Promokodlar va bonuslar",
        "about_trust": "👑 **Ishonchli do'kon:**",
        "about_t1": "• ✅ Tez yetkazib berish",
        "about_t2": "• ✅ Xavfsiz to'lov",
        "about_t3": "• ✅ 24/7 qo'llab-quvvatlash",
        "about_contact": "📞 **Admin bilan bog'lanish:** @samir_admin",
        "shop_title": "🛍 **DO'KON** ⚡️",
        "shop_empty": "😔 Hozircha sotuvda lotlar mavjud emas.\nTez orada yangilari qo'shiladi! 🔥",
        "shop_available": "🟢 Mavjud lotlar: **{count} ta**",
        "shop_choose": "Kerakli lotni tanlang:",
        "lot_in_stock": "📦 Mavjud: **{stock} ta**",
        "lot_sold_out_msg": "😔 **Bu lot to'liq sotildi!**\n\nAdmin tez orada yangi akkauntlar qo'shadi.",
        "lot_buy_title": "🎉 **XARID MUVAFFAQIYATLI!** 👑",
        "lot_buy_name": "🏷 Lot:",
        "lot_buy_price": "💰 Narxi:",
        "lot_buy_stock_left": "📦 Qolgan:",
        "lot_your_credentials": "🔑 **SIZNING MA'LUMOTLARINGIZ:**",
        "lot_credentials_note": "⚠️ *Bu ma'lumotlar faqat sizga tegishli. Hech kimga bermang!*",
        "lot_sold_out_admin": "🔴 **LOT TUGADI!**",
        "profile_title": "👤 **SHAXSIY KABINET** 💎",
        "profile_id": "🆔 Telegram ID:",
        "profile_code": "🔖 Sizning kodingiz:",
        "profile_reg": "📅 Ro'yxatdan o'tgan:",
        "profile_balance": "💰 **Balans:**",
        "profile_spent": "💸 **Sarflangan:**",
        "profile_security": "⚡️ Xavfsizlik: Yuqori 🔒",
        "btn_enter_promo": "🎁 Promokod kiritish",
        "promo_title": "🎁 **PROMOKOD KIRITISH**",
        "promo_hint": "Iltimos, promokodni yuboring:",
        "promo_note": "📌 *Promokod katta-kichik harflarga sezgir emas*",
        "promo_not_found": "❌ **Promokod topilmadi!**\n\nBunday promokod mavjud emas yoki eskirgan.",
        "promo_limit_out": "⚠️ **Promokod limiti tugagan!**\n\nBu promokod allaqachon o'z limitiga yetgan.",
        "promo_used": "⚠️ **Siz bu promokoddan allaqachon foydalangansiz!**",
        "promo_activated": "🎉 **PROMOKOD FAOLLASHTIRILDI!**",
        "promo_code_label": "🎁 Promokod:",
        "promo_bonus": "💰 Bonus:",
        "promo_new_balance": "💎 Yangi balansingiz:",
        "btn_to_profile": "👤 Profilga qaytish",
        "topup_title": "💳 **HISOBNI TO'LDIRISH** ⚡️",
        "topup_desc": "To'ldirmoqchi bo'lgan summani tanlang:",
        "topup_min": "💡 *Minimal: 5 000 so'm*",
        "btn_other_amount": "✍️ Boshqa summa",
        "custom_amount_title": "✍️ **SUMMANI KIRITING**",
        "custom_amount_desc": "O'zingiz xohlagan summani raqamlarda kiriting:",
        "custom_amount_example": "📌 *Misol: 5000*",
        "card_title": "💳 **TO'LOV MA'LUMOTLARI** ⚠️",
        "card_amount": "💰 Tanlangan summa:",
        "card_pay": "📌 Quyidagi kartaga to'lov qiling:",
        "card_number": "💳 Karta:",
        "card_holder": "👤 Egasi:",
        "card_attention": "🚨 **DIQQAT!**",
        "card_warn1": "• To'lovni **aniq** tanlangan summada qiling",
        "card_warn2": "• Kam to'lov qilsangiz — pul qaytarilmaydi!",
        "card_send_receipt": "📸 To'lovdan so'ng **chek (skrinshot)** ni shu botga yuboring!",
        "receipt_sent": "✅ **CHEKINGIZ YUBORILDI!**",
        "receipt_code": "🔖 Sizning kodingiz:",
        "receipt_wait": "⏳ Admin tez orada tekshiradi va balansingizni to'ldiradi.",
        "balance_added": "✅ **BALANS TO'LDIRILDI!** 🎉",
        "balance_added_amount": "💰 Qo'shildi:",
        "balance_new": "💎 Yangi balans:",
        "receipt_rejected": "❌ **To'lov rad etildi!**\n\nSabab: Soxta chek yoki summa noto'g'ri.\nSavollar uchun adminga murojaat qiling.",
        "not_enough": "❌ Mablag' yetarli emas!",
        "your_balance": "Sizda:",
        "price": "Narxi:",
        "only_number": "❌ Faqat raqam kiriting! Qaytadan urinib ko'ring:",
        "min_sum": "❌ Minimal summa: **5 000 so'm**. Qaytadan kiriting:",
        "already_sold": "⚠️ Bu allaqachon sotilgan!",
        "buy_success": "✅ Xarid muvaffaqiyatli!",
        "admin_pass_title": "🔐 **ADMIN PANEL** 🛡",
        "admin_pass_desc": "Xavfsizlik uchun maxfiy parolni kiriting:",
        "admin_pass_note": "🔒 *Parol maxfiy saqlanadi*",
        "admin_pass_wrong": "❌ **Xato parol!** Qaytadan urinib ko'ring.",
        "admin_welcome": "🔒 **PAROL TASDIQLANDI** ✅\n\nXush kelibsiz, **Admin**! 👑",
        "admin_stats": "📊 **STATISTIKA**",
        "admin_users_count": "👥 Foydalanuvchilar:",
        "admin_lots": "📦 Lotlar:",
        "admin_total_bal": "💰 Umumiy balans:",
        "admin_total_sales": "💵 Umumiy sotuv:",
        "admin_total_topups": "💳 To'ldirishlar:",
        "admin_uptime": "⏱ Uptime:",
        "admin_not_admin": "⛔️ Siz admin emassiz!",
        "msg_from_admin": "📦 **Admin xabari:** 🔔",
        "balance_changed": "🎁 **BALANS O'ZGARDI!**",
        "balance_change": "O'zgarish:",
        "balance_current": "💰 Joriy balans:",
        "no_users": "👥 Hozircha foydalanuvchilar yo'q.",
        "no_lots": "⚠️ Lotlar yo'q.",
        "new_lot_order": "🛒 **YANGI LOT SOTIB OLINDI!** 🔔",
        "buyer": "👤 Xaridor:",
        "username_label": "🔗 Username:",
        "id_label": "🆔 ID:",
        "code_label": "🔖 KODI:",
        "lot_label": "📦 Lot:",
        "price_label": "💰 Narxi:",
        "send_login_hint": "⚠️ **LOGIN VA PAROLNI YUBORING:**",
        "new_receipt": "📥 **YANGI TO'LOV CHEKI!** 🔔",
        "sum_label": "💰 Summa:",
        "approved": "✅ **TASDIQLANDI**",
        "rejected": "❌ **RAD ETILDI**",
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "choose_lang": "🌐 **ВЫБЕРИТЕ ЯЗЫК**\n━━━━━━━━━━━━━━━━━━━━\n\nПожалуйста, выберите удобный язык:",
        "lang_changed": "✅ Язык успешно изменён: **Русский**",
        "main_title": "✨ **ALONE PUBG SHOP** ✨",
        "main_hello": "👋 Привет, **{name}**! 💎",
        "main_desc": "🔥 Официальный магазин **PUBG Mobile** аккаунтов.",
        "main_choose": "⚡️ Выберите нужный раздел и начните покупки!",
        "btn_shop": "🛍 Открыть магазин",
        "btn_profile": "👤 Профиль",
        "btn_topup": "💳 Пополнить баланс",
        "btn_about": "ℹ️ О боте",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_admin": "⚙️ Админ панель",
        "btn_back": "⬅️ Назад",
        "btn_cancel": "❌ Отмена",
        "about_title": "ℹ️ **О БОТЕ**",
        "about_random_msg": "🔥 **ЗДЕСЬ ВЫ МОЖЕТЕ КУПИТЬ RANDOM АККАУНТЫ** 🔥",
        "about_services": "🛒 **Услуги:**",
        "about_s1": "• 🎮 PUBG Mobile random аккаунты",
        "about_s3": "• 🎁 Промокоды и бонусы",
        "about_trust": "👑 **Надёжный магазин:**",
        "about_t1": "• ✅ Быстрая доставка",
        "about_t2": "• ✅ Безопасная оплата",
        "about_t3": "• ✅ Поддержка 24/7",
        "about_contact": "📞 **Связь с админом:** @samir_admin",
        "shop_title": "🛍 **МАГАЗИН** ⚡️",
        "shop_empty": "😔 Пока нет доступных лотов.\nСкоро добавятся новые! 🔥",
        "shop_available": "🟢 Доступные лоты: **{count} шт**",
        "shop_choose": "Выберите нужный лот:",
        "lot_in_stock": "📦 В наличии: **{stock} шт**",
        "lot_sold_out_msg": "😔 **Этот лот полностью продан!**\n\nАдмин скоро добавит новые аккаунты.",
        "lot_buy_title": "🎉 **ПОКУПКА УСПЕШНА!** 👑",
        "lot_buy_name": "🏷 Лот:",
        "lot_buy_price": "💰 Цена:",
        "lot_buy_stock_left": "📦 Осталось:",
        "lot_your_credentials": "🔑 **ВАШИ ДАННЫЕ:**",
        "lot_credentials_note": "⚠️ *Эти данные только для вас. Никому не передавайте!*",
        "lot_sold_out_admin": "🔴 **ЛОТ ЗАКОНЧИЛСЯ!**",
        "profile_title": "👤 **ЛИЧНЫЙ КАБИНЕТ** 💎",
        "profile_id": "🆔 Telegram ID:",
        "profile_code": "🔖 Ваш код:",
        "profile_reg": "📅 Регистрация:",
        "profile_balance": "💰 **Баланс:**",
        "profile_spent": "💸 **Потрачено:**",
        "profile_security": "⚡️ Безопасность: Высокая 🔒",
        "btn_enter_promo": "🎁 Ввести промокод",
        "promo_title": "🎁 **ВВЕДИТЕ ПРОМОКОД**",
        "promo_hint": "Пожалуйста, отправьте промокод:",
        "promo_note": "📌 *Промокод не чувствителен к регистру*",
        "promo_not_found": "❌ **Промокод не найден!**\n\nТакого промокода нет или он устарел.",
        "promo_limit_out": "⚠️ **Лимит промокода исчерпан!**\n\nЭтот промокод уже достиг лимита.",
        "promo_used": "⚠️ **Вы уже использовали этот промокод!**",
        "promo_activated": "🎉 **ПРОМОКОД АКТИВИРОВАН!**",
        "promo_code_label": "🎁 Промокод:",
        "promo_bonus": "💰 Бонус:",
        "promo_new_balance": "💎 Ваш новый баланс:",
        "btn_to_profile": "👤 Вернуться в профиль",
        "topup_title": "💳 **ПОПОЛНЕНИЕ БАЛАНСА** ⚡️",
        "topup_desc": "Выберите сумму пополнения:",
        "topup_min": "💡 *Минимум: 5 000 сум*",
        "btn_other_amount": "✍️ Другая сумма",
        "custom_amount_title": "✍️ **ВВЕДИТЕ СУММУ**",
        "custom_amount_desc": "Введите желаемую сумму цифрами:",
        "custom_amount_example": "📌 *Пример: 5000*",
        "card_title": "💳 **ПЛАТЁЖНЫЕ ДАННЫЕ** ⚠️",
        "card_amount": "💰 Выбранная сумма:",
        "card_pay": "📌 Оплатите на карту ниже:",
        "card_number": "💳 Карта:",
        "card_holder": "👤 Владелец:",
        "card_attention": "🚨 **ВНИМАНИЕ!**",
        "card_warn1": "• Оплатите **точную** сумму",
        "card_warn2": "• При недоплате — деньги не возвращаются!",
        "card_send_receipt": "📸 После оплаты отправьте **чек (скриншот)** в бот!",
        "receipt_sent": "✅ **ЧЕК ОТПРАВЛЕН!**",
        "receipt_code": "🔖 Ваш код:",
        "receipt_wait": "⏳ Админ скоро проверит и пополнит баланс.",
        "balance_added": "✅ **БАЛАНС ПОПОЛНЕН!** 🎉",
        "balance_added_amount": "💰 Добавлено:",
        "balance_new": "💎 Новый баланс:",
        "receipt_rejected": "❌ **Платёж отклонён!**\n\nПричина: Фейковый чек или неверная сумма.\nСвяжитесь с админом.",
        "not_enough": "❌ Недостаточно средств!",
        "your_balance": "У вас:",
        "price": "Цена:",
        "only_number": "❌ Только цифры! Попробуйте ещё раз:",
        "min_sum": "❌ Минимум: **5 000 сум**. Введите снова:",
        "already_sold": "⚠️ Уже продано!",
        "buy_success": "✅ Покупка успешна!",
        "admin_pass_title": "🔐 **АДМИН ПАНЕЛЬ** 🛡",
        "admin_pass_desc": "Введите секретный пароль:",
        "admin_pass_note": "🔒 *Пароль хранится в секрете*",
        "admin_pass_wrong": "❌ **Неверный пароль!** Попробуйте снова.",
        "admin_welcome": "🔒 **ПАРОЛЬ ПОДТВЕРЖДЁН** ✅\n\nДобро пожаловать, **Admin**! 👑",
        "admin_stats": "📊 **СТАТИСТИКА**",
        "admin_users_count": "👥 Пользователи:",
        "admin_lots": "📦 Лоты:",
        "admin_total_bal": "💰 Общий баланс:",
        "admin_total_sales": "💵 Общие продажи:",
        "admin_total_topups": "💳 Пополнения:",
        "admin_uptime": "⏱ Uptime:",
        "admin_not_admin": "⛔️ Вы не админ!",
        "msg_from_admin": "📦 **Сообщение от админа:** 🔔",
        "balance_changed": "🎁 **БАЛАНС ИЗМЕНЁН!**",
        "balance_change": "Изменение:",
        "balance_current": "💰 Текущий баланс:",
        "no_users": "👥 Пока нет пользователей.",
        "no_lots": "⚠️ Нет лотов.",
        "new_lot_order": "🛒 **НОВЫЙ ЛОТ КУПЛЕН!** 🔔",
        "buyer": "👤 Покупатель:",
        "username_label": "🔗 Username:",
        "id_label": "🆔 ID:",
        "code_label": "🔖 КОД:",
        "lot_label": "📦 Лот:",
        "price_label": "💰 Цена:",
        "send_login_hint": "⚠️ **ОТПРАВЬТЕ ЛОГИН И ПАРОЛЬ:**",
        "new_receipt": "📥 **НОВЫЙ ЧЕК!** 🔔",
        "sum_label": "💰 Сумма:",
        "approved": "✅ **ПОДТВЕРЖДЕНО**",
        "rejected": "❌ **ОТКЛОНЕНО**",
    },
    "en": {
        "lang_name": "🇬🇧 English",
        "choose_lang": "🌐 **CHOOSE LANGUAGE**\n━━━━━━━━━━━━━━━━━━━━\n\nPlease select your preferred language:",
        "lang_changed": "✅ Language changed successfully: **English**",
        "main_title": "✨ **ALONE PUBG SHOP** ✨",
        "main_hello": "👋 Hello, **{name}**! 💎",
        "main_desc": "🔥 Official shop of **PUBG Mobile** accounts.",
        "main_choose": "⚡️ Choose a section and start shopping!",
        "btn_shop": "🛍 Open Shop",
        "btn_profile": "👤 Profile",
        "btn_topup": "💳 Top Up Balance",
        "btn_about": "ℹ️ About Bot",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_admin": "⚙️ Admin Panel",
        "btn_back": "⬅️ Back",
        "btn_cancel": "❌ Cancel",
        "about_title": "ℹ️ **ABOUT BOT**",
        "about_random_msg": "🔥 **HERE YOU CAN BUY RANDOM ACCOUNTS** 🔥",
        "about_services": "🛒 **Services:**",
        "about_s1": "• 🎮 PUBG Mobile random accounts",
        "about_s3": "• 🎁 Promo codes and bonuses",
        "about_trust": "👑 **Trusted Shop:**",
        "about_t1": "• ✅ Fast delivery",
        "about_t2": "• ✅ Safe payment",
        "about_t3": "• ✅ 24/7 Support",
        "about_contact": "📞 **Contact Admin:** @samir_admin",
        "shop_title": "🛍 **SHOP** ⚡️",
        "shop_empty": "😔 No lots available yet.\nNew ones coming soon! 🔥",
        "shop_available": "🟢 Available lots: **{count}**",
        "shop_choose": "Choose the lot:",
        "lot_in_stock": "📦 In stock: **{stock}**",
        "lot_sold_out_msg": "😔 **This lot is fully sold out!**\n\nAdmin will add new accounts soon.",
        "lot_buy_title": "🎉 **PURCHASE SUCCESSFUL!** 👑",
        "lot_buy_name": "🏷 Lot:",
        "lot_buy_price": "💰 Price:",
        "lot_buy_stock_left": "📦 Left:",
        "lot_your_credentials": "🔑 **YOUR CREDENTIALS:**",
        "lot_credentials_note": "⚠️ *These credentials belong only to you. Don't share them!*",
        "lot_sold_out_admin": "🔴 **LOT SOLD OUT!**",
        "profile_title": "👤 **PROFILE** 💎",
        "profile_id": "🆔 Telegram ID:",
        "profile_code": "🔖 Your code:",
        "profile_reg": "📅 Registered:",
        "profile_balance": "💰 **Balance:**",
        "profile_spent": "💸 **Spent:**",
        "profile_security": "⚡️ Security: High 🔒",
        "btn_enter_promo": "🎁 Enter Promo Code",
        "promo_title": "🎁 **ENTER PROMO CODE**",
        "promo_hint": "Please send the promo code:",
        "promo_note": "📌 *Promo code is case-insensitive*",
        "promo_not_found": "❌ **Promo code not found!**\n\nInvalid or expired code.",
        "promo_limit_out": "⚠️ **Promo limit reached!**\n\nThis promo code has reached its limit.",
        "promo_used": "⚠️ **You already used this promo!**",
        "promo_activated": "🎉 **PROMO ACTIVATED!**",
        "promo_code_label": "🎁 Promo:",
        "promo_bonus": "💰 Bonus:",
        "promo_new_balance": "💎 Your new balance:",
        "btn_to_profile": "👤 Back to Profile",
        "topup_title": "💳 **TOP UP BALANCE** ⚡️",
        "topup_desc": "Choose top-up amount:",
        "topup_min": "💡 *Minimum: 5 000 so'm*",
        "btn_other_amount": "✍️ Other amount",
        "custom_amount_title": "✍️ **ENTER AMOUNT**",
        "custom_amount_desc": "Enter the desired amount in digits:",
        "custom_amount_example": "📌 *Example: 5000*",
        "card_title": "💳 **PAYMENT DETAILS** ⚠️",
        "card_amount": "💰 Selected amount:",
        "card_pay": "📌 Pay to the card below:",
        "card_number": "💳 Card:",
        "card_holder": "👤 Holder:",
        "card_attention": "🚨 **ATTENTION!**",
        "card_warn1": "• Pay the **exact** amount",
        "card_warn2": "• Underpayment — no refund!",
        "card_send_receipt": "📸 After payment, send the **receipt (screenshot)** to the bot!",
        "receipt_sent": "✅ **RECEIPT SENT!**",
        "receipt_code": "🔖 Your code:",
        "receipt_wait": "⏳ Admin will verify and top up your balance.",
        "balance_added": "✅ **BALANCE TOPPED UP!** 🎉",
        "balance_added_amount": "💰 Added:",
        "balance_new": "💎 New balance:",
        "receipt_rejected": "❌ **Payment rejected!**\n\nReason: Fake receipt or wrong amount.\nContact admin.",
        "not_enough": "❌ Not enough funds!",
        "your_balance": "You have:",
        "price": "Price:",
        "only_number": "❌ Numbers only! Try again:",
        "min_sum": "❌ Minimum: **5 000 so'm**. Try again:",
        "already_sold": "⚠️ Already sold!",
        "buy_success": "✅ Purchase successful!",
        "admin_pass_title": "🔐 **ADMIN PANEL** 🛡",
        "admin_pass_desc": "Enter secret password:",
        "admin_pass_note": "🔒 *Password is kept secret*",
        "admin_pass_wrong": "❌ **Wrong password!** Try again.",
        "admin_welcome": "🔒 **PASSWORD CONFIRMED** ✅\n\nWelcome, **Admin**! 👑",
        "admin_stats": "📊 **STATISTICS**",
        "admin_users_count": "👥 Users:",
        "admin_lots": "📦 Lots:",
        "admin_total_bal": "💰 Total balance:",
        "admin_total_sales": "💵 Total sales:",
        "admin_total_topups": "💳 Top-ups:",
        "admin_uptime": "⏱ Uptime:",
        "admin_not_admin": "⛔️ You're not admin!",
        "msg_from_admin": "📦 **Message from admin:** 🔔",
        "balance_changed": "🎁 **BALANCE CHANGED!**",
        "balance_change": "Change:",
        "balance_current": "💰 Current balance:",
        "no_users": "👥 No users yet.",
        "no_lots": "⚠️ No lots.",
        "new_lot_order": "🛒 **NEW LOT PURCHASED!** 🔔",
        "buyer": "👤 Buyer:",
        "username_label": "🔗 Username:",
        "id_label": "🆔 ID:",
        "code_label": "🔖 CODE:",
        "lot_label": "📦 Lot:",
        "price_label": "💰 Price:",
        "send_login_hint": "⚠️ **SEND LOGIN AND PASSWORD:**",
        "new_receipt": "📥 **NEW RECEIPT!** 🔔",
        "sum_label": "💰 Amount:",
        "approved": "✅ **APPROVED**",
        "rejected": "❌ **REJECTED**",
    },
}


# ==================== FSM HOLATLARI ====================
class AdminStates(StatesGroup):
    waiting_for_password = State()
    adding_lot_name = State()
    adding_lot_game = State()
    adding_lot_price = State()
    adding_lot_desc = State()
    adding_credentials_to_lot = State()
    waiting_for_promo_code = State()
    waiting_for_promo_amount = State()
    waiting_for_promo_limit = State()
    waiting_for_broadcast = State()


class BuyStates(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_receipt = State()


class UserStates(StatesGroup):
    waiting_for_activate_promo = State()


# ==================== MA'LUMOTLAR BAZASI ====================
database = {
    "lots": {},
    "users": {},
    "promos": {},
    "klent_counter": 0,
    "total_topups": 0,
    "total_sales": 0,
}


# ==================== YORDAMCHI FUNKSIYALAR ====================
def get_lang(user_id):
    user = database["users"].get(user_id)
    if user and "lang" in user:
        return user["lang"]
    return "uz"


def t(user_id, key, **kwargs):
    lang = get_lang(user_id)
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


async def safe_edit(message, text, kb=None, parse_mode="Markdown"):
    markup = InlineKeyboardMarkup(inline_keyboard=kb) if kb else None
    try:
        if message.photo:
            await message.edit_caption(caption=text, reply_markup=markup, parse_mode=parse_mode)
        elif message.text:
            await message.edit_text(text=text, reply_markup=markup, parse_mode=parse_mode)
        else:
            await message.edit_reply_markup(reply_markup=markup)
    except Exception:
        try:
            await message.answer(text, reply_markup=markup, parse_mode=parse_mode)
        except Exception:
            pass


def format_money(amount):
    return f"{amount:,}".replace(",", " ")


def get_lot_stock(lot):
    return sum(1 for c in lot["credentials"] if not c["sold"])


def get_available_credential(lot):
    for c in lot["credentials"]:
        if not c["sold"]:
            return c
    return None


def main_menu(user_id):
    kb = [
        [InlineKeyboardButton(text=t(user_id, "btn_shop"), callback_data="shop_list")],
        [
            InlineKeyboardButton(text=t(user_id, "btn_profile"), callback_data="profile"),
            InlineKeyboardButton(text=t(user_id, "btn_topup"), callback_data="top_up"),
        ],
        [
            InlineKeyboardButton(text=t(user_id, "btn_about"), callback_data="about_bot"),
            InlineKeyboardButton(text=t(user_id, "btn_lang"), callback_data="choose_lang"),
        ],
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text=t(user_id, "btn_admin"), callback_data="admin_panel")])
    return kb


def back_button(user_id, callback_data="back_to_main"):
    return [[InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data=callback_data)]]


def cancel_button(user_id, callback_data="back_to_main"):
    return [[InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data=callback_data)]]


def lang_keyboard():
    kb = []
    for code, data in TEXTS.items():
        kb.append([InlineKeyboardButton(text=data["lang_name"], callback_data=f"set_lang_{code}")])
    return kb


# ==================== START ====================
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    name = message.from_user.first_name

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
            "lang": "uz",
        }

    # Eski reply keyboard ni o'chirish
    remove_msg = await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
    try:
        await remove_msg.delete()
    except Exception:
        pass

    await message.answer_sticker(sticker=STICKERS["main"])
    caption = (
        f"{t(user_id, 'main_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'main_hello', name=name)}\n\n"
        f"{t(user_id, 'main_desc')}\n\n"
        f"{t(user_id, 'main_choose')}"
    )
    await message.answer(
        caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=main_menu(user_id)),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    name = callback.from_user.first_name

    caption = (
        f"{t(user_id, 'main_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'main_hello', name=name)}\n\n"
        f"{t(user_id, 'main_desc')}\n\n"
        f"{t(user_id, 'main_choose')}"
    )
    await safe_edit(callback.message, caption, main_menu(user_id))
    await callback.answer()


# ==================== 🌐 TIL ====================
@router.callback_query(F.data == "choose_lang")
async def choose_lang(callback: CallbackQuery):
    user_id = callback.from_user.id
    await safe_edit(callback.message, t(user_id, "choose_lang"), lang_keyboard() + back_button(user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_lang(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = callback.data.replace("set_lang_", "")
    user_id = callback.from_user.id

    if lang not in TEXTS:
        await callback.answer("⚠️ Error!", show_alert=True)
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": lang,
        }
    else:
        database["users"][user_id]["lang"] = lang

    name = callback.from_user.first_name
    caption = (
        f"{t(user_id, 'lang_changed')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'main_title')}\n\n"
        f"{t(user_id, 'main_hello', name=name)}\n\n"
        f"{t(user_id, 'main_desc')}\n\n"
        f"{t(user_id, 'main_choose')}"
    )
    await safe_edit(callback.message, caption, main_menu(user_id))
    await callback.answer()


@router.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    user_id = callback.from_user.id
    text = (
        f"{t(user_id, 'about_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'about_random_msg')}\n\n"
        f"{t(user_id, 'about_services')}\n"
        f"{t(user_id, 'about_s1')}\n"
        f"{t(user_id, 'about_s3')}\n\n"
        f"{t(user_id, 'about_trust')}\n"
        f"{t(user_id, 'about_t1')}\n"
        f"{t(user_id, 'about_t2')}\n"
        f"{t(user_id, 'about_t3')}\n\n"
        f"{t(user_id, 'about_contact')}"
    )
    await safe_edit(callback.message, text, back_button(user_id))
    await callback.answer()


# ==================== 🛍 DO'KON (LOTLAR) ====================
@router.callback_query(F.data == "shop_list")
async def shop_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    available_lots = [(lid, lot) for lid, lot in database["lots"].items() if get_lot_stock(lot) > 0]

    if not available_lots:
        await safe_edit(
            callback.message,
            f"{t(user_id, 'shop_title')}\n\n{t(user_id, 'shop_empty')}",
            back_button(user_id)
        )
        await callback.answer()
        return

    kb = []
    for lid, lot in available_lots:
        stock = get_lot_stock(lot)
        kb.append([InlineKeyboardButton(
            text=f"🎮 {lot['name']} — {format_money(int(lot['price']))} so'm ({stock} ta)",
            callback_data=f"view_lot_{lid}"
        )])
    kb.append([InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="back_to_main")])

    await safe_edit(
        callback.message,
        f"{t(user_id, 'shop_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'shop_available', count=len(available_lots))}\n\n"
        f"{t(user_id, 'shop_choose')}",
        kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_lot_"))
async def view_lot(callback: CallbackQuery):
    user_id = callback.from_user.id
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)

    if not lot:
        await callback.answer("⚠️ Lot topilmadi!", show_alert=True)
        return

    stock = get_lot_stock(lot)
    if stock <= 0:
        await safe_edit(
            callback.message,
            f"{t(user_id, 'shop_title')}\n\n{t(user_id, 'lot_sold_out_msg')}",
            back_button(user_id, "shop_list")
        )
        await callback.answer()
        return

    text = (
        f"🎮 **{lot['name']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 O'yin: **{lot.get('game', '—')}**\n"
        f"💰 Narxi: **{format_money(int(lot['price']))} so'm**\n"
        f"{t(user_id, 'lot_in_stock', stock=stock)}\n"
        f"📝 {lot.get('desc', '—')}"
    )
    kb = [
        [InlineKeyboardButton(text="💳 Sotib olish", callback_data=f"buy_lot_{lid}")],
        [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="shop_list")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("buy_lot_"))
async def buy_lot(callback: CallbackQuery):
    user_id = callback.from_user.id
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)
    user = callback.from_user

    if not lot:
        await callback.answer("⚠️ Lot topilmadi!", show_alert=True)
        return

    stock = get_lot_stock(lot)
    if stock <= 0:
        await callback.answer(t(user_id, "already_sold"), show_alert=True)
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    user_balance = database["users"][user_id]["balance"]
    price = int(lot["price"])

    if user_balance < price:
        await callback.answer(
            f"{t(user_id, 'not_enough')}\n{t(user_id, 'your_balance')} {format_money(user_balance)} so'm\n{t(user_id, 'price')} {format_money(price)} so'm",
            show_alert=True
        )
        return

    cred = get_available_credential(lot)
    if not cred:
        await callback.answer(t(user_id, "already_sold"), show_alert=True)
        return

    database["users"][user_id]["balance"] -= price
    database["users"][user_id]["total_spent"] += price
    database["total_sales"] += price

    cred["sold"] = True
    cred["sold_to"] = user_id
    cred["sold_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    klent_code = database["users"][user_id]["klent_code"]
    new_stock = get_lot_stock(lot)

    text = (
        f"{t(user_id, 'lot_buy_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'lot_buy_name')} **{lot['name']}**\n"
        f"{t(user_id, 'lot_buy_price')} **{format_money(price)} so'm**\n"
        f"{t(user_id, 'lot_buy_stock_left')} **{new_stock} ta**\n\n"
        f"{t(user_id, 'lot_your_credentials')}\n"
        f"📧 Email: `{cred['email']}`\n"
        f"🔑 Parol: `{cred['password']}`\n\n"
        f"{t(user_id, 'lot_credentials_note')}\n"
        f"🔖 Sizning kodingiz: `/{klent_code}`"
    )
    await safe_edit(callback.message, text, back_button(user_id))

    admin_text = (
        f"{t(ADMIN_ID, 'new_lot_order')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(ADMIN_ID, 'buyer')} **{user.full_name}**\n"
        f"{t(ADMIN_ID, 'username_label')} @{user.username}\n"
        f"{t(ADMIN_ID, 'id_label')} `{user.id}`\n"
        f"{t(ADMIN_ID, 'code_label')} `/{klent_code}`\n\n"
        f"{t(ADMIN_ID, 'lot_label')} **{lot['name']}**\n"
        f"{t(ADMIN_ID, 'price_label')} **{format_money(price)} so'm**\n"
        f"📦 Qolgan: **{new_stock} ta**\n\n"
        f"📧 Yuborilgan: `{cred['email']}`"
    )
    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")

    if new_stock == 0:
        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{t(ADMIN_ID, 'lot_sold_out_admin')}\n\n"
                 f"{t(ADMIN_ID, 'lot_label')} **{lot['name']}**\n\n"
                 f"Iltimos, yangi akkauntlar qo'shing!",
            parse_mode="Markdown"
        )

    await callback.answer(t(user_id, "buy_success"))


# ==================== PROFIL ====================
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    user = database["users"][user_id]

    text = (
        f"{t(user_id, 'profile_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'profile_id')} `{user_id}`\n"
        f"{t(user_id, 'profile_code')} `/{user['klent_code']}`\n"
        f"{t(user_id, 'profile_reg')} `{user.get('registered_at', '—')}`\n\n"
        f"{t(user_id, 'profile_balance')} `{format_money(user['balance'])} so'm`\n"
        f"{t(user_id, 'profile_spent')} `{format_money(user.get('total_spent', 0))} so'm`\n\n"
        f"{t(user_id, 'profile_security')}"
    )
    kb = [
        [InlineKeyboardButton(text=t(user_id, "btn_enter_promo"), callback_data="enter_promo")],
        [InlineKeyboardButton(text=t(user_id, "btn_lang"), callback_data="choose_lang")],
        [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "enter_promo")
async def enter_promo_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await safe_edit(
        callback.message,
        f"{t(user_id, 'promo_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'promo_hint')}\n\n"
        f"{t(user_id, 'promo_note')}",
        cancel_button(user_id, "profile")
    )
    await state.set_state(UserStates.waiting_for_activate_promo)
    await callback.answer()


@router.message(UserStates.waiting_for_activate_promo)
async def activate_promo_process(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip().upper()
    await state.clear()

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    if code not in database["promos"]:
        await message.answer(
            t(user_id, "promo_not_found"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")
            ]])
        )
        return

    promo = database["promos"][code]
    promo_amount = promo["amount"]
    promo_limit = promo.get("limit", 0)
    promo_used = promo.get("used_count", 0)

    if promo_limit > 0 and promo_used >= promo_limit:
        await message.answer(
            t(user_id, "promo_limit_out"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")
            ]])
        )
        return

    user = database["users"][user_id]

    if code in user["used_promos"]:
        await message.answer(
            t(user_id, "promo_used"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")
            ]])
        )
        return

    user["balance"] += promo_amount
    user["used_promos"].append(code)
    database["promos"][code]["used_count"] = promo_used + 1

    await message.answer(
        f"{t(user_id, 'promo_activated')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'promo_code_label')} `{code}`\n"
        f"{t(user_id, 'promo_bonus')} **{format_money(promo_amount)} so'm**\n\n"
        f"{t(user_id, 'promo_new_balance')} **{format_money(user['balance'])} so'm**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")
        ]])
    )


# ==================== BALANS TO'LDIRISH ====================
@router.callback_query(F.data == "top_up")
async def top_up_balance(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    text = (
        f"{t(user_id, 'topup_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'topup_desc')}\n\n"
        f"{t(user_id, 'topup_min')}"
    )
    kb = [
        [
            InlineKeyboardButton(text="💵 5 000", callback_data="amount_5000"),
            InlineKeyboardButton(text="💵 10 000", callback_data="amount_10000"),
        ],
        [
            InlineKeyboardButton(text="💵 20 000", callback_data="amount_20000"),
            InlineKeyboardButton(text="💵 30 000", callback_data="amount_30000"),
        ],
        [
            InlineKeyboardButton(text="💵 50 000", callback_data="amount_50000"),
            InlineKeyboardButton(text="💵 100 000", callback_data="amount_100000"),
        ],
        [InlineKeyboardButton(text=t(user_id, "btn_other_amount"), callback_data="amount_custom")],
        [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("amount_"))
async def process_amount_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data_value = callback.data.split("_")[1]

    if data_value == "custom":
        await safe_edit(
            callback.message,
            f"{t(user_id, 'custom_amount_title')}\n\n"
            f"{t(user_id, 'custom_amount_desc')}\n"
            f"{t(user_id, 'custom_amount_example')}",
            cancel_button(user_id)
        )
        await state.set_state(BuyStates.waiting_for_custom_amount)
        await callback.answer()
        return

    amount = int(data_value)
    await state.update_data(selected_amount=amount)

    await send_card_details(callback.message, amount, user_id)
    await state.set_state(BuyStates.waiting_for_receipt)
    await callback.answer()


@router.message(BuyStates.waiting_for_custom_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not message.text.isdigit():
        await message.answer(t(user_id, "only_number"))
        return

    amount = int(message.text)
    if amount < MIN_TOPUP:
        await message.answer(t(user_id, "min_sum"))
        return

    await state.update_data(selected_amount=amount)
    await send_card_details(message, amount, user_id)
    await state.set_state(BuyStates.waiting_for_receipt)


async def send_card_details(message, amount: int, user_id: int):
    text = (
        f"{t(user_id, 'card_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'card_amount')} **{format_money(amount)} so'm**\n\n"
        f"{t(user_id, 'card_pay')}\n"
        f"{t(user_id, 'card_number')} `{CARD_NUMBER}`\n"
        f"{t(user_id, 'card_holder')} `{CARD_HOLDER}`\n\n"
        f"{t(user_id, 'card_attention')}\n"
        f"{t(user_id, 'card_warn1')}\n"
        f"{t(user_id, 'card_warn2')}\n\n"
        f"{t(user_id, 'card_send_receipt')}"
    )
    kb = [[InlineKeyboardButton(text=t(user_id, "btn_cancel"), callback_data="back_to_main")]]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.message(BuyStates.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    user = message.from_user
    user_id = user.id
    state_data = await state.get_data()
    selected_amount = state_data.get("selected_amount", 0)

    if user.id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user.id] = {
            "balance": 0,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    klent_code = database["users"][user.id]["klent_code"]

    text = (
        f"{t(ADMIN_ID, 'new_receipt')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(ADMIN_ID, 'buyer')} **{user.full_name}**\n"
        f"{t(ADMIN_ID, 'username_label')} @{user.username}\n"
        f"{t(ADMIN_ID, 'id_label')} `{user.id}`\n"
        f"{t(ADMIN_ID, 'code_label')} `/{klent_code}`\n\n"
        f"{t(ADMIN_ID, 'sum_label')} **{format_money(selected_amount)} so'm**"
    )

    kb = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_yes_{user.id}_{selected_amount}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"topup_no_{user.id}"),
        ]
    ]

    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )
    await message.answer(
        f"{t(user_id, 'receipt_sent')}\n\n"
        f"{t(user_id, 'receipt_code')} `/{klent_code}`\n"
        f"{t(user_id, 'receipt_wait')}"
    )
    await state.clear()


@router.callback_query(F.data.startswith("topup_yes_"))
async def topup_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    added_amount = int(parts[3])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + f"\n\n{t(ADMIN_ID, 'approved')} (+{format_money(added_amount)} so'm)",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    if user_id in database["users"]:
        database["users"][user_id]["balance"] += added_amount
        database["total_topups"] += added_amount

        await callback.bot.send_message(
            chat_id=user_id,
            text=f"{t(user_id, 'balance_added')}\n"
                 f"━━━━━━━━━━━━━━━━━━━━\n\n"
                 f"{t(user_id, 'balance_added_amount')} **{format_money(added_amount)} so'm**\n"
                 f"{t(user_id, 'balance_new')} **{format_money(database['users'][user_id]['balance'])} so'm**",
            parse_mode="Markdown",
        )
    await callback.answer(t(ADMIN_ID, "approved").replace("**", ""))


@router.callback_query(F.data.startswith("topup_no_"))
async def topup_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[2])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + f"\n\n{t(ADMIN_ID, 'rejected')}",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await callback.bot.send_message(chat_id=user_id, text=t(user_id, "receipt_rejected"))
    await callback.answer(t(ADMIN_ID, "rejected").replace("**", ""))


# ==================== ADMIN PANEL ====================
@router.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != ADMIN_ID:
        await callback.answer(t(user_id, "admin_not_admin"), show_alert=True)
        return

    await safe_edit(
        callback.message,
        f"{t(ADMIN_ID, 'admin_pass_title')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(ADMIN_ID, 'admin_pass_desc')}\n\n"
        f"{t(ADMIN_ID, 'admin_pass_note')}",
        cancel_button(ADMIN_ID)
    )
    await state.set_state(AdminStates.waiting_for_password)
    await callback.answer()


@router.message(AdminStates.waiting_for_password)
async def check_admin_password(message: Message, state: FSMContext):
    entered_password = message.text
    try:
        await message.delete()
    except Exception:
        pass

    if entered_password == ADMIN_PASSWORD:
        await state.clear()
        await show_admin_dashboard(message)
    else:
        err_msg = await message.answer(t(ADMIN_ID, "admin_pass_wrong"))
        await asyncio.sleep(3)
        try:
            await err_msg.delete()
        except Exception:
            pass


async def show_admin_dashboard(message_or_callback, is_callback=False):
    total_users = len(database["users"])
    total_lots = len(database["lots"])
    total_stock = sum(get_lot_stock(lot) for lot in database["lots"].values())
    total_sold_creds = sum(
        sum(1 for c in lot["credentials"] if c["sold"]) for lot in database["lots"].values()
    )
    total_balance_all = sum(u["balance"] for u in database["users"].values())
    uptime_seconds = int(time.time() - bot_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    stats_str = (
        f"{t(ADMIN_ID, 'admin_stats')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(ADMIN_ID, 'admin_users_count')} **{total_users} ta**\n"
        f"{t(ADMIN_ID, 'admin_lots')} **{total_lots} ta**\n"
        f"📦 Mavjud stock: **{total_stock} ta**\n"
        f"✅ Sotilgan: **{total_sold_creds} ta**\n"
        f"{t(ADMIN_ID, 'admin_total_bal')} **{format_money(total_balance_all)} so'm**\n"
        f"{t(ADMIN_ID, 'admin_total_sales')} **{format_money(database['total_sales'])} so'm**\n"
        f"{t(ADMIN_ID, 'admin_total_topups')} **{format_money(database['total_topups'])} so'm**\n"
        f"{t(ADMIN_ID, 'admin_uptime')} **{hours}s {minutes}d**\n"
    )

    kb = [
        [InlineKeyboardButton(text="📊 To'liq statistika", callback_data="admin_full_stats")],
        [InlineKeyboardButton(text="📦 LOTLAR (Kanal)", callback_data="admin_lots_menu")],
        [InlineKeyboardButton(text="🎁 Promokod yaratish", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="📢 Rassilka", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="back_to_main")],
    ]

    text = f"{t(ADMIN_ID, 'admin_welcome')}\n\n{stats_str}"

    if is_callback:
        await safe_edit(message_or_callback.message, text, kb)
    else:
        await message_or_callback.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_panel_back")
async def admin_panel_back(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await show_admin_dashboard(callback, is_callback=True)
    await callback.answer()


@router.callback_query(F.data == "admin_full_stats")
async def admin_full_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    total_users = len(database["users"])
    total_balance = sum(u["balance"] for u in database["users"].values())
    total_spent = sum(u.get("total_spent", 0) for u in database["users"].values())
    top_users = sorted(
        database["users"].items(),
        key=lambda x: x[1].get("total_spent", 0),
        reverse=True
    )[:5]

    top_str = "🏆 **TOP 5:**\n"
    if top_users:
        for i, (uid, u) in enumerate(top_users, 1):
            top_str += f"{i}. `{uid}` — {format_money(u.get('total_spent', 0))} so'm\n"
    else:
        top_str += "—\n"

    text = (
        f"📊 **TO'LIQ STATISTIKA**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Foydalanuvchilar: **{total_users}**\n"
        f"💰 Umumiy balans: **{format_money(total_balance)} so'm**\n"
        f"💸 Umumiy sarflangan: **{format_money(total_spent)} so'm**\n"
        f"💵 Sotuvlar: **{format_money(database['total_sales'])} so'm**\n"
        f"💳 To'ldirishlar: **{format_money(database['total_topups'])} so'm**\n\n"
        f"{top_str}"
    )
    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["users"]:
        await safe_edit(callback.message, t(ADMIN_ID, "no_users"), back_button(ADMIN_ID, "admin_panel_back"))
        await callback.answer()
        return

    text = f"👥 **FOYDALANUVCHILAR** ({len(database['users'])} ta)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for uid, u in list(database["users"].items())[:50]:
        lang_flag = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}.get(u.get("lang", "uz"), "🇺🇿")
        text += (
            f"{lang_flag} `{uid}`\n"
            f"🔖 `/{u['klent_code']}`\n"
            f"💰 {format_money(u['balance'])} so'm\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
        )

    if len(database["users"]) > 50:
        text += f"\n*... va yana {len(database['users']) - 50} ta*"

    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== 📦 LOTLAR MENYU (ADMIN) ====================
@router.callback_query(F.data == "admin_lots_menu")
async def admin_lots_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    text = (
        f"📦 **LOTLAR (KANAL) MENYU**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Bu bo'limda siz kanal/lot yaratib, ichiga\n"
        f"email va parollarni qo'shishingiz mumkin.\n\n"
        f"📊 Jami lotlar: **{len(database['lots'])} ta**"
    )
    kb = [
        [InlineKeyboardButton(text="➕ Yangi lot yaratish", callback_data="admin_add_lot")],
        [InlineKeyboardButton(text="📋 Lotlarni boshqarish", callback_data="admin_manage_lots")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== LOT YARATISH ====================
@router.callback_query(F.data == "admin_add_lot")
async def admin_add_lot(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(
        callback.message,
        "📦 **YANGI LOT YARATISH**\n\n"
        "1️⃣ Lot nomini kiriting (masalan: `PUBG 30k lot`):",
        cancel_button(ADMIN_ID, "admin_lots_menu")
    )
    await state.set_state(AdminStates.adding_lot_name)
    await callback.answer()


@router.message(AdminStates.adding_lot_name)
async def admin_get_lot_name(message: Message, state: FSMContext):
    await state.update_data(lot_name=message.text)
    await message.answer("2️⃣ O'yin nomini kiriting (masalan: `PUBG Mobile`):")
    await state.set_state(AdminStates.adding_lot_game)


@router.message(AdminStates.adding_lot_game)
async def admin_get_lot_game(message: Message, state: FSMContext):
    await state.update_data(lot_game=message.text)
    await message.answer("3️⃣ Narxini kiriting (raqamda, masalan: `30000`):")
    await state.set_state(AdminStates.adding_lot_price)


@router.message(AdminStates.adding_lot_price)
async def admin_get_lot_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return
    await state.update_data(lot_price=message.text)
    await message.answer("4️⃣ Tavsif kiriting (yoki `-` yozing):")
    await state.set_state(AdminStates.adding_lot_desc)


@router.message(AdminStates.adding_lot_desc)
async def admin_get_lot_desc(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else "—"
    data = await state.get_data()

    lot_id = len(database["lots"]) + 1
    while lot_id in database["lots"]:
        lot_id += 1

    database["lots"][lot_id] = {
        "name": data["lot_name"],
        "game": data["lot_game"],
        "price": data["lot_price"],
        "desc": desc,
        "credentials": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    await state.clear()
    kb = [
        [InlineKeyboardButton(text="➕ Akkaunt qo'shish", callback_data=f"add_creds_{lot_id}")],
        [InlineKeyboardButton(text="📦 Lotlar menyu", callback_data="admin_lots_menu")],
    ]
    await message.answer(
        f"✅ **LOT YARATILDI!**\n\n"
        f"📦 Nomi: **{data['lot_name']}**\n"
        f"🎮 O'yin: {data['lot_game']}\n"
        f"💰 Narxi: **{format_money(int(data['lot_price']))} so'm**\n"
        f"📝 Tavsif: {desc}\n\n"
        f"⚠️ Endi unga **email va parollarni** qo'shishingiz kerak!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== LOTGA CREDENTIALS QO'SHISH ====================
@router.callback_query(F.data.startswith("add_creds_"))
async def add_creds_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    lot_id = int(callback.data.split("_")[2])
    lot = database["lots"].get(lot_id)
    if not lot:
        await callback.answer("⚠️ Lot topilmadi!", show_alert=True)
        return

    await state.update_data(lot_id=lot_id)
    await safe_edit(
        callback.message,
        f"📦 **{lot['name']}** ga credential qo'shish\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Email va parollarni **har biri yangi qatorda** yuboring.\n\n"
        f"📌 **Format:**\n"
        f"`email:parol`\n\n"
        f"📌 **Misol:**\n"
        f"`user1@gmail.com:parol123`\n"
        f"`user2@gmail.com:parol456`\n"
        f"`user3@gmail.com:parol789`\n\n"
        f"💡 Birdaniga ko'p qator yuborishingiz mumkin!",
        cancel_button(ADMIN_ID, "admin_lots_menu")
    )
    await state.set_state(AdminStates.adding_credentials_to_lot)
    await callback.answer()


@router.message(AdminStates.adding_credentials_to_lot)
async def add_creds_process(message: Message, state: FSMContext):
    data = await state.get_data()
    lot_id = data["lot_id"]
    lot = database["lots"].get(lot_id)
    if not lot:
        await state.clear()
        await message.answer("⚠️ Lot topilmadi!")
        return

    lines = [l.strip() for l in message.text.strip().split("\n") if l.strip()]
    added = 0
    errors = []

    for line in lines:
        if ":" not in line:
            errors.append(line)
            continue
        parts = line.split(":", 1)
        email = parts[0].strip()
        password = parts[1].strip()
        if not email or not password:
            errors.append(line)
            continue

        already_exists = False
        for other_lot in database["lots"].values():
            for c in other_lot["credentials"]:
                if c["email"].lower() == email.lower():
                    already_exists = True
                    break
            if already_exists:
                break

        if already_exists:
            errors.append(f"{line} (allaqachon mavjud)")
            continue

        lot["credentials"].append({
            "email": email,
            "password": password,
            "sold": False,
            "sold_to": None,
            "sold_at": None,
        })
        added += 1

    await state.clear()

    stock = get_lot_stock(lot)
    text = (
        f"✅ **{added} ta credential qo'shildi!**\n\n"
        f"📦 Lot: **{lot['name']}**\n"
        f"📊 Jami stock: **{stock} ta**\n"
    )
    if errors:
        text += f"\n⚠️ **Xatolar ({len(errors)} ta):**\n"
        for e in errors[:10]:
            text += f"• `{e}`\n"
        if len(errors) > 10:
            text += f"*... va yana {len(errors) - 10} ta*\n"

    kb = [
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data=f"add_creds_{lot_id}")],
        [InlineKeyboardButton(text="📋 Lotni ko'rish", callback_data=f"view_lot_admin_{lot_id}")],
        [InlineKeyboardButton(text="📦 Lotlar menyu", callback_data="admin_lots_menu")],
    ]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


# ==================== LOTLARNI BOSHQARISH ====================
@router.callback_query(F.data == "admin_manage_lots")
async def admin_manage_lots(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["lots"]:
        await safe_edit(callback.message, t(ADMIN_ID, "no_lots"), back_button(ADMIN_ID, "admin_lots_menu"))
        await callback.answer()
        return

    kb = []
    for lid, lot in database["lots"].items():
        stock = get_lot_stock(lot)
        total = len(lot["credentials"])
        status = "🟢" if stock > 0 else "🔴"
        kb.append([InlineKeyboardButton(
            text=f"{status} #{lid} {lot['name']} ({stock}/{total})",
            callback_data=f"view_lot_admin_{lid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_lots_menu")])

    await safe_edit(callback.message, "📋 **LOTLARNI BOSHQARISH:**", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("view_lot_admin_"))
async def view_lot_admin(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[3])
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Lot topilmadi!", show_alert=True)
        return

    stock = get_lot_stock(lot)
    total = len(lot["credentials"])
    sold = total - stock

    sold_list = ""
    for c in lot["credentials"]:
        if c["sold"]:
            sold_list += f"• `{c['email']}` → `{c['sold_to']}` ({c['sold_at']})\n"

    text = (
        f"📦 **{lot['name']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 O'yin: **{lot.get('game', '—')}**\n"
        f"💰 Narxi: **{format_money(int(lot['price']))} so'm**\n"
        f"📝 Tavsif: {lot.get('desc', '—')}\n\n"
        f"📊 **STATISTIKA:**\n"
        f"📦 Jami: **{total} ta**\n"
        f"🟢 Mavjud: **{stock} ta**\n"
        f"✅ Sotilgan: **{sold} ta**\n"
    )

    if sold_list:
        text += f"\n📋 **Sotilganlar:**\n{sold_list}"

    if stock == 0:
        text += "\n\n🔴 **LOT TO'LIQ SOTILDI!**"

    kb = [
        [InlineKeyboardButton(text="➕ Credential qo'shish", callback_data=f"add_creds_{lid}")],
        [InlineKeyboardButton(text="👁 Mavjud credentiallar", callback_data=f"show_creds_{lid}")],
        [InlineKeyboardButton(text="🗑 Lotni o'chirish", callback_data=f"delete_lot_{lid}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_manage_lots")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("show_creds_"))
async def show_creds(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Lot topilmadi!", show_alert=True)
        return

    available = [c for c in lot["credentials"] if not c["sold"]]
    if not available:
        await safe_edit(callback.message, "⚠️ Mavjud credential yo'q!", back_button(ADMIN_ID, f"view_lot_admin_{lid}"))
        await callback.answer()
        return

    text = f"👁 **{lot['name']} — Mavjud credentiallar** ({len(available)} ta)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for c in available[:50]:
        text += f"• `{c['email']}:{c['password']}`\n"
    if len(available) > 50:
        text += f"\n*... va yana {len(available) - 50} ta*"

    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"view_lot_admin_{lid}")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_lot_"))
async def delete_lot(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    if lid in database["lots"]:
        del database["lots"][lid]
        await callback.answer("✅ Lot o'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
    await admin_manage_lots(callback)


# ==================== PROMOKOD YARATISH ====================
@router.callback_query(F.data == "admin_create_promo")
async def admin_create_promo(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "🎁 **PROMOKOD YARATISH**\n\nKodni kiriting:", cancel_button(ADMIN_ID, "admin_panel_back"))
    await state.set_state(AdminStates.waiting_for_promo_code)
    await callback.answer()


@router.message(AdminStates.waiting_for_promo_code)
async def admin_get_promo_code(message: Message, state: FSMContext):
    promo_code = message.text.strip().upper()
    await state.update_data(promo_code=promo_code)
    await message.answer("💰 Qiymatini kiriting (so'mda):")
    await state.set_state(AdminStates.waiting_for_promo_amount)


@router.message(AdminStates.waiting_for_promo_amount)
async def admin_get_promo_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return
    await state.update_data(promo_amount=int(message.text))
    await message.answer("🔢 Limit (0 = cheksiz):")
    await state.set_state(AdminStates.waiting_for_promo_limit)


@router.message(AdminStates.waiting_for_promo_limit)
async def admin_get_promo_limit(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return

    data = await state.get_data()
    promo_code = data["promo_code"]
    amount = data["promo_amount"]
    limit = int(message.text)

    database["promos"][promo_code] = {
        "amount": amount,
        "limit": limit,
        "used_count": 0,
    }

    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel_back")]]
    limit_text = "cheksiz" if limit == 0 else f"{limit} ta"
    await message.answer(
        f"✅ **PROMOKOD YARATILDI!**\n\n"
        f"🎁 Kod: `{promo_code}`\n"
        f"💰 Qiymat: **{format_money(amount)} so'm**\n"
        f"🔢 Limit: **{limit_text}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== RASILKA ====================
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "📢 **RASSILKA**\n\nXabar yuboring:", cancel_button(ADMIN_ID, "admin_panel_back"))
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    await state.clear()
    count = 0
    failed = 0
    for user_id in database["users"].keys():
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    kb = [[InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **RASSILKA TUGADI!**\n\n✔️ Yuborildi: **{count}**\n❌ Xato: **{failed}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== /klent VA /user ====================
@router.message(F.text.startswith("/klent"))
async def admin_manage_klent(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠ Format:\n`/klent1 Salom`\n`/klent1 +40000`", parse_mode="Markdown")
        return

    klent_code_input = parts[0][1:]
    command_body = parts[1].strip()

    target_user_id = None
    target_user_data = None
    for uid, udata in database["users"].items():
        if udata["klent_code"] == klent_code_input:
            target_user_id = uid
            target_user_data = udata
            break

    if not target_user_id:
        await message.reply(f"❌ Topilmadi: `/{klent_code_input}`", parse_mode="Markdown")
        return

    cleaned_body = command_body.replace(" ", "")
    if cleaned_body.startswith("+") or cleaned_body.startswith("-") or cleaned_body.isdigit():
        try:
            amount = int(cleaned_body)
            target_user_data["balance"] += amount
            new_balance = target_user_data["balance"]

            await message.reply(
                f"✅ `/{klent_code_input}` balansi: **{amount:+,} so'm**\n"
                f"💰 Yangi: **{format_money(new_balance)} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"{t(target_user_id, 'balance_changed')}\n\n"
                         f"{t(target_user_id, 'balance_change')} **{amount:+,} so'm**\n"
                         f"{t(target_user_id, 'balance_current')} **{format_money(new_balance)} so'm**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=f"{t(target_user_id, 'msg_from_admin')}\n\n{command_body}",
            parse_mode="Markdown"
        )
        await message.reply(f"✅ Xabar `/{klent_code_input}` ga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")


@router.message(F.text.startswith("/user"))
async def admin_manage_user_id(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.reply("⚠ Format: `/user 123456789 +40000`", parse_mode="Markdown")
        return

    if not parts[1].isdigit():
        await message.reply("❌ ID faqat raqam!")
        return

    target_user_id = int(parts[1])
    command_body = parts[2].strip()

    if target_user_id not in database["users"]:
        await message.reply("❌ Bu ID ro'yxatdan o'tmagan!")
        return

    target_user_data = database["users"][target_user_id]
    cleaned_body = command_body.replace(" ", "")

    if cleaned_body.startswith("+") or cleaned_body.startswith("-") or cleaned_body.isdigit():
        try:
            amount = int(cleaned_body)
            target_user_data["balance"] += amount
            new_balance = target_user_data["balance"]

            await message.reply(
                f"✅ ID `{target_user_id}` balansi: **{amount:+,} so'm**\n"
                f"💰 Yangi: **{format_money(new_balance)} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"{t(target_user_id, 'balance_changed')}\n\n"
                         f"{t(target_user_id, 'balance_change')} **{amount:+,} so'm**\n"
                         f"{t(target_user_id, 'balance_current')} **{format_money(new_balance)} so'm**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=f"{t(target_user_id, 'msg_from_admin')}\n\n{command_body}",
            parse_mode="Markdown"
        )
        await message.reply(f"✅ Xabar `{target_user_id}` ga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")


# ==================== BOTNI ISHGA TUSHIRISH ====================
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🏠 Asosiy menyu"),
        BotCommand(command="lang", description="🌐 Til / Язык / Language"),
        BotCommand(command="help", description="ℹ️ Yordam"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command("lang"))
async def cmd_lang(message: Message):
    user_id = message.from_user.id
    await message.answer(
        t(user_id, "choose_lang"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=lang_keyboard()),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        f"ℹ️ **HELP**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• `/start` — Asosiy menyu\n"
        f"• `/lang` — Tilni o'zgartirish\n"
        f"• `/help` — Yordam\n\n"
        f"📞 @samir_admin",
        parse_mode="Markdown"
    )


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await set_bot_commands(bot)

    print("╔══════════════════════════════════╗")
    print("║   🚀 ALONE PUBG SHOP              ║")
    print("║   ✅ Ishga tushdi!                ║")
    print(f"║   👑 Admin: {ADMIN_ID}        ║")
    print("║   🌐 UZ / RU / EN                 ║")
    print("║   📦 LOT (KANAL) TIZIMI           ║")
    print("╚══════════════════════════════════╝")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())