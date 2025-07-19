import sqlite3
from baza import is_timer_enabled, is_ban, deactivate_premium, get_usernames, set_timer, activate_premium, get_all_ads_from_db, delete_ad_from_db, ban_user, delete_user, add_ad_to_db, ghost_mode, delete_admin, is_admin 
from config import bot, CHANNEL_developers, CHANNEL_osn_thread 
from telebot import types 
from markup import build_admin_markup


def admin_window(message):
    user_id = message.from_user.id
    if user_id == 7135396517 or is_admin(user_id):
        markup = build_admin_markup(user_id)
        bot.send_message(message.chat.id, '📖admin-menu', reply_markup=markup)
    else:
        bot.reply_to(message, 'Иди нахуй, со своей командой')
        with open('gif.mp4', 'rb') as gif:
            bot.send_animation(message.chat.id, gif)


@bot.callback_query_handler(func=lambda call: call.data in ['timer', 'ghost'])
def handle_dynamic_buttons(call):
    user_id = call.from_user.id
    if call.data == 'timer':
        current_state = is_timer_enabled(user_id)
        if current_state:
            set_timer(user_id, 0)
        else:
            set_timer(user_id, 1)
    elif call.data == 'ghost':
        ghost_mode(user_id)
    new_markup = build_admin_markup(user_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=new_markup)
    bot.answer_callback_query(call.id)


def split_message(text, max_length=4096):
    lines = text.split('\n')
    messages = []
    current_message = ''
    
    for line in lines:
        if len(current_message) + len(line) + 1 > max_length:
            messages.append(current_message)
            current_message = line
        else:
            current_message += '\n' + line if current_message else line
    if current_message:
        messages.append(current_message)
    return messages


@bot.callback_query_handler(func=lambda callback: callback.data in ['users', 'allmessage', 'exit', 'timer', 'banuser', 'razban', 'premium', 'gift', 'adversing_adms', 'not_premium', 'message_for_user', 'ghost', 'add_admin', delete_admin]) 
def commandsadmin(callback):
    user_id = callback.from_user.id 

    if is_ban(user_id): 
        bot.send_message(callback.message.chat.id, '⛔️Вы забанены⛔️') 
    else: 
        if callback.data == 'users':
            usernames = get_usernames()
            if usernames:
                filtered_usernames = [f"{idx+1}. @{username.replace(' ', '')}" for idx, username in enumerate(usernames) if username]
                response = "\n".join(filtered_usernames)
                messages = split_message(response)
                
                for msg in messages:
                    bot.send_message(callback.message.chat.id, msg)
            else:
                bot.send_message(callback.message.chat.id, "No usernames found.")
        elif callback.data == 'allmessage':
            reklama(callback.message)
        elif callback.data == 'timer':
            current_state = is_timer_enabled(user_id)
            if current_state:
                set_timer(user_id, False)
            else:
                set_timer(user_id, True)
        elif callback.data == 'banuser':
            bot.send_message(callback.message.chat.id, 'Введи user_id')
            bot.register_next_step_handler(callback.message, ban) 
        elif callback.data == 'razban':
            bot.send_message(callback.message.chat.id, 'Введи user_id')
            bot.register_next_step_handler(callback.message, razban) 
        elif callback.data == 'premium':
            bot.send_message(callback.message.chat.id, 'Подписка активированна')
            activate_premium(user_id)
        elif callback.data == 'gift':
            bot.send_message(callback.message.chat.id, 'Введи user_id пользователя, которому хочешь подарить премку \n\nПодарить можно на 30, 90 и 365 дней \n(Вписывай через запятую, если не вписать количество дней, то подарок будет на 30 дней)')
            bot.register_next_step_handler(callback.message, gift_user) 
        elif callback.data == 'adversing_adms':
            bot.send_message(callback.message.chat.id,
                            "Фото и видео не поддерживаються \nЧтоб перейти на следующию строчку введите \\n") 
            bot.send_message(callback.message.chat.id, "Ваш текст:")
            bot.register_next_step_handler(callback.message, anonka_ad)
        elif callback.data == 'not_premium':
            bot.send_message(callback.message.chat.id, 'Введи id пользователя у которого хочешь отключить подписку')
            bot.register_next_step_handler(callback.message, deactivate_fuck)
        elif callback.data == 'message_for_user':
            bot.send_message(callback.message.chat.id, 'Введи id получателя и после зарятой сообщение')
            bot.register_next_step_handler(callback.message, id_message_for_user)
        elif callback.data == 'ghost':
            new_value = ghost_mode(callback.from_user.id)
            status = "включен" if new_value == 1 else "выключен"
            bot.send_message(callback.message.chat.id, f"Режим инкогнито {status}.")
        elif callback.data == 'add_admin':
            bot.send_message(callback.message.chat.id, 'Введи user_id админа, которого хочешь добавить')
            bot.register_next_step_handler(callback.message, add_admin_handler)
        elif callback.data == 'delete_admin':
            bot.send_message(callback.message.chat.id, 'Введи user_id админа, которого хочешь удалить')
            bot.register_next_step_handler(callback.message, delete_admin_handler)


def add_admin_handler(message):
    try:
        user_id = int(message.text)
        from baza import add_admin
        add_admin(user_id)
        bot.send_message(message.chat.id, f"Пользователь {user_id} добавлен в админы")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при добавлении: {e}")


def delete_admin_handler(message):
    try:
        user_id = int(message.text)
        from baza import delete_admin
        delete_admin(user_id)
        bot.send_message(message.chat.id, f"Пользователь {user_id} удален из админов")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при удалении: {e}")
            


def id_message_for_user(message):
    try:
        user_input = message.text
        recipient_id, text_message = user_input.split(',', 1)
        recipient_id = recipient_id.strip()  
        text_message = text_message.strip()  
        bot.send_message(recipient_id, text_message)
        bot.send_message(message.chat.id, f'Сообщение отправлено пользователю с ID {recipient_id}')
    except:
        bot.send_message(message.chat.id, 'Ошибка! Введи данные в формате: ID получателя, сообщение')


def deactivate_fuck(message):
    user_id = message.text
    deactivate_premium(user_id)
    bot.send_message(message.chat.id, 'Прощай, прощай премиум')


@bot.callback_query_handler(func=lambda callback: callback.data == 'all_adversting')
def show_all_ads(callback):
    ads = get_all_ads_from_db()
    
    if len(ads) == 0:
        bot.send_message(callback.message.chat.id, "На данный момент нет доступной рекламы.")
    else:
        for ad_id, ad_content in ads:
            markup = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton('🗑️trash', callback_data=f'delete_ad_{ad_id}')
            markup.add(delete_button)
            bot.send_message(callback.message.chat.id, ad_content, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_ad_'))
def handle_delete_ad(call):
    ad_id = int(call.data.split('_')[2])  
    delete_ad_from_db(ad_id) 
    bot.answer_callback_query(call.id, "Реклама удалена.")
    bot.delete_message(call.message.chat.id, call.message.message_id)


def ban(message):
    user_id = message.text 
    ban_user(user_id, False)
    bot.send_message(message.chat.id, 'Ура, пользователь заблокирован') 


def razban(message):
    user_id = message.text 
    ban_user(user_id, True)
    bot.send_message(message.chat.id, 'Пользователь разблокирован') 


def gift_user(message):
    try:
        parts = message.text.split(',', 1)
        if len(parts) == 2:
            user_id, days = parts[0].strip(), parts[1].strip()
            days = int(days)
            if days == 30 or days == 90 or days == 365:
                activate_premium(user_id, days)
                bot.send_message(user_id, f'🎁Вам подарили premium на {days} дней')
                bot.send_message(message.chat.id, 'Подарок отправлен')
            else: 
                bot.send_message(message.chat.id, 'Неверное количество дней')
        else:
            user_id = parts[0].strip()
            activate_premium(user_id)
            bot.send_message(user_id, '🎁Вам подарили premium на месяц')
            bot.send_message(message.chat.id, 'Подарок отправлен')
    except Exception as e:
        print(f"Ошибка при подарке премиума: {e}")
        bot.send_message(message.chat.id, 'пользователь не найден')


def reklama(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exit = types.KeyboardButton('👋🏻exit') 
    markup.add(exit)

    bot.send_message(message.chat.id, 'Ваще сообщение для пользователей:', reply_markup=markup)
    bot.register_next_step_handler(message, messageusersfree)


def messageusersfree(message):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute('SELECT user_id FROM users')
        user_ids = c.fetchall()
        for user_id in user_ids:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id[0], message.text, parse_mode="Markdown")
                elif message.content_type == 'photo':
                    bot.send_photo(user_id[0], message.photo[-1].file_id, caption=message.caption, parse_mode="Markdown")
                elif message.content_type == 'video':
                    bot.send_video(user_id[0], message.video.file_id, caption=message.caption, parse_mode="Markdown") 
            except Exception as e: 
                if e.result.status_code == 403:
                    print(f"Пользователь {user_id[0]} заблокировал бота. Удаляю из базы данных.")
                    delete_user(user_id[0])
                else:
                    print(f"Ошибка при отправке сообщения пользователю {user_id[0]}: {e}") 
        bot.send_message(message.chat.id, '👌Сообщение отправленно пользователям') 
    except sqlite3.Error as e:
        print(f"Ошибка при отправке сообщений: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка при отправке сообщений: {e}", message_thread_id=CHANNEL_osn_thread)
    finally:
        if conn:
            conn.close()
    


def anonka_ad(message):
    if message.content_type == 'text':
        ad_content = message.text
        add_ad_to_db(ad_content)  
        bot.send_message(message.chat.id, 'Реклама добавленна')
    else:
        bot.send_message(message.chat.id, 'Данный тип рекламы не поддерживается')