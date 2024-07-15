import json
import sqlite3
import telebot
import weather
from telebot import types
with open('settings.json', 'r', encoding='utf-8') as f:
    bot_file = json.load(f)

def database():
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()
    return conn, cur

bot = telebot.TeleBot(token = bot_file['TOKEN'])
new_get_city = False
get_city = False
@bot.message_handler(commands = ['start'])
def starting(message):
    global new_get_city, get_city
    conn, cur = database()
    id_user = message.from_user.id
    user_name = message.from_user.first_name
    cur.execute("SELECT name_city FROM weather_table WHERE id_user = ?", (id_user,))
    user_table = cur.fetchone()
    if user_table == None:

        bot.send_message(message.chat.id, text = f'Привет {user_name}, пожалуйста введи название места жительства о погоде которого ты хочешь знать!😊')
        new_get_city = True
    else:
        buttons = types.InlineKeyboardMarkup(row_width=2)
        city_rename = types.InlineKeyboardButton(text = 'Переназначить\nгород', callback_data='city_rename')
        get_weather_city = types.InlineKeyboardButton(text = 'Узнать погоду', callback_data='get_weather_city')
        buttons.add(city_rename, get_weather_city)
        bot.send_message(message.chat.id, text = f'Привет {user_name}, что хочешь узнать или сделать?🤔', reply_markup=buttons)


@bot.message_handler(content_types='text')
def texting(message):
    global new_get_city, get_city
    conn, cur = database()
    id_user = message.from_user.id
    text_message = message.text
    if new_get_city:
        if weather.check_city(text_message):
            cur.execute("INSERT INTO weather_table (id_user, name_city) VALUES (?, ?)", (id_user, text_message))
            conn.commit()
            get_city = False
            buttons = types.InlineKeyboardMarkup(row_width=1)
            start = types.InlineKeyboardButton(text = 'назад', callback_data='start')
            buttons.add(start)
            bot.send_message(message.chat.id, text = 'Ваше место жительство добавлено', reply_markup=buttons)
        else:
            bot.send_message(message.chat.id, text = 'Вы ввели некорректное место жительства, попробуйте еще раз🙏🏼')
    elif get_city:
            cur.execute("UPDATE weather_table SET name_city = (?) WHERE id_user = (?)", (text_message, id_user))
            conn.commit()
            new_get_city = False
            buttons = types.InlineKeyboardMarkup(row_width=1)
            start = types.InlineKeyboardButton(text = 'назад', callback_data='start')
            buttons.add(start)
            bot.send_message(message.chat.id, text = 'Ваше место жительство добавлено', reply_markup=buttons)


@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    global get_city
    call_data = call.data
    user_name = call.message.from_user.first_name
    conn, cur = database()
    id_user = call.message.chat.id
    if call_data == 'get_weather_city':
        cur.execute("SELECT name_city FROM weather_table WHERE id_user = ?", (id_user,))
        city = cur.fetchone()[0]
        bot.send_message(call.message.chat.id, text = f'{weather.weather_city(city)}')
    elif call_data == 'city_rename':
        bot.send_message(call.message.chat.id, text = f'Введи название место жительства о погоде которого ты хочешь знать!😊')
        get_city = True
    elif call.data == 'start':
        buttons = types.InlineKeyboardMarkup(row_width=2)
        city_rename = types.InlineKeyboardButton(text = 'Переназначить\nгород', callback_data='city_rename')
        get_weather_city = types.InlineKeyboardButton(text = 'Узнать погоду', callback_data='get_weather_city')
        buttons.add(city_rename, get_weather_city)
        bot.send_message(call.message.chat.id, text = f'Привет {user_name}, что хочешь узнать или сделать?🤔', reply_markup=buttons)
bot.infinity_polling()