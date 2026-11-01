import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery

TOKEN = "9055119041:AAFRUIlISUHTM0XNUU-JY9Bws2MCwFPZ14M"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧁 Играть в Muffin Game", web_app=types.WebAppInfo(url="https://muffin331.github.io/Muffin_TgGames/"))],
        [InlineKeyboardButton(text="⭐ Купить монеты", callback_data="buy_coins"), InlineKeyboardButton(text="🎁 Кейсы с подарками", callback_data="cases")],
        [InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="promocode")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "💚 **Muffin Game** — твоя удача начинается здесь!\n\nВыбирай разделы ниже:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "buy_coins")
async def buy_coins_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 монет — 1 ⭐", callback_data="star_100")],
        [InlineKeyboardButton(text="500 монет — 5 ⭐", callback_data="star_500")],
        [InlineKeyboardButton(text="1000 монет — 10 ⭐", callback_data="star_1000")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_home")]
    ])
    await callback.message.edit_text("💰 **Покупка монет**\nВыбери пакет для игры:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("star_"))
async def process_star_purchase(callback: types.CallbackQuery):
    amount = callback.data.split("_")[1]
    prices = {"100": (1, "100 монет Muffin"), "500": (5, "500 монет Muffin"), "1000": (10, "1000 монет Muffin")}
    stars, title = prices[amount]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=title,
        description="Пополнение игрового баланса Muffin Game",
        payload=f"coins_{amount}",
        currency="XTR",
        prices=[LabeledPrice(label="Монеты", amount=stars)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    await message.answer("✅ Успешно! Монеты зачислены на твой баланс в Muffin Game.")

@dp.callback_query(F.data == "cases")
async def cases_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Кейс за 1 ⭐", callback_data="case_1")],
        [InlineKeyboardButton(text="📦 Кейс за 5 ⭐", callback_data="case_5")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_home")]
    ])
    await callback.message.edit_text("🎁 **Кейсы с подарками**\nВозможный приз: сердечко, роза или тортик Telegram!", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery):
    await callback.message.edit_text("💚 **Muffin Game** — твоя удача начинается здесь!\n\nВыбирай разделы ниже:", reply_markup=get_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "promocode")
async def promocode_info(callback: types.CallbackQuery):
    await callback.answer("Отправь промокод текстовым сообщением в чат!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
import json
from aiogram.filters import Command
from aiogram import types, F

# Твой личный ID администратора
ADMIN_ID = 1116150221

# Обработка нажатия кнопки "Забрать" в Mini App
@dp.message(F.web_app_data)
async def receive_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "claim_win":
            amount = data.get("amount", 0)
            
            # Здесь будет сохранение монет в базу данных для message.from_user.id
            
            await message.answer(f"🎉 Успешно! Ты забрал `{amount}` монет на свой баланс!")
    except Exception:
        await message.answer("⚠️ Ошибка при обработке наград из игры.")

# Открытие админ-панели (только для тебя)
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "👑 **Админ-панель Muffin Game**\n\n"
        "Команда для выдачи монет:\n"
        "`/give [ID_игрока] [сумма]`"
    )

# Выдача монет игроку через команду /give
@dp.message(Command("give"))
async def admin_give_coins(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Пример использования: `/give 123456789 500`")
        return
    
    target_user_id = args[1]
    amount = args[2]
    
    # Здесь логика начисления монет игроку в базу данных
    
    await message.answer(f"✅ Успешно! Игроку `{target_user_id}` начислено `{amount}` монет.")
    
    try:
        await bot.send_message(target_user_id, f"🎁 Администратор выдал тебе `{amount}` монет!")
    except Exception:
        pass
# Словарь для хранения промокодов (в памяти) или можешь сохранять их в базу данных
PROMO_CODES = {
    "START2026": 500,  # промокод: количество монет
    "BONUS": 1000
}

# Активация промокода игроком
@dp.message(Command("promo"))
async def activate_promo(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Введи промокод. Пример: `/promo START2026`")
        return
    
    code = args[1].upper()
    
    if code in PROMO_CODES:
        amount = PROMO_CODES[code]
        # Здесь добавь сохранение / зачисление монет в базу данных игроку message.from_user.id
        await message.answer(f"🎉 Промокод активирован! Тебе начислено `{amount}` монет.")
    else:
        await message.answer("❌ Неверный или уже истекший промокод.")

# Команда для тебя (админа), чтобы добавлять новые промокоды на лету
@dp.message(Command("addpromo"))
async def admin_add_promo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ Использование: `/addpromo [КОД] [сумма]`")
        return
    
    code = args[1].upper()
    try:
        amount = int(args[2])
        PROMO_CODES[code] = amount
        await message.answer(f"✅ Промокод `{code}` на `{amount}` монет успешно создан!")
    except ValueError:
        await message.answer("⚠️ Сумма должна быть числом.")
from aiogram.filters import Command
from aiogram import types, F
import json

ADMIN_ID = 1116150221  # Твой точный ID числом без кавычек

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    # Проверка ID
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет доступа к админ-панели.")
        return
    
    await message.answer(
        "👑 **Админ-панель Muffin Game**\n\n"
        "Команда для выдачи монет:\n"
        "`/give [ID_игрока] [сумма]`"
    )
