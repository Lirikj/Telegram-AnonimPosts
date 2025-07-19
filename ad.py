from baza import get_active_ads_from_db
from telebot import types
from config import bot
from pay import premium_users

current_ad_index = 0


def send_advertisement(bot, message):
    global current_ad_index
    active_ads = get_active_ads_from_db()
    if not active_ads:
        return
    if current_ad_index >= len(active_ads):
        current_ad_index = 0

    current_ad_content = active_ads[current_ad_index]
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        on_premium_button = types.InlineKeyboardButton('⛔️отключить рекламу⛔️', callback_data='disable_ad') 
        markup.add(on_premium_button)
        bot.send_message(message.chat.id, current_ad_content, reply_markup=markup) 
    except Exception as e:
        print(f"Ошибка при отправке рекламы: {e}")

    current_ad_index = (current_ad_index + 1) % len(active_ads) 
    


