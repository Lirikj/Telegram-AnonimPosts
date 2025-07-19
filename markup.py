from telebot import types
from baza import is_admin, get_ghost_state, is_timer_enabled



def apply_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    apply_btn = types.InlineKeyboardButton('подключить 🌟Premium', callback_data='apply')
    markup.add(apply_btn)
    return markup


def markup_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    admin_btn = types.InlineKeyboardButton('👨🏼‍💻admin-menu', callback_data='admin_menu')
    info_btn = types.InlineKeyboardButton('📑info', callback_data='info_func') 
    # my_posts_btn = types.InlineKeyboardButton('🗂️Мои посты', callback_data='my_posts')
    get_link = types.InlineKeyboardButton('💬Anongram', url='t.me/AnongramAnonBot')

    if is_admin(user_id):
        markup.add(admin_btn)
    markup.add(info_btn)
    markup.add(get_link)
    return markup 



def build_admin_markup(user_id):
    timer_state = is_timer_enabled(user_id)
    timer_text = '⏰Выключить' if timer_state else '⏰Включить'
    ghost_state = get_ghost_state(user_id)
    ghost_text = '👻Инкогнито❌' if ghost_state == 1 else '👻Инкогнито✅'
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    users = types.InlineKeyboardButton('🫂users', callback_data='users')
    allmessage = types.InlineKeyboardButton('💬Сообщение', callback_data='allmessage')
    timer = types.InlineKeyboardButton(timer_text, callback_data='timer')
    banuser = types.InlineKeyboardButton('⛔️ban', callback_data='banuser')
    razban = types.InlineKeyboardButton('😊разбан', callback_data='razban')
    premium = types.InlineKeyboardButton('🌟Anonka premium', callback_data='premium')
    not_premium = types.InlineKeyboardButton('👎Отключить премиум', callback_data='not_premium')
    gift = types.InlineKeyboardButton('🎁Gift', callback_data='gift')
    adversting = types.InlineKeyboardButton('🖼️Реклама', callback_data='adversing_adms')
    all_adversting = types.InlineKeyboardButton('🙉Вся реклама', callback_data='all_adversting')
    i_love_you = types.InlineKeyboardButton('💌Сообщение пользователю', callback_data='message_for_user')
    ghost = types.InlineKeyboardButton(ghost_text, callback_data='ghost')
    add_admin = types.InlineKeyboardButton('➕Админ', callback_data='add_admin')
    delete_admin = types.InlineKeyboardButton('➖Админ', callback_data='delete_admin')
    exit = types.InlineKeyboardButton('↪️Выйти', callback_data='back_func')
    
    markup.add(users, allmessage, i_love_you)
    markup.add(premium, gift)
    markup.add(timer, not_premium)
    markup.add(adversting, all_adversting)
    markup.add(banuser, razban)
    markup.add(add_admin, delete_admin)
    markup.add(ghost)
    markup.add(exit)
    return markup



