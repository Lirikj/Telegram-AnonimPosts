from config import bot
from baza import save_user_data, user_exists, get_posts_by_user
from telebot import types
from markup import markup_menu, build_admin_markup
from pay import premium_users



def start_message(message):
    user = message.from_user
    user_id = message.from_user.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    premium_button = types.KeyboardButton('🌟Premium')
    info = types.KeyboardButton('📕menu') 
    markup.add(premium_button, info)

    if not user_exists(user_id):
        bot.send_message(message.chat.id, '\nПродолжая пользоваться ботом вы соглашаетесь с пользовательскм соглашением \n   \nПользовательское соглашение разделе /info ')
        bot.send_message(message.chat.id , '👋Привет! Я бот @Nurlatanonim \n \nОтправьте мне сообщение, фото или видео, которое хотите анонимно опубликовать в канале.', reply_markup=markup)
        save_user_data(user) 
    else: 
        save_user_data(user) 
        bot.send_message(message.chat.id, '✍️Напиши сообщение и я его опубликую', reply_markup=markup)


def info(message):
    try:
        user_id = message.from_user.id
        markup = markup_menu(user_id)
        bot.send_message(message.chat.id, '📖Nurlatanonim menu', reply_markup=markup)
    except:
        bot.send_message(message.chat.id, 'ошибка 404') 



@bot.callback_query_handler(func=lambda callback: callback.data in ['info_func', 'admin_menu'])
def menu_buttons(callback):
    try:
        user_id = callback.message.from_user.id

        if callback.data == 'info_func':
            markup = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton('↪️вернуться в меню', callback_data='back_func') 
            markup.add(back_btn)
            bot.edit_message_text(
                chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                text="\n🤖версия бота 6.3 \n👨🏼‍💻developer - @JonsonP \n\nДля модерации контента используется языковая модель от OpenAI ChatGPT 4.1  \n\n<a href='https://telegra.ph/Soglashenie-o-polzovanii-Botom-09-05'>Пользовательское соглашение</a>",
                parse_mode="HTML", reply_markup=markup)
            
        elif callback.data == 'admin_menu':
            markup = build_admin_markup(user_id)
            bot.edit_message_text(
                chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                text='👨🏼‍💻admin-menu', reply_markup=markup)

    except: 
        bot.send_message(callback.message.chat.id, 'ошибка 404')



@bot.callback_query_handler(func=lambda callback: callback.data in ['back_func'])
def back_func(callback):
    try:
        user_id = callback.from_user.id
        markup = markup_menu(user_id)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='📖Nurlatanonim menu', reply_markup=markup)
    except:
        bot.send_message(callback.message.chat.id, 'ошибка 404') 


@bot.callback_query_handler(func=lambda callback: callback.data in ['disable_ad', 'apply'])
def off_ad(callback):
    try:
        premium_users(callback.message)
    except Exception as e:
        print(f"Ошибка при отправке кнопки отмены рекламы {e}")

