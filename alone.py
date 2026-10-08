import asyncio
import logging
import time
import os
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
from supabase import create_client, Client

# === SOZLAMALAR ===
TOKEN = os.getenv("TOKEN", "8692469958:AAH75IR4Wvo1fF4zxD1eH5P013KF72Y0cLY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6650430442"))
ADMIN_PASSWORD = "alone"
CARD_NUMBER = "8600 1402 3999 1731"
CARD_HOLDER = "N.m"
MIN_TOPUP = 5000

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

logging.basicConfig(level=logging.INFO)
router = Router()
bot_start_time = time.time()

supabase: Client = None

# ==================== SUPABASE ====================
def init_supabase():
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase ulandi: {SUPABASE_URL}")
    else:
        print("⚠️ Supabase URL/KEY yo'q — xotirada ishlaydi")
        supabase = None


# ==================== BAZADAN YUKLASH ====================
def load_database():
    """Supabase'dan barcha ma'lumotlarni yuklash"""
    if not supabase:
        return

    try:
        # Users
        res = supabase.table("users").select("*").execute()
        for u in res.data:
            database["users"][u["user_id"]] = {
                "balance": u.get("balance", 0),
                "klent_code": u.get("klent_code", ""),
                "lang": u.get("lang", "uz"),
                "registered_at": u.get("registered_at", ""),
                "total_spent": u.get("total_spent", 0),
                "used_promos": u.get("used_promos") or [],
            }

        # Lots
        res = supabase.table("lots").select("*").execute()
        for l in res.data:
            database["lots"][l["lot_id"]] = {
                "name": l.get("name", ""),
                "game": l.get("game", ""),
                "price": l.get("price", "0"),
                "desc": l.get("desc_text", "—"),
                "created_at": l.get("created_at", ""),
                "credentials": [],
            }

        # Credentials
        res = supabase.table("credentials").select("*").execute()
        for c in res.data:
            lot_id = c.get("lot_id")
            if lot_id in database["lots"]:
                database["lots"][lot_id]["credentials"].append({
                    "email": c.get("email", ""),
                    "password": c.get("password", ""),
                    "sold": c.get("sold", False),
                    "sold_to": c.get("sold_to"),
                    "sold_at": c.get("sold_at"),
                })

        # Promos
        res = supabase.table("promos").select("*").execute()
        for p in res.data:
            database["promos"][p["code"]] = {
                "amount": p.get("amount", 0),
                "limit": p.get("limit_count", 0),
                "used_count": p.get("used_count", 0),
            }

        # Stats
        res = supabase.table("stats").select("*").execute()
        for s in res.data:
            if s["key"] in database:
                database[s["key"]] = s["value"]

        print(f"✅ Baza yuklandi: {len(database['users'])} user, {len(database['lots'])} lot")
    except Exception as e:
        print(f"❌ Load xatolik: {e}")


# ==================== YANGILASH ====================
def save_user(user_id):
    if not supabase or user_id not in database["users"]:
        return
    try:
        u = database["users"][user_id]
        supabase.table("users").upsert({
            "user_id": user_id,
            "balance": u.get("balance", 0),
            "klent_code": u.get("klent_code", ""),
            "lang": u.get("lang", "uz"),
            "registered_at": u.get("registered_at", ""),
            "total_spent": u.get("total_spent", 0),
            "used_promos": u.get("used_promos", []),
        }).execute()
    except Exception as e:
        print(f"❌ save_user: {e}")


def save_lot(lot_id):
    if not supabase or lot_id not in database["lots"]:
        return
    try:
        l = database["lots"][lot_id]
        supabase.table("lots").upsert({
            "lot_id": lot_id,
            "name": l.get("name", ""),
            "game": l.get("game", ""),
            "price": l.get("price", "0"),
            "desc_text": l.get("desc", "—"),
            "created_at": l.get("created_at", ""),
        }).execute()
        # Credentials ni yangilash
        for c in l.get("credentials", []):
            supabase.table("credentials").upsert({
                "lot_id": lot_id,
                "email": c.get("email", ""),
                "password": c.get("password", ""),
                "sold": c.get("sold", False),
                "sold_to": c.get("sold_to"),
                "sold_at": c.get("sold_at"),
            }, on_conflict="email").execute()
    except Exception as e:
        print(f"❌ save_lot: {e}")


def delete_lot_db(lot_id):
    if not supabase:
        return
    try:
        supabase.table("lots").delete().eq("lot_id", lot_id).execute()
    except Exception as e:
        print(f"❌ delete_lot: {e}")


def save_promo(code):
    if not supabase or code not in database["promos"]:
        return
    try:
        p = database["promos"][code]
        supabase.table("promos").upsert({
            "code": code,
            "amount": p.get("amount", 0),
            "limit_count": p.get("limit", 0),
            "used_count": p.get("used_count", 0),
        }).execute()
    except Exception as e:
        print(f"❌ save_promo: {e}")


def delete_promo_db(code):
    if not supabase:
        return
    try:
        supabase.table("promos").delete().eq("code", code).execute()
    except Exception as e:
        print(f"❌ delete_promo: {e}")


def save_stats(key, value):
    if not supabase:
        return
    try:
        supabase.table("stats").upsert({"key": key, "value": value}).execute()
    except Exception as e:
        print(f"❌ save_stats: {e}")


def save_lot_counter():
    save_stats("lot_counter", database.get("lot_counter", 0))


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
        "shop_available": "📦 Jami lotlar: **{count} ta**",
        "shop_choose": "Kerakli lotni tanlang:",
        "lot_in_stock": "📦 Mavjud: **{stock} ta**",
        "lot_sold_out_msg": "🔴 **Bu lot to'liq sotildi!**",
        "lot_buy_title": "🎉 **XARID MUVAFFAQIYATLI!** 👑",
        "lot_buy_name": "🏷 Lot:",
        "lot_buy_price": "💰 Narxi:",
        "lot_buy_stock_left": "📦 Qolgan:",
        "lot_your_credentials": "🔑 **SIZNING MA'LUMOTLARINGIZ:**",
        "lot_credentials_note": "⚠️ *Bu ma'lumotlar faqat sizga tegishli.*",
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
        "promo_not_found": "❌ **Promokod topilmadi!**",
        "promo_used": "⚠️ **Siz bu promokoddan foydalangansiz!**",
        "promo_activated": "🎉 **PROMOKOD FAOLLASHTIRILDI!**",
        "promo_sent_to_admin": "✅ **Promokod qabul qilindi!**",
        "btn_to_profile": "👤 Profilga qaytish",
        "topup_title": "💳 **HISOBNI TO'LDIRISH** ⚡️",
        "topup_desc": "To'ldirmoqchi bo'lgan summani tanlang:",
        "topup_min": "💡 *Minimal: 5 000 so'm*",
        "btn_other_amount": "✍️ Boshqa summa",
        "custom_amount_title": "✍️ **SUMMANI KIRITING**",
        "custom_amount_desc": "Summani raqamlarda kiriting:",
        "custom_amount_example": "📌 *Misol: 5000*",
        "card_title": "💳 **TO'LOV MA'LUMOTLARI** ⚠️",
        "card_amount": "💰 Tanlangan summa:",
        "card_pay": "📌 Quyidagi kartaga to'lov qiling:",
        "card_number": "💳 Karta:",
        "card_holder": "👤 Egasi:",
        "card_attention": "🚨 **DIQQAT!**",
        "card_warn1": "• To'lovni **aniq** summada qiling",
        "card_warn2": "• Kam to'lov qilsangiz — pul qaytarilmaydi!",
        "card_send_receipt": "📸 To'lovdan so'ng **chek** ni botga yuboring!",
        "receipt_sent": "✅ **CHEKINGIZ YUBORILDI!**",
        "receipt_code": "🔖 Sizning kodingiz:",
        "receipt_wait": "⏳ Admin tez orada tekshiradi.",
        "balance_added": "✅ **BALANS TO'LDIRILDI!** 🎉",
        "balance_added_amount": "💰 Qo'shildi:",
        "balance_new": "💎 Yangi balans:",
        "receipt_rejected": "❌ **To'lov rad etildi!**",
        "not_enough": "❌ Mablag' yetarli emas!",
        "your_balance": "Sizda:",
        "price": "Narxi:",
        "only_number": "❌ Faqat raqam kiriting:",
        "min_sum": "❌ Minimal: **5 000 so'm**:",
        "already_sold": "⚠️ Bu allaqachon sotilgan!",
        "buy_success": "✅ Xarid muvaffaqiyatli!",
        "admin_pass_title": "🔐 **ADMIN PANEL** 🛡",
        "admin_pass_desc": "Maxfiy parolni kiriting:",
        "admin_pass_note": "🔒 *Parol maxfiy saqlanadi*",
        "admin_pass_wrong": "❌ **Xato parol!**",
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
        "new_receipt": "📥 **YANGI CHEK!** 🔔",
        "sum_label": "💰 Summa:",
        "approved": "✅ **TASDIQLANDI**",
        "rejected": "❌ **RAD ETILDI**",
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "choose_lang": "🌐 **ВЫБЕРИТЕ ЯЗЫК**\n━━━━━━━━━━━━━━━━━━━━\n\nВыберите удобный язык:",
        "lang_changed": "✅ Язык изменён: **Русский**",
        "main_title": "✨ **ALONE PUBG SHOP** ✨",
        "main_hello": "👋 Привет, **{name}**! 💎",
        "main_desc": "🔥 Официальный магазин **PUBG Mobile** аккаунтов.",
        "main_choose": "⚡️ Выберите раздел и начните покупки!",
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
        "about_contact": "📞 **Связь:** @samir_admin",
        "shop_title": "🛍 **МАГАЗИН** ⚡️",
        "shop_empty": "😔 Пока нет лотов.",
        "shop_available": "📦 Всего лотов: **{count} шт**",
        "shop_choose": "Выберите лот:",
        "lot_in_stock": "📦 В наличии: **{stock} шт**",
        "lot_sold_out_msg": "🔴 **Лот полностью продан!**",
        "lot_buy_title": "🎉 **ПОКУПКА УСПЕШНА!** 👑",
        "lot_buy_name": "🏷 Лот:",
        "lot_buy_price": "💰 Цена:",
        "lot_buy_stock_left": "📦 Осталось:",
        "lot_your_credentials": "🔑 **ВАШИ ДАННЫЕ:**",
        "lot_credentials_note": "⚠️ *Эти данные только для вас.*",
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
        "promo_hint": "Отправьте промокод:",
        "promo_note": "📌 *Промокод не чувствителен к регистру*",
        "promo_not_found": "❌ **Промокод не найден!**",
        "promo_used": "⚠️ **Вы уже использовали его!**",
        "promo_activated": "🎉 **ПРОМОКОД АКТИВИРОВАН!**",
        "promo_sent_to_admin": "✅ **Промокод принят!**",
        "btn_to_profile": "👤 В профиль",
        "topup_title": "💳 **ПОПОЛНЕНИЕ** ⚡️",
        "topup_desc": "Выберите сумму:",
        "topup_min": "💡 *Минимум: 5 000 сум*",
        "btn_other_amount": "✍️ Другая сумма",
        "custom_amount_title": "✍️ **ВВЕДИТЕ СУММУ**",
        "custom_amount_desc": "Введите сумму цифрами:",
        "custom_amount_example": "📌 *Пример: 5000*",
        "card_title": "💳 **ПЛАТЁЖНЫЕ ДАННЫЕ** ⚠️",
        "card_amount": "💰 Выбранная сумма:",
        "card_pay": "📌 Оплатите на карту:",
        "card_number": "💳 Карта:",
        "card_holder": "👤 Владелец:",
        "card_attention": "🚨 **ВНИМАНИЕ!**",
        "card_warn1": "• Оплатите **точную** сумму",
        "card_warn2": "• При недоплате — без возврата!",
        "card_send_receipt": "📸 Отправьте **чек** в бот!",
        "receipt_sent": "✅ **ЧЕК ОТПРАВЛЕН!**",
        "receipt_code": "🔖 Ваш код:",
        "receipt_wait": "⏳ Админ скоро проверит.",
        "balance_added": "✅ **БАЛАНС ПОПОЛНЕН!** 🎉",
        "balance_added_amount": "💰 Добавлено:",
        "balance_new": "💎 Новый баланс:",
        "receipt_rejected": "❌ **Платёж отклонён!**",
        "not_enough": "❌ Недостаточно средств!",
        "your_balance": "У вас:",
        "price": "Цена:",
        "only_number": "❌ Только цифры:",
        "min_sum": "❌ Минимум: **5 000 сум**:",
        "already_sold": "⚠️ Уже продано!",
        "buy_success": "✅ Успешно!",
        "admin_pass_title": "🔐 **АДМИН ПАНЕЛЬ** 🛡",
        "admin_pass_desc": "Введите пароль:",
        "admin_pass_note": "🔒 *Пароль в секрете*",
        "admin_pass_wrong": "❌ **Неверный пароль!**",
        "admin_welcome": "🔒 **ПАРОЛЬ ПОДТВЕРЖДЁН** ✅\n\nДобро пожаловать! 👑",
        "admin_stats": "📊 **СТАТИСТИКА**",
        "admin_users_count": "👥 Пользователи:",
        "admin_lots": "📦 Лоты:",
        "admin_total_bal": "💰 Общий баланс:",
        "admin_total_sales": "💵 Продажи:",
        "admin_total_topups": "💳 Пополнения:",
        "admin_uptime": "⏱ Uptime:",
        "admin_not_admin": "⛔️ Вы не админ!",
        "msg_from_admin": "📦 **Сообщение от админа:** 🔔",
        "balance_changed": "🎁 **БАЛАНС ИЗМЕНЁН!**",
        "balance_change": "Изменение:",
        "balance_current": "💰 Текущий:",
        "no_users": "👥 Пока нет пользователей.",
        "no_lots": "⚠️ Нет лотов.",
        "new_lot_order": "🛒 **НОВЫЙ ЛОТ КУПЛЕН!** 🔔",
        "buyer": "👤 Покупатель:",
        "username_label": "🔗 Username:",
        "id_label": "🆔 ID:",
        "code_label": "🔖 КОД:",
        "lot_label": "📦 Лот:",
        "price_label": "💰 Цена:",
        "new_receipt": "📥 **НОВЫЙ ЧЕК!** 🔔",
        "sum_label": "💰 Сумма:",
        "approved": "✅ **ПОДТВЕРЖДЕНО**",
        "rejected": "❌ **ОТКЛОНЕНО**",
    },
    "en": {
        "lang_name": "🇬🇧 English",
        "choose_lang": "🌐 **CHOOSE LANGUAGE**\n━━━━━━━━━━━━━━━━━━━━\n\nSelect your preferred language:",
        "lang_changed": "✅ Language changed: **English**",
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
        "about_contact": "📞 **Contact:** @samir_admin",
        "shop_title": "🛍 **SHOP** ⚡️",
        "shop_empty": "😔 No lots yet.",
        "shop_available": "📦 Total lots: **{count}**",
        "shop_choose": "Choose the lot:",
        "lot_in_stock": "📦 In stock: **{stock}**",
        "lot_sold_out_msg": "🔴 **Lot fully sold out!**",
        "lot_buy_title": "🎉 **PURCHASE SUCCESSFUL!** 👑",
        "lot_buy_name": "🏷 Lot:",
        "lot_buy_price": "💰 Price:",
        "lot_buy_stock_left": "📦 Left:",
        "lot_your_credentials": "🔑 **YOUR CREDENTIALS:**",
        "lot_credentials_note": "⚠️ *Only for you.*",
        "lot_sold_out_admin": "🔴 **LOT SOLD OUT!**",
        "profile_title": "👤 **PROFILE** 💎",
        "profile_id": "🆔 Telegram ID:",
        "profile_code": "🔖 Your code:",
        "profile_reg": "📅 Registered:",
        "profile_balance": "💰 **Balance:**",
        "profile_spent": "💸 **Spent:**",
        "profile_security": "⚡️ Security: High 🔒",
        "btn_enter_promo": "🎁 Enter Promo",
        "promo_title": "🎁 **ENTER PROMO CODE**",
        "promo_hint": "Send promo code:",
        "promo_note": "📌 *Case-insensitive*",
        "promo_not_found": "❌ **Promo not found!**",
        "promo_used": "⚠️ **Already used!**",
        "promo_activated": "🎉 **PROMO ACTIVATED!**",
        "promo_sent_to_admin": "✅ **Promo accepted!**",
        "btn_to_profile": "👤 Back to Profile",
        "topup_title": "💳 **TOP UP** ⚡️",
        "topup_desc": "Choose amount:",
        "topup_min": "💡 *Minimum: 5 000 so'm*",
        "btn_other_amount": "✍️ Other amount",
        "custom_amount_title": "✍️ **ENTER AMOUNT**",
        "custom_amount_desc": "Enter amount in digits:",
        "custom_amount_example": "📌 *Example: 5000*",
        "card_title": "💳 **PAYMENT DETAILS** ⚠️",
        "card_amount": "💰 Amount:",
        "card_pay": "📌 Pay to card:",
        "card_number": "💳 Card:",
        "card_holder": "👤 Holder:",
        "card_attention": "🚨 **ATTENTION!**",
        "card_warn1": "• Pay **exact** amount",
        "card_warn2": "• Underpayment — no refund!",
        "card_send_receipt": "📸 Send **receipt** to bot!",
        "receipt_sent": "✅ **RECEIPT SENT!**",
        "receipt_code": "🔖 Your code:",
        "receipt_wait": "⏳ Admin will verify soon.",
        "balance_added": "✅ **BALANCE TOPPED UP!** 🎉",
        "balance_added_amount": "💰 Added:",
        "balance_new": "💎 New balance:",
        "receipt_rejected": "❌ **Payment rejected!**",
        "not_enough": "❌ Not enough funds!",
        "your_balance": "You have:",
        "price": "Price:",
        "only_number": "❌ Numbers only:",
        "min_sum": "❌ Minimum: **5 000 so'm**:",
        "already_sold": "⚠️ Already sold!",
        "buy_success": "✅ Successful!",
        "admin_pass_title": "🔐 **ADMIN PANEL** 🛡",
        "admin_pass_desc": "Enter password:",
        "admin_pass_note": "🔒 *Password secret*",
        "admin_pass_wrong": "❌ **Wrong password!**",
        "admin_welcome": "🔒 **PASSWORD CONFIRMED** ✅\n\nWelcome! 👑",
        "admin_stats": "📊 **STATISTICS**",
        "admin_users_count": "👥 Users:",
        "admin_lots": "📦 Lots:",
        "admin_total_bal": "💰 Total balance:",
        "admin_total_sales": "💵 Sales:",
        "admin_total_topups": "💳 Top-ups:",
        "admin_uptime": "⏱ Uptime:",
        "admin_not_admin": "⛔️ You're not admin!",
        "msg_from_admin": "📦 **Message from admin:** 🔔",
        "balance_changed": "🎁 **BALANCE CHANGED!**",
        "balance_change": "Change:",
        "balance_current": "💰 Current:",
        "no_users": "👥 No users yet.",
        "no_lots": "⚠️ No lots.",
        "new_lot_order": "🛒 **NEW LOT PURCHASED!** 🔔",
        "buyer": "👤 Buyer:",
        "username_label": "🔗 Username:",
        "id_label": "🆔 ID:",
        "code_label": "🔖 CODE:",
        "lot_label": "📦 Lot:",
        "price_label": "💰 Price:",
        "new_receipt": "📥 **NEW RECEIPT!** 🔔",
        "sum_label": "💰 Amount:",
        "approved": "✅ **APPROVED**",
        "rejected": "❌ **REJECTED**",
    },
}


# ==================== FSM ====================
class AdminStates(StatesGroup):
    waiting_for_password = State()
    adding_lot_name = State()
    adding_lot_game = State()
    adding_lot_price = State()
    adding_lot_desc = State()
    adding_credentials_to_lot = State()
    editing_lot_name = State()
    editing_lot_game = State()
    editing_lot_price = State()
    editing_lot_desc = State()
    waiting_for_promo_code = State()
    waiting_for_promo_amount = State()
    waiting_for_promo_limit = State()
    waiting_for_broadcast = State()


class BuyStates(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_receipt = State()


class UserStates(StatesGroup):
    waiting_for_activate_promo = State()


# ==================== BAZA ====================
database = {
    "lots": {},
    "users": {},
    "promos": {},
    "klent_counter": 0,
    "total_topups": 0,
    "total_sales": 0,
    "lot_counter": 0,
}


# ==================== YORDAMCHILAR ====================
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


def parse_amount(text):
    cleaned = text.replace(".", "").replace(" ", "").replace(",", "")
    if cleaned.startswith("-"):
        num = cleaned[1:]
        if num.isdigit():
            return -int(num)
    elif cleaned.startswith("+"):
        num = cleaned[1:]
        if num.isdigit():
            return int(num)
    elif cleaned.isdigit():
        return int(cleaned)
    return None


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
    return [[InlineKeyboardButton(text=data["lang_name"], callback_data=f"set_lang_{code}")]
            for code, data in TEXTS.items()]


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
        save_user(user_id)
        save_stats("klent_counter", database["klent_counter"])

    remove_msg = await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
    try:
        await remove_msg.delete()
    except Exception:
        pass

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


# ==================== TIL ====================
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
            "balance": 0, "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [], "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": lang,
        }
    else:
        database["users"][user_id]["lang"] = lang
    save_user(user_id)

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


# ==================== SHOP ====================
@router.callback_query(F.data == "shop_list")
async def shop_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    all_lots = list(database["lots"].items())

    if not all_lots:
        await safe_edit(callback.message, f"{t(user_id, 'shop_title')}\n\n{t(user_id, 'shop_empty')}", back_button(user_id))
        await callback.answer()
        return

    kb = []
    for lid, lot in all_lots:
        stock = get_lot_stock(lot)
        if stock > 0:
            kb.append([InlineKeyboardButton(
                text=f"🎮 {lot['name']} — {format_money(int(lot['price']))} so'm | 📦 {stock} ta",
                callback_data=f"view_lot_{lid}"
            )])
        else:
            kb.append([InlineKeyboardButton(
                text=f"🔴 {lot['name']} — SOTILDI (0 ta)",
                callback_data=f"view_lot_{lid}"
            )])
    kb.append([InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="back_to_main")])

    await safe_edit(
        callback.message,
        f"{t(user_id, 'shop_title')}\n━━━━━━━━━━━━━━━━━━━━\n\n{t(user_id, 'shop_available', count=len(all_lots))}\n\n{t(user_id, 'shop_choose')}",
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
    text = (
        f"🎮 **{lot['name']}**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 O'yin: **{lot.get('game', '—')}**\n"
        f"💰 Narxi: **{format_money(int(lot['price']))} so'm**\n"
        f"📦 Qolgan: **{stock} ta**\n"
        f"📝 {lot.get('desc', '—')}"
    )
    if stock > 0:
        kb = [
            [InlineKeyboardButton(text="💳 Sotib olish", callback_data=f"buy_lot_{lid}")],
            [InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="shop_list")]
        ]
    else:
        text += "\n\n🔴 **BU LOT TO'LIQ SOTILDI!**"
        kb = [[InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="shop_list")]]

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
            "balance": 0, "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [], "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    user_balance = database["users"][user_id]["balance"]
    price = int(lot["price"])

    if user_balance < price:
        await callback.answer(f"{t(user_id, 'not_enough')}\n{t(user_id, 'your_balance')} {format_money(user_balance)}\n{t(user_id, 'price')} {format_money(price)}", show_alert=True)
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

    save_user(user_id)
    save_lot(lid)
    save_stats("total_sales", database["total_sales"])

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
        f"🔖 `/{klent_code}`"
    )
    await safe_edit(callback.message, text, back_button(user_id))

    admin_text = (
        f"{t(ADMIN_ID, 'new_lot_order')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(ADMIN_ID, 'buyer')} **{user.full_name}**\n"
        f"🔗 @{user.username}\n"
        f"🆔 `{user.id}`\n"
        f"🔖 `/{klent_code}`\n\n"
        f"{t(ADMIN_ID, 'lot_label')} **{lot['name']}**\n"
        f"{t(ADMIN_ID, 'price_label')} **{format_money(price)} so'm**\n"
        f"📦 Qolgan: **{new_stock} ta**"
    )
    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await callback.answer(t(user_id, "buy_success"))


# ==================== PROFIL ====================
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [], "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }
        save_user(user_id)

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
        f"{t(user_id, 'promo_title')}\n━━━━━━━━━━━━━━━━━━━━\n\n{t(user_id, 'promo_hint')}\n\n{t(user_id, 'promo_note')}",
        cancel_button(user_id, "profile")
    )
    await state.set_state(UserStates.waiting_for_activate_promo)
    await callback.answer()


@router.message(UserStates.waiting_for_activate_promo)
async def activate_promo_process(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip()
    await state.clear()

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [], "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    code_upper = code.upper()
    promo_found = None
    promo_code_found = None
    for pc, pdata in database["promos"].items():
        if pc.upper() == code_upper:
            promo_found = pdata
            promo_code_found = pc
            break

    if not promo_found:
        await message.answer(t(user_id, "promo_not_found"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")]]))
        return

    promo = promo_found
    promo_amount = promo["amount"]
    promo_limit = promo.get("limit", 0)
    promo_used = promo.get("used_count", 0)

    if promo_limit > 0 and promo_used >= promo_limit:
        await message.answer("⚠️ Limit tugagan!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")]]))
        return

    user = database["users"][user_id]
    if promo_code_found in user["used_promos"]:
        await message.answer(t(user_id, "promo_used"),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")]]))
        return

    user["balance"] += promo_amount
    user["used_promos"].append(promo_code_found)
    database["promos"][promo_code_found]["used_count"] = promo_used + 1

    save_user(user_id)
    save_promo(promo_code_found)

    await message.answer(
        f"{t(user_id, 'promo_activated')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 `{promo_code_found}`\n💰 **{format_money(promo_amount)} so'm**\n\n"
        f"{t(user_id, 'promo_sent_to_admin')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(user_id, "btn_to_profile"), callback_data="profile")]])
    )

    admin_text = (
        f"🎁 **PROMOKOD FAOLLASHTIRILDI!** 🔔\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **{message.from_user.full_name}**\n"
        f"🔗 @{message.from_user.username}\n"
        f"🆔 `{user_id}`\n"
        f"🔖 `/{user['klent_code']}`\n\n"
        f"🎁 Promokod: `{promo_code_found}`\n"
        f"💰 **{format_money(promo_amount)} so'm**"
    )
    await message.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")


# ==================== TOP UP ====================
@router.callback_query(F.data == "top_up")
async def top_up_balance(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    text = f"{t(user_id, 'topup_title')}\n━━━━━━━━━━━━━━━━━━━━\n\n{t(user_id, 'topup_desc')}\n\n{t(user_id, 'topup_min')}"
    kb = [
        [InlineKeyboardButton(text="💵 5 000", callback_data="amount_5000"),
         InlineKeyboardButton(text="💵 10 000", callback_data="amount_10000")],
        [InlineKeyboardButton(text="💵 20 000", callback_data="amount_20000"),
         InlineKeyboardButton(text="💵 30 000", callback_data="amount_30000")],
        [InlineKeyboardButton(text="💵 50 000", callback_data="amount_50000"),
         InlineKeyboardButton(text="💵 100 000", callback_data="amount_100000")],
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
        await safe_edit(callback.message,
            f"{t(user_id, 'custom_amount_title')}\n\n{t(user_id, 'custom_amount_desc')}\n{t(user_id, 'custom_amount_example')}",
            cancel_button(user_id))
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
    amount = parse_amount(message.text)
    if amount is None or amount <= 0:
        await message.answer(t(user_id, "only_number"))
        return
    if amount < MIN_TOPUP:
        await message.answer(t(user_id, "min_sum"))
        return
    await state.update_data(selected_amount=amount)
    await send_card_details(message, amount, user_id)
    await state.set_state(BuyStates.waiting_for_receipt)


async def send_card_details(message, amount: int, user_id: int):
    text = (
        f"{t(user_id, 'card_title')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(user_id, 'card_amount')} **{format_money(amount)} so'm**\n\n"
        f"{t(user_id, 'card_pay')}\n"
        f"{t(user_id, 'card_number')} `{CARD_NUMBER}`\n"
        f"{t(user_id, 'card_holder')} `{CARD_HOLDER}`\n\n"
        f"{t(user_id, 'card_attention')}\n"
        f"{t(user_id, 'card_warn1')}\n{t(user_id, 'card_warn2')}\n\n"
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
            "balance": 0, "klent_code": f"klent{database['klent_counter']}",
            "used_promos": [], "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0, "lang": "uz",
        }

    klent_code = database["users"][user.id]["klent_code"]

    text = (
        f"{t(ADMIN_ID, 'new_receipt')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(ADMIN_ID, 'buyer')} **{user.full_name}**\n"
        f"🔗 @{user.username}\n"
        f"🆔 `{user.id}`\n"
        f"🔖 `/{klent_code}`\n\n"
        f"{t(ADMIN_ID, 'sum_label')} **{format_money(selected_amount)} so'm**"
    )
    kb = [[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_yes_{user.id}_{selected_amount}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"topup_no_{user.id}"),
    ]]
    await message.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")
    await message.answer(
        f"{t(user_id, 'receipt_sent')}\n\n{t(user_id, 'receipt_code')} `/{klent_code}`\n{t(user_id, 'receipt_wait')}"
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
            parse_mode="Markdown")
    except Exception:
        pass

    if user_id in database["users"]:
        database["users"][user_id]["balance"] += added_amount
        database["total_topups"] += added_amount
        save_user(user_id)
        save_stats("total_topups", database["total_topups"])

        await callback.bot.send_message(
            chat_id=user_id,
            text=f"{t(user_id, 'balance_added')}\n━━━━━━━━━━━━━━━━━━━━\n\n"
                 f"{t(user_id, 'balance_added_amount')} **{format_money(added_amount)} so'm**\n"
                 f"{t(user_id, 'balance_new')} **{format_money(database['users'][user_id]['balance'])} so'm**",
            parse_mode="Markdown")
    await callback.answer(t(ADMIN_ID, "approved").replace("**", ""))


@router.callback_query(F.data.startswith("topup_no_"))
async def topup_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[2])
    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + f"\n\n{t(ADMIN_ID, 'rejected')}",
            parse_mode="Markdown")
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
    await safe_edit(callback.message,
        f"{t(ADMIN_ID, 'admin_pass_title')}\n━━━━━━━━━━━━━━━━━━━━\n\n{t(ADMIN_ID, 'admin_pass_desc')}\n\n{t(ADMIN_ID, 'admin_pass_note')}",
        cancel_button(ADMIN_ID))
    await state.set_state(AdminStates.waiting_for_password)
    await callback.answer()


@router.message(AdminStates.waiting_for_password)
async def check_admin_password(message: Message, state: FSMContext):
    entered = message.text
    try:
        await message.delete()
    except Exception:
        pass
    if entered == ADMIN_PASSWORD:
        await state.clear()
        await show_admin_dashboard(message)
    else:
        err = await message.answer(t(ADMIN_ID, "admin_pass_wrong"))
        await asyncio.sleep(3)
        try:
            await err.delete()
        except Exception:
            pass


async def show_admin_dashboard(msg_or_cb, is_callback=False):
    total_users = len(database["users"])
    total_lots = len(database["lots"])
    total_stock = sum(get_lot_stock(l) for l in database["lots"].values())
    total_sold = sum(sum(1 for c in l["credentials"] if c["sold"]) for l in database["lots"].values())
    total_bal = sum(u["balance"] for u in database["users"].values())
    uptime = int(time.time() - bot_start_time)
    h = uptime // 3600
    m = (uptime % 3600) // 60

    stats_str = (
        f"{t(ADMIN_ID, 'admin_stats')}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(ADMIN_ID, 'admin_users_count')} **{total_users} ta**\n"
        f"{t(ADMIN_ID, 'admin_lots')} **{total_lots} ta**\n"
        f"📦 Mavjud: **{total_stock} ta**\n"
        f"✅ Sotilgan: **{total_sold} ta**\n"
        f"{t(ADMIN_ID, 'admin_total_bal')} **{format_money(total_bal)} so'm**\n"
        f"{t(ADMIN_ID, 'admin_total_sales')} **{format_money(database['total_sales'])} so'm**\n"
        f"{t(ADMIN_ID, 'admin_total_topups')} **{format_money(database['total_topups'])} so'm**\n"
        f"{t(ADMIN_ID, 'admin_uptime')} **{h}s {m}d**\n"
    )

    kb = [
        [InlineKeyboardButton(text="📊 To'liq statistika", callback_data="admin_full_stats")],
        [InlineKeyboardButton(text="📦 LOTLAR (Kanal)", callback_data="admin_lots_menu")],
        [InlineKeyboardButton(text="🎁 Promokodlar", callback_data="admin_promos_menu")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="📢 Rassilka", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="back_to_main")],
    ]
    text = f"{t(ADMIN_ID, 'admin_welcome')}\n\n{stats_str}"

    if is_callback:
        await safe_edit(msg_or_cb.message, text, kb)
    else:
        await msg_or_cb.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


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
    top = sorted(database["users"].items(), key=lambda x: x[1].get("total_spent", 0), reverse=True)[:5]
    top_str = "🏆 **TOP 5:**\n"
    if top:
        for i, (uid, u) in enumerate(top, 1):
            top_str += f"{i}. `{uid}` — {format_money(u.get('total_spent', 0))} so'm\n"
    else:
        top_str += "—\n"

    text = (
        f"📊 **TO'LIQ STATISTIKA**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Foydalanuvchilar: **{total_users}**\n"
        f"💰 Umumiy balans: **{format_money(total_balance)} so'm**\n"
        f"💸 Umumiy sarflangan: **{format_money(total_spent)} so'm**\n"
        f"💵 Sotuvlar: **{format_money(database['total_sales'])} so'm**\n"
        f"💳 To'ldirishlar: **{format_money(database['total_topups'])} so'm**\n\n{top_str}"
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
        flag = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}.get(u.get("lang", "uz"), "🇺🇿")
        text += f"{flag} `{uid}` — `/{u['klent_code']}` — **{format_money(u['balance'])} so'm**\n"
    if len(database["users"]) > 50:
        text += f"\n*... va yana {len(database['users']) - 50} ta*"
    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== LOT MENU ====================
@router.callback_query(F.data == "admin_lots_menu")
async def admin_lots_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    text = (
        f"📦 **LOTLAR MENYU**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Lot yaratib, ichiga email va parollarni qo'shing.\n\n"
        f"📊 Jami lotlar: **{len(database['lots'])} ta**"
    )
    kb = [
        [InlineKeyboardButton(text="➕ Yangi lot yaratish", callback_data="admin_add_lot")],
        [InlineKeyboardButton(text="📋 Lotlarni boshqarish", callback_data="admin_manage_lots")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== YANGI LOT ====================
@router.callback_query(F.data == "admin_add_lot")
async def admin_add_lot(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message,
        "📦 **YANGI LOT — 1/4**\n\nLot nomini kiriting:\n📌 *Misol: PUBG 30k lot*",
        cancel_button(ADMIN_ID, "admin_lots_menu"))
    await state.set_state(AdminStates.adding_lot_name)
    await callback.answer()


@router.message(AdminStates.adding_lot_name)
async def lot_name(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("❌ Bo'sh bo'lmasin!")
        return
    await state.update_data(lot_name=message.text.strip())
    await message.answer("📦 **2/4** — O'yin nomini kiriting:")
    await state.set_state(AdminStates.adding_lot_game)


@router.message(AdminStates.adding_lot_game)
async def lot_game(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("❌ Bo'sh bo'lmasin!")
        return
    await state.update_data(lot_game=message.text.strip())
    await message.answer("📦 **3/4** — Narxini kiriting (raqamda):")
    await state.set_state(AdminStates.adding_lot_price)


@router.message(AdminStates.adding_lot_price)
async def lot_price(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if amount is None or amount <= 0:
        await message.answer("❌ Faqat musbat raqam!")
        return
    await state.update_data(lot_price=str(amount))
    await message.answer("📦 **4/4** — Tavsif kiriting (yoki `-`):")
    await state.set_state(AdminStates.adding_lot_desc)


@router.message(AdminStates.adding_lot_desc)
async def lot_desc(message: Message, state: FSMContext):
    desc = message.text.strip() if message.text.strip() != "-" else "—"
    data = await state.get_data()

    database["lot_counter"] += 1
    lot_id = database["lot_counter"]

    database["lots"][lot_id] = {
        "name": data["lot_name"],
        "game": data["lot_game"],
        "price": data["lot_price"],
        "desc": desc,
        "credentials": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save_lot(lot_id)
    save_lot_counter()

    await state.clear()
    kb = [
        [InlineKeyboardButton(text="➕ Account qo'shish", callback_data=f"add_creds_{lot_id}")],
        [InlineKeyboardButton(text="📋 Lotni ko'rish", callback_data=f"view_lot_admin_{lot_id}")],
        [InlineKeyboardButton(text="📦 Lotlar menyu", callback_data="admin_lots_menu")],
    ]
    await message.answer(
        f"✅ **LOT YARATILDI!**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 ID: **#{lot_id}**\n📦 **{data['lot_name']}**\n"
        f"🎮 {data['lot_game']}\n💰 **{format_money(int(data['lot_price']))} so'm**\n"
        f"📝 {desc}\n\n⚠️ Endi accountlarni qo'shing!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown")


# ==================== ACCOUNT QO'SHISH ====================
@router.callback_query(F.data.startswith("add_creds_"))
async def add_creds_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return
    await state.update_data(lot_id=lid)
    await safe_edit(callback.message,
        f"📦 **{lot['name']}** — ACCOUNT QO'SHISH\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Har biri **yangi qatorda**: `email:parol`\n\n"
        f"📌 Misol:\n`user1@gmail.com:parol123`\n`user2@gmail.com:parol456`\n\n"
        f"📊 Hozirgi stock: **{get_lot_stock(lot)} ta**",
        cancel_button(ADMIN_ID, f"view_lot_admin_{lid}"))
    await state.set_state(AdminStates.adding_credentials_to_lot)
    await callback.answer()


@router.message(AdminStates.adding_credentials_to_lot)
async def add_creds_process(message: Message, state: FSMContext):
    data = await state.get_data()
    lid = data.get("lot_id")
    lot = database["lots"].get(lid)
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

        # Bir xil emailni tekshirish
        exists = False
        for ol in database["lots"].values():
            for c in ol["credentials"]:
                if c["email"].lower() == email.lower():
                    exists = True
                    break
            if exists:
                break
        if exists:
            errors.append(f"{line} (mavjud)")
            continue

        lot["credentials"].append({
            "email": email, "password": password,
            "sold": False, "sold_to": None, "sold_at": None,
        })
        added += 1

    save_lot(lid)
    await state.clear()

    stock = get_lot_stock(lot)
    text = f"✅ **{added} ta account qo'shildi!**\n━━━━━━━━━━━━━━━━━━━━\n\n📦 **{lot['name']}**\n📊 Jami stock: **{stock} ta**\n"
    if errors:
        text += f"\n⚠️ **Xatolar ({len(errors)}):**\n"
        for e in errors[:10]:
            text += f"• `{e}`\n"

    kb = [
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data=f"add_creds_{lid}")],
        [InlineKeyboardButton(text="📋 Lotni ko'rish", callback_data=f"view_lot_admin_{lid}")],
        [InlineKeyboardButton(text="📦 Lotlar menyu", callback_data="admin_lots_menu")],
    ]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


# ==================== LOTLARNI BOSHQARISH ====================
@router.callback_query(F.data == "admin_manage_lots")
async def admin_manage_lots(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not database["lots"]:
        await safe_edit(callback.message, "⚠️ Hozircha lotlar yo'q.",
            [
                [InlineKeyboardButton(text="➕ Yangi lot yaratish", callback_data="admin_add_lot")],
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_lots_menu")],
            ])
        await callback.answer()
        return
    kb = []
    for lid, lot in database["lots"].items():
        stock = get_lot_stock(lot)
        total = len(lot["credentials"])
        status = "🟢" if stock > 0 else "🔴"
        kb.append([InlineKeyboardButton(
            text=f"{status} #{lid} {lot['name']} — 📦 {stock}/{total}",
            callback_data=f"view_lot_admin_{lid}")])
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
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return
    stock = get_lot_stock(lot)
    total = len(lot["credentials"])
    sold = total - stock
    text = (
        f"📦 **{lot['name']}**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 **#{lid}**\n🎮 {lot.get('game', '—')}\n"
        f"💰 **{format_money(int(lot['price']))} so'm**\n"
        f"📝 {lot.get('desc', '—')}\n"
        f"📅 {lot.get('created_at', '—')}\n\n"
        f"📊 **STATISTIKA:**\n"
        f"📦 Jami: **{total} ta**\n🟢 Mavjud: **{stock} ta**\n✅ Sotilgan: **{sold} ta**\n"
    )
    kb = [
        [InlineKeyboardButton(text="➕ Account qo'shish", callback_data=f"add_creds_{lid}")],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_lot_{lid}")],
        [InlineKeyboardButton(text="👁 Mavjud accountlar", callback_data=f"show_creds_{lid}")],
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
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return
    available = [c for c in lot["credentials"] if not c["sold"]]
    if not available:
        await safe_edit(callback.message, "⚠️ Mavjud account yo'q!",
            [
                [InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"add_creds_{lid}")],
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"view_lot_admin_{lid}")],
            ])
        await callback.answer()
        return
    text = f"👁 **{lot['name']}** — **{len(available)} ta**\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for c in available[:50]:
        text += f"• `{c['email']}:{c['password']}`\n"
    if len(available) > 50:
        text += f"\n*... va yana {len(available) - 50} ta*"
    kb = [
        [InlineKeyboardButton(text="🗑 Sotilmaganlarini o'chirish", callback_data=f"clear_creds_{lid}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"view_lot_admin_{lid}")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("clear_creds_"))
async def clear_creds(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return
    before = len(lot["credentials"])
    lot["credentials"] = [c for c in lot["credentials"] if c["sold"]]
    after = len(lot["credentials"])
    removed = before - after
    save_lot(lid)
    await callback.answer(f"✅ {removed} ta o'chirildi!", show_alert=True)
    await view_lot_admin(callback)


# ==================== TAHRIRLASH ====================
@router.callback_query(F.data.startswith("edit_lot_"))
async def edit_lot_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return
    text = f"✏️ **{lot['name']}** — TAHRIRLASH\n━━━━━━━━━━━━━━━━━━━━\n\nQaysi maydon?"
    kb = [
        [InlineKeyboardButton(text=f"🏷 Nomi: {lot['name']}", callback_data=f"edit_field_{lid}_name")],
        [InlineKeyboardButton(text=f"🎮 O'yin: {lot.get('game', '—')}", callback_data=f"edit_field_{lid}_game")],
        [InlineKeyboardButton(text=f"💰 Narxi: {format_money(int(lot['price']))} so'm", callback_data=f"edit_field_{lid}_price")],
        [InlineKeyboardButton(text=f"📝 Tavsif: {lot.get('desc', '—')[:30]}", callback_data=f"edit_field_{lid}_desc")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"view_lot_admin_{lid}")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_field_"))
async def edit_lot_field(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split("_")
    lid = int(parts[2])
    field = parts[3]
    lot = database["lots"].get(lid)
    if not lot:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
        return

    names = {"name": "nomini", "game": "o'yin nomini", "price": "narxini (raqamda)", "desc": "tavsifini"}
    await state.update_data(edit_lot_id=lid, edit_field=field)

    if field == "name":
        await state.set_state(AdminStates.editing_lot_name)
    elif field == "game":
        await state.set_state(AdminStates.editing_lot_game)
    elif field == "price":
        await state.set_state(AdminStates.editing_lot_price)
    elif field == "desc":
        await state.set_state(AdminStates.editing_lot_desc)

    await safe_edit(callback.message, f"✏️ **{lot['name']}** — {names.get(field, field)} kiriting:",
        cancel_button(ADMIN_ID, f"view_lot_admin_{lid}"))
    await callback.answer()


@router.message(AdminStates.editing_lot_name)
async def edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lid = data["edit_lot_id"]
    lot = database["lots"].get(lid)
    if not lot:
        await state.clear()
        return
    val = message.text.strip()
    if not val:
        await message.answer("❌ Bo'sh bo'lmasin!")
        return
    lot["name"] = val
    save_lot(lid)
    await state.clear()
    kb = [[InlineKeyboardButton(text="⬅️ Lotga qaytish", callback_data=f"view_lot_admin_{lid}")]]
    await message.answer(f"✅ Nom o'zgartirildi: **{val}**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.message(AdminStates.editing_lot_game)
async def edit_game(message: Message, state: FSMContext):
    data = await state.get_data()
    lid = data["edit_lot_id"]
    lot = database["lots"].get(lid)
    if not lot:
        await state.clear()
        return
    val = message.text.strip()
    if not val:
        await message.answer("❌ Bo'sh bo'lmasin!")
        return
    lot["game"] = val
    save_lot(lid)
    await state.clear()
    kb = [[InlineKeyboardButton(text="⬅️ Lotga qaytish", callback_data=f"view_lot_admin_{lid}")]]
    await message.answer(f"✅ O'yin: **{val}**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.message(AdminStates.editing_lot_price)
async def edit_price(message: Message, state: FSMContext):
    data = await state.get_data()
    lid = data["edit_lot_id"]
    lot = database["lots"].get(lid)
    if not lot:
        await state.clear()
        return
    amount = parse_amount(message.text)
    if amount is None or amount <= 0:
        await message.answer("❌ Faqat musbat raqam!")
        return
    lot["price"] = str(amount)
    save_lot(lid)
    await state.clear()
    kb = [[InlineKeyboardButton(text="⬅️ Lotga qaytish", callback_data=f"view_lot_admin_{lid}")]]
    await message.answer(f"✅ Narx: **{format_money(amount)} so'm**", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.message(AdminStates.editing_lot_desc)
async def edit_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    lid = data["edit_lot_id"]
    lot = database["lots"].get(lid)
    if not lot:
        await state.clear()
        return
    val = message.text.strip()
    lot["desc"] = val if val != "-" else "—"
    save_lot(lid)
    await state.clear()
    kb = [[InlineKeyboardButton(text="⬅️ Lotga qaytish", callback_data=f"view_lot_admin_{lid}")]]
    await message.answer(f"✅ Tavsif o'zgartirildi!", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.callback_query(F.data.startswith("delete_lot_"))
async def delete_lot(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    lid = int(callback.data.split("_")[2])
    if lid in database["lots"]:
        del database["lots"][lid]
        delete_lot_db(lid)
        await callback.answer("✅ Lot o'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
    await admin_manage_lots(callback)


# ==================== PROMOKODLAR ====================
@router.callback_query(F.data == "admin_promos_menu")
async def admin_promos_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    text = f"🎁 **PROMOKODLAR**\n━━━━━━━━━━━━━━━━━━━━\n\n📊 Jami: **{len(database['promos'])} ta**"
    if database["promos"]:
        text += "\n\n📋 **Mavjud:**\n"
        for code, p in database["promos"].items():
            used = p.get("used_count", 0)
            limit = p.get("limit", 0)
            lt = "∞" if limit == 0 else str(limit)
            text += f"• `{code}` — {format_money(p['amount'])} so'm ({used}/{lt})\n"
    kb = [
        [InlineKeyboardButton(text="➕ Yangi promokod", callback_data="admin_add_promo")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data="admin_delete_promo_menu")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")],
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "admin_add_promo")
async def admin_add_promo(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "🎁 **YANGI PROMOKOD**\n\nPromokod nomini kiriting:\n📌 *Misol: alone*",
        cancel_button(ADMIN_ID, "admin_promos_menu"))
    await state.set_state(AdminStates.waiting_for_promo_code)
    await callback.answer()


@router.message(AdminStates.waiting_for_promo_code)
async def promo_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if not code:
        await message.answer("❌ Bo'sh bo'lmasin!")
        return
    if code in database["promos"]:
        await message.answer("⚠️ Bu promokod mavjud! Boshqa nom:")
        return
    await state.update_data(promo_code=code)
    await message.answer("💰 Qiymatini kiriting (so'mda):")
    await state.set_state(AdminStates.waiting_for_promo_amount)


@router.message(AdminStates.waiting_for_promo_amount)
async def promo_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if amount is None or amount <= 0:
        await message.answer("❌ Faqat musbat raqam!")
        return
    await state.update_data(promo_amount=amount)
    await message.answer("🔢 Limit (0 = cheksiz):")
    await state.set_state(AdminStates.waiting_for_promo_limit)


@router.message(AdminStates.waiting_for_promo_limit)
async def promo_limit(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return
    data = await state.get_data()
    code = data["promo_code"]
    database["promos"][code] = {
        "amount": data["promo_amount"],
        "limit": int(message.text),
        "used_count": 0,
    }
    save_promo(code)
    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Promokodlar menyu", callback_data="admin_promos_menu")]]
    lt = "cheksiz" if int(message.text) == 0 else f"{message.text} ta"
    await message.answer(
        f"✅ **PROMOKOD YARATILDI!**\n\n🎁 `{code}`\n💰 **{format_money(data['promo_amount'])} so'm**\n🔢 **{lt}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.callback_query(F.data == "admin_delete_promo_menu")
async def admin_delete_promo_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    if not database["promos"]:
        await safe_edit(callback.message, "⚠️ Promokodlar yo'q.", back_button(ADMIN_ID, "admin_promos_menu"))
        await callback.answer()
        return
    kb = [[InlineKeyboardButton(text=f"🗑 {code}", callback_data=f"delete_promo_{code}")] for code in database["promos"].keys()]
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_promos_menu")])
    await safe_edit(callback.message, "🗑 **Qaysi promokodni o'chirish?**", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_promo_"))
async def delete_promo(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    code = callback.data.replace("delete_promo_", "")
    if code in database["promos"]:
        del database["promos"][code]
        delete_promo_db(code)
        await callback.answer(f"✅ {code} o'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
    await admin_delete_promo_menu(callback)


# ==================== RASILKA ====================
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message,
        "📢 **RASSILKA**\n\nBarcha foydalanuvchilarga xabar:\n\n📌 *Matn, rasm yoki video*\n📌 *Misol: randomlar sotuvda*",
        cancel_button(ADMIN_ID, "admin_panel_back"))
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast)
async def broadcast_send(message: Message, state: FSMContext):
    await state.clear()
    count = 0
    failed = 0
    for uid in list(database["users"].keys()):
        try:
            await message.send_copy(chat_id=uid)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **RASSILKA TUGADI!**\n\n✔️ Yuborildi: **{count}**\n❌ Xato: **{failed}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


# ==================== /klent va /user ====================
@router.message(F.text.startswith("/klent"))
async def admin_klent(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply(
            "⚠ **Format:**\n• `/klent1 +10.000`\n• `/klent1 -10.000`\n• `/klent1 Salom`\n• `/klent1 email:parol`",
            parse_mode="Markdown")
        return

    code_input = parts[0][1:]
    body = parts[1].strip()

    target_id = None
    target_data = None
    for uid, udata in database["users"].items():
        if udata["klent_code"] == code_input:
            target_id = uid
            target_data = udata
            break

    if not target_id:
        await message.reply(f"❌ Topilmadi: `/{code_input}`", parse_mode="Markdown")
        return

    if body.startswith("+") or body.startswith("-"):
        amount = parse_amount(body)
        if amount is None or amount == 0:
            await message.reply("❌ Summani to'g'ri kiriting!")
            return
        target_data["balance"] += amount
        new_bal = target_data["balance"]
        save_user(target_id)
        await message.reply(
            f"✅ `/{code_input}`: **{amount:+,} so'm**\n💰 Yangi: **{format_money(new_bal)} so'm**",
            parse_mode="Markdown")
        try:
            await message.bot.send_message(chat_id=target_id,
                text=f"{t(target_id, 'balance_changed')}\n\n"
                     f"{t(target_id, 'balance_change')} **{amount:+,} so'm**\n"
                     f"{t(target_id, 'balance_current')} **{format_money(new_bal)} so'm**",
                parse_mode="Markdown")
        except Exception:
            pass
        return

    if ":" in body:
        try:
            await message.bot.send_message(chat_id=target_id,
                text=f"🎁 **SIZNING AKKOUNTINGIZ!** 🔑\n━━━━━━━━━━━━━━━━━━━━\n\n📧 `{body}`\n\n⚠️ *Hech kimga bermang!*",
                parse_mode="Markdown")
            await message.reply(f"✅ Akkaunt `/{code_input}` ga yuborildi!")
        except Exception as e:
            await message.reply(f"❌ {e}")
        return

    try:
        await message.bot.send_message(chat_id=target_id,
            text=f"{t(target_id, 'msg_from_admin')}\n\n{body}", parse_mode="Markdown")
        await message.reply(f"✅ Xabar `/{code_input}` ga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ {e}")


@router.message(F.text.startswith("/user"))
async def admin_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.reply("⚠ Format: `/user 123456789 +10.000`", parse_mode="Markdown")
        return

    target_id = int(parts[1])
    body = parts[2].strip()

    if target_id not in database["users"]:
        await message.reply("❌ Topilmadi!")
        return

    target_data = database["users"][target_id]

    if body.startswith("+") or body.startswith("-"):
        amount = parse_amount(body)
        if amount is None or amount == 0:
            await message.reply("❌ Summani to'g'ri kiriting!")
            return
        target_data["balance"] += amount
        new_bal = target_data["balance"]
        save_user(target_id)
        await message.reply(f"✅ ID `{target_id}`: **{amount:+,} so'm**\n💰 **{format_money(new_bal)} so'm**", parse_mode="Markdown")
        try:
            await message.bot.send_message(chat_id=target_id,
                text=f"{t(target_id, 'balance_changed')}\n\n"
                     f"{t(target_id, 'balance_change')} **{amount:+,} so'm**\n"
                     f"{t(target_id, 'balance_current')} **{format_money(new_bal)} so'm**",
                parse_mode="Markdown")
        except Exception:
            pass
        return

    if ":" in body:
        try:
            await message.bot.send_message(chat_id=target_id,
                text=f"🎁 **SIZNING AKKOUNTINGIZ!** 🔑\n━━━━━━━━━━━━━━━━━━━━\n\n📧 `{body}`",
                parse_mode="Markdown")
            await message.reply(f"✅ Akkaunt `{target_id}` ga yuborildi!")
        except Exception as e:
            await message.reply(f"❌ {e}")
        return

    try:
        await message.bot.send_message(chat_id=target_id, text=f"{t(target_id, 'msg_from_admin')}\n\n{body}", parse_mode="Markdown")
        await message.reply(f"✅ Xabar yuborildi!")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ==================== BOTNI ISHGA TUSHIRISH ====================
async def set_bot_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 Asosiy menyu"),
        BotCommand(command="lang", description="🌐 Til / Язык / Language"),
        BotCommand(command="help", description="ℹ️ Yordam"),
    ])


@router.message(Command("lang"))
async def cmd_lang(message: Message):
    uid = message.from_user.id
    await message.answer(t(uid, "choose_lang"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=lang_keyboard()), parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ **HELP**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "• `/start` — Asosiy menyu\n• `/lang` — Tilni o'zgartirish\n• `/help` — Yordam",
        parse_mode="Markdown")


async def main():
    init_supabase()
    load_database()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await set_bot_commands(bot)

    print("╔══════════════════════════════════╗")
    print("║   🚀 ALONE PUBG SHOP              ║")
    print("║   ✅ Ishga tushdi!                ║")
    print(f"║   👑 Admin: {ADMIN_ID}        ║")
    print(f"║   💾 Supabase: {'✅' if supabase else '❌'}             ║")
    print("╚══════════════════════════════════╝")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
