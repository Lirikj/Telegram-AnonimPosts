import re
from baza import get_user_emoji, is_premium_enabled, update_user_emoji, activate_premium, resolve_username_to_id, get_user_custom_emoji, set_user_emoji
from config import bot 
from telebot import types
from telebot.types import LabeledPrice, ShippingOption

last_invoice = {}
gift_dict = {}

prices = [LabeledPrice(label="XTR", amount=50)]  
prices_premium = [LabeledPrice(label="XTR", amount=25)]  

prices_premium_month = [LabeledPrice(label="Premium на месяц", amount=15)]
prices_premium_3months = [LabeledPrice(label="Premium на 3 месяца", amount=40)]
prices_premium_year = [LabeledPrice(label="Premium на год", amount=150)]

shipping_options = [ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 50)),]


def premium_users(message):
    user_id = message.from_user.id
    user_emoji = get_user_emoji(user_id)
    is_enabled, days_left = is_premium_enabled(user_id)
    user_custom_emoji = get_user_custom_emoji(user_id)

    if is_enabled:
        markup = types.InlineKeyboardMarkup(row_width=2)
        choice = types.InlineKeyboardButton('💭Изменить эмодзи', callback_data='choice') 
        defalt = types.InlineKeyboardButton('🌟 по умолчанию', callback_data='defalt') 
        defalt_homeles = types.InlineKeyboardButton('💌 бедный эмодзи статус', callback_data='defalt_homeles')
        if user_custom_emoji is not None:
            custom_emoji = types.InlineKeyboardButton(user_custom_emoji, callback_data='custom_emoji_btn')
        new_custom_emoji = types.InlineKeyboardButton('➕ Добавить свой эмодзи', callback_data='new_custom_emoji_btn')

        
        if user_emoji == '🌟':
            markup.add(choice)
            markup.add(defalt_homeles)
            if user_custom_emoji is not None:
                markup.add(custom_emoji)
            markup.add(new_custom_emoji)
            bot.send_message(message.chat.id, f"Ваша подписка активна. Осталось {days_left} дней.\n\nУ вас стоит эмодзи статус по умолчанию", reply_markup=markup)
        elif user_emoji == '💌':
            markup.add(choice)
            markup.add(defalt)
            if user_custom_emoji is not None:
                markup.add(custom_emoji)
            markup.add(new_custom_emoji)
            bot.send_message(message.chat.id, f"Ваша подписка активна. Осталось {days_left} дней.\n\nВаш эмодзи {user_emoji}", reply_markup=markup)
        elif user_emoji == user_custom_emoji:
            markup.add(choice)
            markup.add(defalt)
            markup.add(defalt_homeles)
            markup.add(new_custom_emoji)
            bot.send_message(message.chat.id, f"Ваша подписка активна. Осталось {days_left} дней.\n\nВаш эмодзи {user_custom_emoji}", reply_markup=markup)
        else:
            markup.add(choice)
            markup.add(defalt)
            markup.add(defalt_homeles)
            if user_custom_emoji is not None:
                if user_custom_emoji != user_emoji:
                    custom_emoji = types.InlineKeyboardButton(user_custom_emoji, callback_data='custom_emoji_btn')
                    markup.add(custom_emoji)
            markup.add(new_custom_emoji)
            bot.send_message(message.chat.id, f"Ваша подписка активна. Осталось {days_left} дней.\n\nВаш эмодзи {user_emoji}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Возможности 🌟 Anonka Premium:'
                                    '\n\n1) ⭐️ Особый значок: Подписчики теперь могут выбрать свой уникальный значок, выделяющий их среди других.'
                                    '\n\n2) 📌 Возможность закреплять сообщения: Закрепляйте важные сообщения, чтобы больше людей заметили ваше сообщение.'
                                    '\n\n3) ⏳ Отсутствие таймера: Не беспокойтесь о таймере – ваше время теперь полностью ваше!'
                                    '\n\n4) 📝 Редактирование сообщений: Теперь вы можете редактировать свои сообщения для еще большего удобства.'
                                    '\n\n5) 🚫 Отключение рекламы: Наслаждайтесь бесконечным общением без рекламных объявлений.'
                                    '\n\n6) 🗑️ Возможность удалить сообщение: Удаляйте нежелательные сообщения в любой момент.'
                                    '\n\n7) ❓ Возможность создавать опросы: Создавайте анонимные или публичные голосования прямо через бота и взаимодействуйте с аудиторией.'
                                    '\n\n8) 🌍 Доступ ко всем возможностям: Anonka Premium распространяется на другие боты, включая @Nurlatanonim_bot, @Samaraanonim_bot, @Kazananonim_bot и @AnongramAnonBot!')
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        month_button = types.InlineKeyboardButton('Premium на месяц', callback_data='premium_month')
        three_months_button = types.InlineKeyboardButton('Premium на 3 месяца', callback_data='premium_3months')
        year_button = types.InlineKeyboardButton('Premium на год', callback_data='premium_year')
        markup.add(month_button, three_months_button, year_button)
        bot.send_message(message.chat.id, 'Выберите тариф:', reply_markup=markup)


def gift_func(message):
    bot.send_message(message.chat.id,"Отправь юзернейм (например, @JonsonP) или ID пользователя, которому хочешь подарить подписку.")
    bot.register_next_step_handler(message, gift_premium_step)


def gift_premium_step(message):
    from_user_id = message.from_user.id
    target_id = resolve_username_to_id(message.text)
    if target_id is None:
        bot.send_message(message.chat.id, "Неверный формат юзернейма или ID")
        return
    
    target_enabled, _ = is_premium_enabled(target_id)
    if target_enabled:
        bot.send_message(message.chat.id, "У пользователя уже есть активная подписка, выберите другого.")
        return
    gift_dict[from_user_id] = {'target': target_id, 'duration': 0}
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    month_button = types.InlineKeyboardButton('🎁 Gift Premium на месяц', callback_data='gift_month')
    three_months_button = types.InlineKeyboardButton('🎁 Gift Premium на 3 месяца', callback_data='gift_3months')
    year_button = types.InlineKeyboardButton('🎁 Gift Premium на год', callback_data='gift_year')
    markup.add(month_button, three_months_button, year_button)
    bot.send_message(message.chat.id, 'Выберите желаемый срок подарка:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ['premium_month', 'premium_3months', 'premium_year'])
def handle_premium_choice(callback):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    if user_id in last_invoice:
        try:
            bot.delete_message(callback.message.chat.id, last_invoice[user_id])
        except Exception as e:
            print(f"Ошибка удаления старого счета: {e}")
        del last_invoice[user_id]

    if callback.data == 'premium_month':
        prices = prices_premium_month
    elif callback.data == 'premium_3months':
        prices = prices_premium_3months
    elif callback.data == 'premium_year':
        prices = prices_premium_year

    invoice_message = bot.send_invoice(
        chat_id=chat_id,
        title="Premium",
        description="Anonka premium",
        invoice_payload=callback.data,
        provider_token=None,  
        currency="XTR",
        prices=prices,
        start_parameter="premium-payment")
    
    last_invoice[user_id] = invoice_message.message_id


@bot.callback_query_handler(func=lambda callback: callback.data in ['gift_month', 'gift_3months', 'gift_year'])
def handle_gift_choice(callback):
    sender_id = callback.from_user.id
    if sender_id not in gift_dict:
        bot.send_message(callback.message.chat.id, "Информация о подарке не найдена.")
        return
    if sender_id in last_invoice:
        try:
            bot.delete_message(callback.message.chat.id, last_invoice[sender_id])
        except Exception as e:
            print(f"Ошибка удаления старого счета: {e}")
        del last_invoice[sender_id]

    if callback.data == 'gift_month':
        prices = prices_premium_month
    elif callback.data == 'gift_3months':
        prices = prices_premium_3months
    elif callback.data == 'gift_year':
        prices = prices_premium_year

    invoice_message = bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Gift Premium",
        description="Подарочная подписка",
        invoice_payload=callback.data,
        provider_token=None,  
        currency="XTR",
        prices=prices,
        start_parameter="gift-payment",
    )
    last_invoice[sender_id] = invoice_message.message_id


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options, error_message='Попробуйте еще раз позже')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Попробуйте заплатить еще раз через несколько минут, нам нужен небольшой отдых")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    payload = message.successful_payment.invoice_payload
    user_id = message.from_user.id

    if payload in ['premium_month', 'premium_3months', 'premium_year']:
        if payload == 'premium_month':
            duration = 30
        elif payload == 'premium_3months':
            duration = 90
        elif payload == 'premium_year':
            duration = 365

        bot.send_message(message.chat.id, f'Подписка активирована на {duration} дней.\n♥️ Мы любим тебя всей нашей командой разработчиков', parse_mode='Markdown')
        activate_premium(user_id, duration)
    
    elif payload in ['gift_month', 'gift_3months', 'gift_year']:
        sender_id = user_id  
        if sender_id not in gift_dict:
            bot.send_message(message.chat.id, "Информация о подарке не найдена.")
            return
        target_id = gift_dict[sender_id]['target']
        if payload == 'gift_month':
            duration = 30
        elif payload == 'gift_3months':
            duration = 90
        elif payload == 'gift_year':
            duration = 365
        
        sender_username = message.from_user.username if message.from_user.username else message.from_user.first_name
        activate_premium(target_id, duration)
        
        bot.send_message(message.chat.id, f'Подарок оформлен на {duration} дней. Подписка активирована для пользователя {target_id}.\nПодарил: @{sender_username}', parse_mode='Markdown')
        bot.send_message(target_id, f'Вам подарили премиум подписку на {duration} дней от пользователя @{sender_username}!\n♥️ Наслаждайтесь!', parse_mode='Markdown')
        del gift_dict[sender_id]
    else:
        bot.send_message(message.chat.id, 'Подписка активирована на 30 дней.\n♥️ Мы любим тебя всей нашей командой разработчиков', parse_mode='Markdown')
        activate_premium(user_id, 30)


def is_emoji(s):
    emoji_pattern = re.compile(
        "["  
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA70-\U0001FAFF"
        "\U0000200D"
        "\u200B-\u200D"
        "\uFE0F"
        "\U0001F3FB-\U0001F3FF"
        "\U0001F004-\U0001F0CF"  
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.fullmatch(s) is not None


@bot.callback_query_handler(func=lambda cb: cb.data in ['choice','defalt','defalt_homeles','custom_emoji_btn','new_custom_emoji_btn'])
def emodji_status(callback):
    user_id    = callback.from_user.id
    chat_id    = callback.message.chat.id
    message_id = callback.message.message_id

    current_custom = get_user_custom_emoji(user_id)
    user_emoji = get_user_emoji(user_id)

    if callback.data == 'choice':
        bot.send_message(chat_id, 'Пожалуйста, отправьте одно эмодзи.')
        bot.register_next_step_handler(callback.message,lambda msg: choice_emodji(msg, chat_id, message_id))
        return

    if callback.data == 'defalt':
        update_user_emoji(user_id, '🌟')
        new_emoji = '🌟'
    elif callback.data == 'defalt_homeles':
        update_user_emoji(user_id, '💌')
        new_emoji = '💌'
    elif callback.data == 'custom_emoji_btn':
        new_emoji = current_custom
        update_user_emoji(user_id, new_emoji)
    elif callback.data == 'new_custom_emoji_btn':
        bot.send_message(chat_id, 'Пожалуйста, добавьте свой эмодзи')
        bot.register_next_step_handler(callback.message, lambda msg: choice_custom_emoji(msg, chat_id, message_id))
        return
    else:
        return

    current_custom = get_user_custom_emoji(user_id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_choice = types.InlineKeyboardButton('💭 Изменить эмодзи', callback_data='choice')
    btn_def   = types.InlineKeyboardButton('🌟 По умолчанию',    callback_data='defalt')
    btn_hom   = types.InlineKeyboardButton('💌 Бедный статус',  callback_data='defalt_homeles')
    btn_new   = types.InlineKeyboardButton('➕ Добавить эмодзи', callback_data='new_custom_emoji_btn')

    buttons = [btn_choice]
    if new_emoji == '🌟':
        buttons.append(btn_hom)
    elif new_emoji == '💌':
        buttons.append(btn_def)
    else:  
        buttons += [btn_def, btn_hom]
    if current_custom is not None:
        if current_custom != user_emoji:
            btn_custom = types.InlineKeyboardButton(current_custom, callback_data='custom_emoji_btn')
            buttons.append(btn_custom)
    buttons.append(btn_new)

    markup.add(*buttons)

    bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=f'Эмодзи изменено на: {new_emoji}',reply_markup=markup)


def choice_emodji(message, orig_chat_id, orig_message_id):
    user_id = message.from_user.id
    custom_emoji = get_user_custom_emoji(user_id)
    new_emoji = message.text
    user_emoji = get_user_emoji(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    choice_btn = types.InlineKeyboardButton('💭 Изменить эмодзи', callback_data='choice')
    defalt_btn = types.InlineKeyboardButton('🌟 по умолчанию', callback_data='defalt')
    defalt_homeles_btn = types.InlineKeyboardButton('💌 бедный эмодзи статус', callback_data='defalt_homeles')
    if custom_emoji is not None:
        custom_emoji = types.InlineKeyboardButton(custom_emoji, callback_data='custom_emoji_btn')
    new_custom_emoji = types.InlineKeyboardButton('➕ Добавить свой эмодзи', callback_data='new_custom_emoji_btn')
    markup.add(choice_btn)
    markup.add(defalt_btn)
    markup.add(defalt_homeles_btn)
    if custom_emoji is not None:
        if custom_emoji != user_emoji:
            markup.add(custom_emoji)
    markup.add(new_custom_emoji)

    if is_emoji(new_emoji):
        update_user_emoji(user_id, new_emoji)
        bot.delete_message(orig_chat_id, orig_message_id)
        bot.send_message(orig_chat_id, f'Эмодзи изменено на: {new_emoji}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте одно эмодзи.')
        bot.register_next_step_handler(message, lambda msg: choice_emodji(msg, orig_chat_id, orig_message_id))


def choice_custom_emoji(message, orig_chat_id, orig_message_id): 
    user_id = message.from_user.id
    new_custom_emoji = message.text
    markup = types.InlineKeyboardMarkup(row_width=2)
    choice_btn = types.InlineKeyboardButton('💭 Изменить эмодзи', callback_data='choice')
    defalt_btn = types.InlineKeyboardButton('🌟 по умолчанию', callback_data='defalt')
    defalt_homeles_btn = types.InlineKeyboardButton('💌 бедный эмодзи статус', callback_data='defalt_homeles')
    new_custom_emoji_btn = types.InlineKeyboardButton('➕ Добавить свой эмодзи', callback_data='new_custom_emoji_btn')
    markup.add(choice_btn)
    markup.add(defalt_btn)
    markup.add(defalt_homeles_btn)
    markup.add(new_custom_emoji_btn)

    if is_emoji(new_custom_emoji):
        set_user_emoji(user_id, new_custom_emoji)
        bot.delete_message(orig_chat_id, orig_message_id)
        bot.send_message(orig_chat_id, f'Эмодзи изменено на: {new_custom_emoji}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте одно эмодзи.')
        bot.register_next_step_handler(message, lambda msg: choice_custom_emoji(msg, orig_chat_id, orig_message_id))