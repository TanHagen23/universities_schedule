from telebot import types, telebot
from schedule_dictionary import schedule
from datetime import datetime

bot = telebot.TeleBot('7868621264:AAFolJ9Z3rWEOTyEOqwFOEK9D5qWOzi9SpE')
@bot.message_handler(commands=['start', 'help'])
def start (message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_lesson = types.KeyboardButton("Текущий урок")
    markup.add(button_lesson)
    bot.send_message(
        message.chat.id, 
        f'Привет, {message.from_user.first_name}! Используйте /today для расписания на сегодня, /week  или  нажмите "Текущий урок" для расписания на неделю.',
        reply_markup=markup
        )

def format_schedule(day, lessons):
    text = f"Расписание на {day}:\n"
    for lesson in lessons:
        время = lesson.get('время', 'Время не указано')
        предмет = lesson.get('предмет', 'Предмет не указан')
        преподаватель = lesson.get('преподаватель', 'Преподаватель не указан')
        
        # Обработка подгрупп
        if 'подгруппа_1' in lesson:
            подгруппа_1 = lesson['подгруппа_1']
            text += f"{время} - Подгруппа 1: {подгруппа_1['предмет']} (Преподаватель: {подгруппа_1['преподаватель']})\n"
        elif 'подгруппа_2' in lesson:
            подгруппа_2 = lesson['подгруппа_2']
            text += f"{время} - Подгруппа 2: {подгруппа_2['предмет']} (Преподаватель: {подгруппа_2['преподаватель']})\n"
        else:
            text += f"{время} - {предмет} (Преподаватель: {преподаватель})\n"
    
    return text

@bot.message_handler(func=lambda message: message.text == "Текущий урок")
def current_lesson(message):
    days_of_week = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }

    today = datetime.now().strftime("%A")
    day = days_of_week.get(today, today)
    current_time = datetime.now().time()
    schedule_today = schedule.get(day, [])

    current_lesson_text = "Сейчас нет занятий!"
    for lesson in schedule_today:
        время = lesson.get("время", "")
        if время:
            start_time_str, end_time_str = время.split(" - ")
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            # Проверка, находится ли текущее время в интервале урока
            if start_time <= current_time <= end_time:
                # Если есть подгруппы
                if 'подгруппа_1' in lesson and 'подгруппа_2' in lesson:
                    подгруппа_1 = lesson['подгруппа_1']
                    подгруппа_2 = lesson['подгруппа_2']
                    current_lesson_text = (f"Сейчас идет урок:\n"
                                           f"Подгруппа 1: {подгруппа_1['предмет']} "
                                           f"(Преподаватель: {подгруппа_1['преподаватель']})\n"
                                           f"Подгруппа 2: {подгруппа_2['предмет']} "
                                           f"(Преподаватель: {подгруппа_2['преподаватель']})")
                else:
                    # Если подгрупп нет, используем основной предмет и преподавателя
                    предмет = lesson.get("предмет", "Предмет не указан")
                    преподаватель = lesson.get("преподаватель", "Преподаватель не указан")
                    current_lesson_text = f"Сейчас идет урок: {предмет} (Преподаватель: {преподаватель})"
                break  # Завершаем цикл, если нашли текущий урок

    bot.send_message(message.chat.id, current_lesson_text)


@bot.message_handler(commands=['today'])
def send_schedule(message):
    days_of_week = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }
    
    today = datetime.now().strftime("%A")
    day = days_of_week.get(today, today)
    schedule_today = schedule.get(day, [])

    if schedule_today:
        text = format_schedule(day, schedule_today)
    else:
        text = "Сегодня занятий нет!"

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['week'])
def send_week_schedule(message):
    text = "Расписание на неделю:\n\n"
    for day, lessons in schedule.items():
        text += format_schedule(day, lessons)
        text += "\n"
    
    bot.send_message(message.chat.id, text)

bot.polling(non_stop=True)