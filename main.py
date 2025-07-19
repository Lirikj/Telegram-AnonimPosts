import re 
import time
import threading
import requests
from pay import premium_users, gift_func
from admin_menu import admin_window
from config import bot, CHANNEL_developers, CHANNEL_osn, CHANNEL_osn_thread, admin
from telebot import types 
from markup import apply_markup
from commands import start_message, info
from ad import send_advertisement
from baza import ( is_timer_enabled, is_ban, get_user_emoji, is_premium_enabled, init_db, init_ad_db, remove_old_ads_from_db, start_premium_checker, get_ghost_state, count_post_stats)
from moderator import chat_with_gpt



EMOJI_RE = re.compile(r'^([\U0001F300-\U0001FAFF]+)\s*(.*)')

last_message_time = {}
old_message = {}
edit_message_data = {}
delete_message_data = {}
current_ad_index = 0  
user_settings = {}  


@bot.message_handler(commands=['start', 'st', 'update'])
def get_start_message(message):
    start_message(message)


@bot.message_handler(commands=['info']) 
def get_info(message):
    info(message)


@bot.message_handler(commands=['gift'])
def gift(message): 
    gift_func(message)


@bot.message_handler(commands=['admin']) 
def start_window_admin(message):
    admin_window(message)


@bot.message_handler(commands=['premium'])
def get_premium_users(message):
    premium_users(message)


def get_user(message):
    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ''
    user_emoji = get_user_emoji(user_id)
    ghost_state = get_ghost_state(user_id)
    username = user.username
    is_enabled, days_left = is_premium_enabled(user_id)
    return user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left


@bot.message_handler(content_types=['text'], func=lambda message: message.chat.id == message.from_user.id)
def echo_message(message):
    user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)
    enable_markup = apply_markup()

    try:    
        if message.text == '🌟Premium':
            premium_users(message) 
        elif message.text == '📕menu' or message.text == "📕info":
            info(message)
        elif message.text == '↩️Отмена':
            start_message(message)
        else:
            m = EMOJI_RE.match(message.text)
            if m:
                leading_emojis, rest = m.groups()
            else: 
                leading_emojis, rest = user_emoji, message.text

            if ghost_state == 0:
                if is_enabled:
                    bot.send_message(CHANNEL_developers, f"💬Новое сообщение💬\n🌟Премиум активирован\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{message.text}", parse_mode="HTML")
                else:
                    bot.send_message(CHANNEL_developers, f"💬Новое сообщение💬\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{message.text}", parse_mode="HTML")

            if is_ban(user_id): 
                bot.send_message(message.chat.id, '⛔️Вы забанены⛔️') 
                return  
            
            # if chat_with_gpt(message.text) == 'False':
            #     bot.send_message(message.chat.id, '❌Сообщение нарушает правила')
            #     return

            if is_enabled: 
                sent_message = bot.send_message(CHANNEL_osn, f"{leading_emojis}:{rest} \n\n"
                                                            "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML", disable_web_page_preview=True)
                markup = types.InlineKeyboardMarkup()
                pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
                edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{sent_message.message_id}')
                deleate_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
                markup.add(pin_button, edit_button, deleate_button)
                
                bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
            else:
                
                current_time = time.time()
                if is_timer_enabled(user_id):
                    if user_id in last_message_time:
                        last_message_time_user = last_message_time[user_id]
                        if current_time - last_message_time_user < 60:
                            bot.reply_to(message, "Подождите минуту.", reply_markup=enable_markup)
                            return
                last_message_time[user_id] = current_time
                
                sent_message = bot.send_message(CHANNEL_osn, f"💌:{message.text} \n\n"
                                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML", disable_web_page_preview=True)
                bot.reply_to(message, '✅Опубликовано')
                send_advertisement(bot, message)
                        
    except Exception as e:
        print(f"Ошибка в echo_message: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в echo_message: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка отправки сообщения. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.message_handler(content_types=['voice'], func=lambda message: message.chat.id == message.from_user.id)
def handle_voice_message(message):
    try:
        user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)
        enable_markup = apply_markup()

        file_info = bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        downloaded_file_voice = bot.download_file(file_path)


        if ghost_state == 0:
            if is_enabled:
                bot.send_voice(CHANNEL_developers, downloaded_file_voice, caption=f"💬Новое сообщение💬\n🌟Премиум активирован\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}",  parse_mode="HTML")
            else:
                bot.send_voice(CHANNEL_developers, downloaded_file_voice, caption=f"💬Новое сообщение💬\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}",  parse_mode="HTML")

        if is_ban(user_id): 
            bot.send_message(message.chat.id, '⛔️Вы забанены⛔️') 
            return 

        if is_enabled:
            sent_message = bot.send_voice(CHANNEL_osn, downloaded_file_voice, caption=f'{user_emoji}:аудиосообщение \n\n'
                                    "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")

            markup = types.InlineKeyboardMarkup()
            pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
            deleate_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
            markup.add(pin_button, deleate_button)

            bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
        else:
            current_time = time.time()
            if is_timer_enabled(user_id):
                if user_id in last_message_time:
                    last_message_time_user = last_message_time[user_id]
                    if current_time - last_message_time_user < 60:
                        bot.reply_to(message, "Подождите минуту.", reply_markup = enable_markup)
                        return
            last_message_time[user_id] = current_time

            bot.send_voice(CHANNEL_osn, downloaded_file_voice, caption='💌:аудиосообщение \n\n'
                                    "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
            bot.reply_to(message, '✅Опубликовано')
            send_advertisement(bot, message)

    except Exception as e:
        print(f"Ошибка в handle_voice_message: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в handle_voice_message: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка отправки аудиосообщения. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id == message.from_user.id)
def handle_photo_message(message):
    try:
        user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)
        enable_markup = apply_markup()

        downloaded_file_photo = message.photo[-1].file_id
        caption = message.caption

        if ghost_state == 0:
            if is_enabled:
                bot.send_photo(CHANNEL_developers, downloaded_file_photo, caption=f"💬Новое сообщение💬\n🌟Премиум активирован\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{caption}", parse_mode="HTML")
            else:
                bot.send_photo(CHANNEL_developers, downloaded_file_photo, caption=f"💬Новое сообщение💬\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{caption}", parse_mode="HTML")

        if is_ban(user_id): 
            bot.send_message(message.chat.id, '⛔️Вы забанены⛔️') 
            return  
        
        if is_enabled:
            if caption:
                # if chat_with_gpt(caption) == 'False':
                #     bot.send_message(message.chat.id, '❌Сообщение не прошло модерацию. Попробуйте изменить текст и отправить снова.')
                #     return
                
                m = EMOJI_RE.match(caption)
                if m:
                    leading_emojis, rest = m.groups()
                else:
                    leading_emojis, rest = user_emoji, caption

                sent_message = bot.send_photo(CHANNEL_osn, downloaded_file_photo, caption=f"{leading_emojis}:{rest} \n\n"
                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
                markup = types.InlineKeyboardMarkup()
                pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
                edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{sent_message.message_id}')
                deleate_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
                markup.add(pin_button, edit_button, deleate_button)
                bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
            else:
                sent_message = bot.send_photo(CHANNEL_osn, downloaded_file_photo, caption=f"{user_emoji}:анонимное фото \n\n"
                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")

                markup = types.InlineKeyboardMarkup()
                pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
                deleate_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
                markup.add(pin_button, deleate_button)
                bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
        else:
            current_time = time.time()
            if is_timer_enabled(user_id):
                if user_id in last_message_time:
                    last_message_time_user = last_message_time[user_id]
                    if current_time - last_message_time_user < 60:
                        bot.reply_to(message, "Подождите минуту.", reply_markup=enable_markup)
                        return
            last_message_time[user_id] = current_time

            if caption:
                bot.send_photo(CHANNEL_osn, downloaded_file_photo, caption=f"💌:{caption} \n\n"
                                    "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
                bot.reply_to(message, '✅Опубликовано')
            else:
                bot.send_photo(CHANNEL_osn, downloaded_file_photo, caption="💌:анонимное фото \n\n"
                                    "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
                bot.reply_to(message, '✅Опубликовано')
            send_advertisement(bot, message)

    except Exception as e:
        print(f"Ошибка в handle_photo_message: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в handle_photo_message: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка отправки фото. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.message_handler(content_types=['video_note'], func=lambda message: message.chat.id == message.from_user.id)
def handle_video_note_message(message):
    try:
        user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)
        enable_markup = apply_markup()

        downloaded_file_note = message.video_note.file_id

        if ghost_state == 0:
            if is_enabled:
                bot.send_message(CHANNEL_developers, f"💬Новое сообщение💬\n🌟Премиум активирован\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}", parse_mode="HTML")
            else:
                bot.send_message(CHANNEL_developers, f"💬Новое сообщение💬\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}", parse_mode="HTML")
            bot.send_video_note(CHANNEL_developers, downloaded_file_note)

        current_time = time.time()
        user_emoji = get_user_emoji(user_id)

        if is_ban(user_id): 
            bot.send_message(message.chat.id, '⛔️Вы забанены⛔️') 
            return 
        
        if is_enabled:
            sent_message = bot.send_video_note(CHANNEL_osn, downloaded_file_note)

            markup = types.InlineKeyboardMarkup()
            pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
            delete_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
            markup.add(pin_button, delete_button)

            bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
        else:
            current_time = time.time()
            if is_timer_enabled(user_id):
                if user_id in last_message_time:
                    last_message_time_user = last_message_time[user_id]
                    if current_time - last_message_time_user < 60:
                        bot.reply_to(message, "Подождите минуту.", reply_markup=enable_markup)
                        return
            last_message_time[user_id] = current_time

            bot.send_video_note(CHANNEL_osn, downloaded_file_note)
            bot.reply_to(message, '✅Опубликовано')
            send_advertisement(bot, message)

    except Exception as e:
        print(f"Ошибка в handle_video_note_message: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в handle_video_note_message: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка отправки кружочка. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.message_handler(content_types=['video'], func=lambda message: message.chat.id == message.from_user.id)
def handle_video_message(message):
    try:
        user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)
        enable_markup = apply_markup()

        downloaded_file_video = message.video.file_id
        caption = message.caption


        if ghost_state == 0:
            if is_enabled:
                bot.send_video(CHANNEL_developers, downloaded_file_video, caption=f"💬Новое сообщение💬\n🌟Премиум активирован\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{caption}", parse_mode="HTML")
            else:
                bot.send_video(CHANNEL_developers, downloaded_file_video, caption=f"💬Новое сообщение💬\n🆔{user_id}\n<a href='tg://openmessage?user_id={user_id}'>🪪{first_name} {last_name}</a>\n👤@{username}\n----------------------\n💌{caption}", parse_mode="HTML")

        if is_ban(user_id): 
            bot.send_message(message.chat.id, '⛔️Вы забанены⛔️') 
            return 
            
        if is_enabled:
            leading_emojis = user_emoji  
            rest = caption or "анонимное видео"
            if caption:                    
                m = EMOJI_RE.match(caption)
                if m:
                    leading_emojis, rest = m.groups()
                else:
                    leading_emojis, rest = user_emoji, caption
            sent_message = bot.send_video(CHANNEL_osn, downloaded_file_video, caption=f"{leading_emojis}:{rest} \n\n"
                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")

            markup = types.InlineKeyboardMarkup()
            pin_button = types.InlineKeyboardButton('📌', callback_data=f'pin_{sent_message.message_id}')
            edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{sent_message.message_id}')
            deleate_button = types.InlineKeyboardButton('🚫', callback_data=f'delete.message_{sent_message.message_id}')
            markup.add(pin_button, edit_button, deleate_button)

            bot.reply_to(message, '✅Опубликовано', reply_markup=markup)
        else:
            current_time = time.time()
            if is_timer_enabled(user_id):
                if user_id in last_message_time:
                    last_message_time_user = last_message_time[user_id]
                    if current_time - last_message_time_user < 60:                              
                        bot.reply_to(message, "Подождите минуту.", reply_markup=enable_markup)
                        return
            last_message_time[user_id] = current_time
            if caption:
                bot.send_video(CHANNEL_osn, downloaded_file_video, caption=f"💌:{caption} \n\n"
                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
                bot.reply_to(message, '✅Опубликовано')
            else:
                bot.send_video(CHANNEL_osn, downloaded_file_video, caption="💌:анонимное видео \n\n"
                                        "<a href='t.me/Nurlatanonim_bot'>Отправить анонимное сообщение</a>", parse_mode="HTML")
                bot.reply_to(message, '✅Опубликовано')
            send_advertisement(bot, message)

    except Exception as e:
        print(f"Ошибка в handle_video_message: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в handle_video_message: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка отправки видео. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.message_handler(content_types=['poll'], func=lambda message: message.chat.id == message.from_user.id)
def recreate_poll(message):
    user, user_id, first_name, last_name, user_emoji, ghost_state, username, is_enabled, days_left = get_user(message)

    try:
        if is_enabled:
            poll = message.poll
            options_text = [option.text for option in poll.options]

            poll_kwargs = {
                'chat_id': CHANNEL_osn,
                'question': f"{user_emoji}:{poll.question}",
                'options': [option.text for option in poll.options],
                'is_anonymous': poll.is_anonymous,
                'allows_multiple_answers': poll.allows_multiple_answers,
                'type': poll.type  }

            if poll.type == 'quiz' and hasattr(poll, 'correct_option_id'):
                poll_kwargs['correct_option_id'] = poll.correct_option_id


            if hasattr(poll, 'open_period'):
                poll_kwargs['open_period'] = poll.open_period
            if hasattr(poll, 'close_date'):
                poll_kwargs['close_date'] = poll.close_date
            
            if ghost_state == 0:
                bot.send_message(CHANNEL_developers, f"💬Опрос💬\n🌟Премиум активирован\n🆔{user_id}\n[🪪{first_name} {last_name}](tg://openmessage?user_id={user_id})\n👤@{username}\n----------------------\n💌{poll.question}",  parse_mode="Markdown")
            bot.send_poll(**poll_kwargs)
            bot.reply_to(message, '✅Опубликовано')
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            on_premium_button = types.InlineKeyboardButton('Приобрести 🌟Anonka premium', callback_data='disable_ad') 
            markup.add(on_premium_button)
            bot.send_message(message.chat.id, '❌Создавать опросы можно только с 🌟Anonka premium', reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в recreate_poll: {e}")
        bot.send_message(CHANNEL_developers, f"Ошибка в recreate_poll: {e}", message_thread_id=CHANNEL_osn_thread)
        bot.send_message(message.chat.id, '😢ошибка создании опроса. Попробуйте снова\nЕсли снова вылезает ошибка свяжитесь с разработчиком @JonsonP')


@bot.callback_query_handler(func=lambda c: c.data.startswith('pin_'))
def pin(callback_query):
    try:
        message_id_to_pin = int(callback_query.data.split('_')[1])
        bot.pin_chat_message(CHANNEL_osn, message_id=message_id_to_pin)
        bot.send_message(callback_query.message.chat.id, "👌Сообщение закрепленно.")
    except Exception as e:
        bot.send_message(callback_query.message.chat.id, "Сообщение не найдено")


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('edit_'))
def edit(callback_query):
    try:
        message_id_to_edit = int(callback_query.data.split('_')[1])
        chat_id = callback_query.message.chat.id

        message_to_edit = bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_osn, message_id=message_id_to_edit)
        edit_message_data[callback_query.from_user.id] = {
            "message_id": message_id_to_edit,
            "message_type": message_to_edit.content_type,
            "media": message_to_edit.photo if message_to_edit.content_type == 'photo' else 
                    message_to_edit.video if message_to_edit.content_type == 'video' else None}

        bot.send_message(chat_id, '✏️Введите исправленный текст')
        bot.register_next_step_handler(callback_query.message, edit_message)
        
    except Exception as e:
        bot.send_message(callback_query.message.chat.id, "Не удалось обработать запрос")
        bot.send_message(CHANNEL_developers, f"Ошибка в edit: {e}", message_thread_id=CHANNEL_osn_thread)
        print(f"Ошибка в edit: {e}")


def edit_message(message):
    user_id = message.from_user.id
    user_emoji = get_user_emoji(user_id)
    text_edit = f'{user_emoji}✏️:{message.text}'
    message_data = edit_message_data.get(user_id)

    if message_data:
        try:
            message_type = message_data["message_type"]
            
            if message_type == 'text':
                bot.edit_message_text(
                    chat_id=CHANNEL_osn,
                    message_id=message_data["message_id"],
                    text=text_edit
                )
            elif message_type in ['photo', 'video']:
                bot.edit_message_caption(
                    chat_id=CHANNEL_osn,
                    message_id=message_data["message_id"],
                    caption=text_edit
                )

            bot.send_message(message.chat.id, "👌Сообщение отредактировано.")
            del edit_message_data[user_id]
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка при редактировании сообщения")
            bot.send_message(CHANNEL_developers, f"Ошибка в edit_message: {e}", message_thread_id=CHANNEL_osn_thread)
    else:
        bot.send_message(message.chat.id, "Не удалось найти сообщение для редактирования.")


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('delete.message_'))
def delete_message(callback_query):
    try:
        message_id_to_delete = int(callback_query.data.split('_')[1])
        delete_message_data[callback_query.from_user.id] = message_id_to_delete

        if message_id_to_delete:
            bot.delete_message(chat_id=CHANNEL_osn, message_id=message_id_to_delete)
            bot.send_message(callback_query.message.chat.id, "🗑️Сообщение удаленно.")
        else: 
            bot.send_message(callback_query.message.chat.id, 'Не удалось найти сообщение')

    except Exception as e:
        bot.send_message(callback_query.message.chat.id, "Не удалось обновить сообщение")
        bot.send_message(CHANNEL_developers, f"Ошибка в delete_message: {e}", message_thread_id=CHANNEL_osn_thread)
        print(f"Ошибка в delete_message: {e}")



@bot.callback_query_handler(func=lambda callback: callback.data == 'disable_ad') 
def off_ad(callback):
    try:
        premium_users(callback.message)
    except Exception as e:
        print(f"Ошибка при отправки кнопки отмены рекламы {e}") 


def run_stats_scheduler():
    while True:
        time.sleep(86400)  
        count_post_stats()


init_db()
init_ad_db()
remove_old_ads_from_db(bot, admin)


stats_thread = threading.Thread(target=run_stats_scheduler)
stats_thread.daemon = True
stats_thread.start()
thread = threading.Thread(target=start_premium_checker, daemon=True)
thread.start()



while True:
    try:
        bot.polling(none_stop=True, timeout=90)
    except requests.exceptions.ReadTimeout:
        print("⏳ ReadTimeout! Перезапускаю polling...")
        bot.send_message(CHANNEL_developers, "⏳ ReadTimeout! Перезапускаю polling...", message_thread_id=CHANNEL_osn_thread)
        time.sleep(5)  
    except Exception as e:
        bot.send_message(CHANNEL_developers, f"Ошибка в bot.polling: {e}", message_thread_id=CHANNEL_osn_thread)
        print(f"Ошибка в bot.polling: {e}")
        time.sleep(5)


