import sqlite3
import time
from config import bot, CHANNEL_osn
from datetime import datetime, timedelta


def init_db():
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        date_joined TEXT,
                        timer INTEGER DEFAULT 1,
                        ban INTEGER DEFAULT 0,
                        premium TEXT,
                        premium_expiry TEXT, 
                        emoji TEXT DEFAULT '🌟', 
                        user_emoji TEXT DEFAULT 'None',
                        ghost_mode INTEGER DEFAULT 0, 
                        admin INTEGER DEFAULT 0
                )''')

        c.execute('''CREATE TABLE IF NOT EXISTS posts (
                        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        content TEXT,
                        media_type TEXT,
                        file_id TEXT,
                        date TEXT,
                        comments INTEGER DEFAULT 0,
                        reactions INTEGER DEFAULT 0,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        if conn:
            conn.close()


def user_exists(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_post(user_id, content, media_type=None, file_id=None):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO posts (user_id, content, media_type, file_id, date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            content,
            media_type,
            file_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении записи в таблицу posts: {e}")
    finally:
        if conn:
            conn.close()


def count_post_stats():
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        cutoff = (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""SELECT post_id, content, views, reactions, comments, date FROM posts WHERE date <= ?""", (cutoff,))
        posts = c.fetchall()

        for post in posts:
            post_id, content, views, reactions, comments, date_str = post

            report = (
                f"Статистика поста ID {post_id}:\n"
                f"Дата публикации: {date_str}\n"
                f"Просмотры: {views}\n"
                f"Реакции: {reactions}\n"
                f"Комментарии: {comments}"
            )
            bot.send_message(CHANNEL_osn, report)

        conn.close()
    except Exception as e:
        print(f"Ошибка при подсчете статистики: {e}")


def get_posts_by_user(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("""
            SELECT post_id, content, media_type, file_id, date, comments, reactions, views 
            FROM posts 
            WHERE user_id = ? 
            ORDER BY date DESC
        """, (user_id,))
        posts = c.fetchall()
        return posts
    except sqlite3.Error as e:
        print(f"Ошибка при получении постов для пользователя {user_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()


def remove_old_posts():
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        cutoff = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("DELETE FROM posts WHERE date <= ?", (cutoff,))
        conn.commit()
        print("Старые посты удалены")
    except sqlite3.Error as e:
        print(f"Ошибка при удалении старых постов: {e}")
    finally:
        if conn:
            conn.close()


def activate_premium(user_id, duration=30):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        premium_expiry = (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d %H:%M:%S')

        c.execute('''UPDATE users
                    SET premium = 1, premium_expiry = ?
                    WHERE user_id = ?''', (premium_expiry, user_id))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении данных: {e}")
    finally:
        if conn:
            conn.close()


def deactivate_premium(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        c.execute('''UPDATE users
                    SET premium = 0, premium_expiry = NULL
                    WHERE user_id = ?''', (user_id,))

        conn.commit() 
    except sqlite3.Error as e:
        print(f"Ошибка при деактивации премиум-подписки: {e}")
    finally:
        if conn:
            conn.close()


def check_premium_status():
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        now = datetime.now()
        c.execute('SELECT user_id, premium_expiry FROM users WHERE premium = 1')
        users_with_premium = c.fetchall()

        for user in users_with_premium:
            user_id, premium_expiry = user
            if premium_expiry:
                premium_expiry_dt = datetime.strptime(premium_expiry, '%Y-%m-%d %H:%M:%S')
                if premium_expiry_dt < now:
                    try:
                        bot.send_message(user_id, 'Ваша подписка закончилась')
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                    deactivate_premium(user_id)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при проверке статуса премиум-подписки: {e}")
    finally:
        if conn:
            conn.close()


def get_days_left(premium_expiry):
    now = datetime.now()
    premium_end = datetime.strptime(premium_expiry, '%Y-%m-%d %H:%M:%S')
    days_left = (premium_end - now).days
    return days_left if days_left > 0 else 0


def is_premium_enabled(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        now = datetime.now()
        c.execute('SELECT premium, premium_expiry FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result is not None:
            premium, premium_expiry = result
            if premium:
                if premium_expiry is None or datetime.strptime(premium_expiry, '%Y-%m-%d %H:%M:%S') <= now:
                    deactivate_premium(user_id)
                    return False, 0  
                else:
                    days_left = get_days_left(premium_expiry)
                    return True, days_left  
            return False, 0  

        return False, 0  
    except sqlite3.Error as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return False, 0
    finally:
        if conn:
            conn.close()


def start_premium_checker():
    while True:
        check_premium_status()  
        time.sleep(5)


def save_user_data(user):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, date_joined)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                date_joined = excluded.date_joined
        """, (user.id, user.username, user.first_name, user.last_name, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении данных пользователя: {e}")
    finally:
        if conn:
            conn.close()


def delete_user(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        conn.close()


def get_usernames():
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users")
        usernames = [row[0] for row in c.fetchall()]
        return usernames
    except sqlite3.Error as e:
        print(f"Error fetching usernames: {e}")
        return []
    finally:
        if conn:
            conn.close()


def set_timer(user_id, state):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        timer_value = 1 if state else 0
        
        c.execute('''
            INSERT INTO users (user_id, timer)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            timer = excluded.timer
        ''', (user_id, timer_value))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении базы данных: {e}")
    finally:
        if conn:
            conn.close()


def is_timer_enabled(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        c.execute('SELECT timer FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result is not None:
            return result[0]  #

    except sqlite3.Error as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return None
    finally:
        if conn:
            conn.close()


def ban_user(user_id, state):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        ban_value = 1 if not state else 0  

        c.execute('''
            INSERT INTO users (user_id, ban)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            ban = excluded.ban
        ''', (user_id, ban_value))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении базы данных: {e}")
    finally:
        if conn:
            conn.close()


def is_ban(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()

        c.execute('SELECT ban FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result is not None:
            return result[0] == 1 
        else:
            return False 

    except sqlite3.Error as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_user_emoji(user_id):
    conn = sqlite3.connect('usersj.db')
    c = conn.cursor()
    c.execute("SELECT emoji FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return '🌟'


def update_user_emoji(user_id, new_emoji):
    conn = sqlite3.connect('usersj.db')
    c = conn.cursor()
    c.execute("UPDATE users SET emoji = ? WHERE user_id = ?", (new_emoji, user_id))
    conn.commit()
    conn.close()


def init_ad_db():
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS ads (
                        ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT,
                        date_added TEXT,
                        expiry_date TEXT
                    )''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы для рекламы: {e}")
    finally:
        if conn:
            conn.close()


def add_ad_to_db(content):
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()

        date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO ads (content, date_added) VALUES (?, ?)", (content, date_added))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении рекламы: {e}")
    finally:
        if conn:
            conn.close()


def get_active_ads_from_db():
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()

        c.execute("SELECT content FROM ads")
        ads = c.fetchall()

        return [ad[0] for ad in ads]  
    except sqlite3.Error as e:
        print(f"Ошибка при получении активной рекламы: {e}")
        return []
    finally:
        if conn:
            conn.close()


def remove_old_ads_from_db(bot, admin_chat_id):
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("SELECT ad_id, content FROM ads WHERE expiry_date < ?", (cutoff_date,))
        old_ads = c.fetchall()

        if old_ads:
            ads_text = "\n\n".join(f"Реклама ID {ad_id}: {content}" for ad_id, content in old_ads)
            bot.send_message(admin_chat_id, f"Следующие рекламы будут удалены:\n\n{ads_text}")
            c.execute("DELETE FROM ads WHERE expiry_date < ?", (cutoff_date,))
            conn.commit()

            bot.send_message(admin_chat_id, "Старая реклама успешно удалена.")
        else:
            bot.send_message(admin_chat_id, "Нет старой рекламы для удаления.")

    except sqlite3.Error as e:
        print(f"Ошибка при удалении старой рекламы: {e}")
    finally:
        if conn:
            conn.close()


def get_all_ads_from_db():
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()

        c.execute("SELECT ad_id, content FROM ads")
        ads = c.fetchall()

        return ads  
    except sqlite3.Error as e:
        print(f"Ошибка при получении рекламы: {e}")
        return []
    finally:
        if conn:
            conn.close()


def delete_ad_from_db(ad_id):
    try:
        conn = sqlite3.connect('ads.db')
        c = conn.cursor()

        c.execute("DELETE FROM ads WHERE ad_id = ?", (ad_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении рекламы: {e}")
    finally:
        if conn:
            conn.close()


def ghost_mode(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT ghost_mode FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        current_value = row[0] if row is not None else 0

        new_value = 0 if current_value == 1 else 1

        c.execute('''
            INSERT INTO users (user_id, ghost_mode)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            ghost_mode = excluded.ghost_mode
        ''', (user_id, new_value))
        conn.commit()
        return new_value
    except sqlite3.Error as e:
        print(f"Ошибка при переключении ghost_mode для пользователя {user_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_ghost_state(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT ghost_mode FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row is not None else 0
    except sqlite3.Error as e:
        print(f"Ошибка при получении ghost_mode: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def admin_mode(user_id, state):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        admin_value = 1 if state else 0  

        c.execute('''
            INSERT INTO users (user_id, admin)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            admin = excluded.admin
        ''', (user_id, admin_value))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении статуса администратора: {e}")
    finally:
        if conn:
            conn.close()


def add_admin(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (user_id, admin)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
            admin = 1
        ''', (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении администратора для пользователя {user_id}: {e}")
    finally:
        if conn:
            conn.close() 


def delete_admin(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("UPDATE users SET admin = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении статуса администратора для пользователя {user_id}: {e}")
    finally:
        if conn:
            conn.close() 


def is_admin(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT admin FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return (row is not None and row[0] == 1)
    except sqlite3.Error as e:
        print(f"Ошибка при проверке админа для пользователя {user_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()


def resolve_username_to_id(identifier):
    identifier = identifier.strip()
    if identifier.startswith('@'):
        identifier = identifier[1:]
    if identifier.isdigit():
        return int(identifier)
    
    identifier_lower = identifier.lower()
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE lower(username) = ?", (identifier_lower,))
        result = c.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Ошибка при разрешении username: {e}")
        return None
    finally:
        if conn:
            conn.close()



def set_user_emoji(user_id, new_emoji):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (user_id, user_emoji)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                user_emoji = excluded.user_emoji
        """, (user_id, new_emoji))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при установке emoji для пользователя {user_id}: {e}")
    finally:
        if conn:
            conn.close()


def get_user_custom_emoji(user_id):
    try:
        conn = sqlite3.connect('usersj.db')
        c = conn.cursor()
        c.execute("SELECT user_emoji FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            return None
        val = row[0]
        return None if val == 'None' else val
    except sqlite3.Error as e:
        print(f"Ошибка при получении user_emoji для пользователя {user_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()