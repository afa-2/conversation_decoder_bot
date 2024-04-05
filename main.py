import os
import time
import telebot
import logging
from scripts.get_settings_from_config import get_settings
from scripts.work_with_audio import get_text_from_audio


"""
Предварительная подготовка
"""
# Логирование -------------------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("log.txt"),  # Запись логов в файл
    ]
)

# Получаем настройки -------------------------------------------------------------------------------------------
settings = get_settings()
token = settings['telegram_token']  # токен бота
users = settings['users']  # словарь с юзерами


# Запускаем бота -----------------------------------------------------------------------------------------------
bot = telebot.TeleBot(token)

"""
Основной скрипт
"""

# Реагируем на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обработчик команды /start
    """
    chat_id = message.chat.id
    user_name = message.from_user.username
    user_id = str(message.from_user.id)

    # проверяем, есть ти такой id в словаре users_id_and_assistants
    if user_id in users:
        text = (f"Hello, {user_name}!!! Коротко о том, как мной пользоваться.\n"
                f"Загружаешь аудиофайл и ждешь текста. \n")
    else:
        text = "А вы вообще кто?"

    bot.send_message(chat_id, text)


# Реагируем на загрузку нового файла
@bot.message_handler(content_types=['audio', 'document', 'voice'])
def create_new_thread(message):
    """
    Эта функция вызывается, когда пользователь загружает аудиофайл, затем отправляет его в openai и получает текст
    """
    try:
        # получаем id пользователя
        user_id = str(message.from_user.id)
        # проверяем, есть ти такой id в словаре users_id_and_assistants
        if user_id in users:
            path_to_file = ''

            if message.content_type == 'audio':  # если это аудио файл
                # принимаем и сохраняем файл на сервер в папку audio
                file_info = bot.get_file(message.audio.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                path_to_file = 'audio/' + message.audio.file_name
                with open(path_to_file, 'wb') as new_file:
                    new_file.write(downloaded_file)

            elif message.content_type == 'document':  # если это wav
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                path_to_file = 'audio/' + message.document.file_name
                with open(path_to_file, 'wb') as new_file:
                    new_file.write(downloaded_file)

            elif message.content_type == 'voice':  # если это голос
                file_info = bot.get_file(message.voice.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = f'{user_id}_voice.ogg'
                path_to_file = 'audio/' + file_name
                with open(path_to_file, 'wb') as new_file:
                    new_file.write(downloaded_file)

            if len(path_to_file) > 0:  # если мы вообще что-то сохранили
                try:
                    bot.reply_to(message, "Файл успешно принят, отправляю на обработку в openAi")

                    # берем файл и отправляем в openai для расшифровки
                    open_ai_key = users[user_id]['open_ai_key']  # получаем ключ openai для пользователя
                    result_text = get_text_from_audio(open_ai_key, path_to_file)

                    # возвращаем результат клиенту
                    # if message is too long / если сообщение слишком длинное
                    if len(result_text) > 4096:
                        for x in range(0, len(result_text), 4096):
                            bot.send_message(message.chat.id, '{}'.format(result_text[x:x + 4096]))
                            time.sleep(0.5)
                    else:
                        bot.send_message(message.chat.id, '{}'.format(result_text))

                except Exception as e:
                    errr_text = f"Ошибка: {e}"
                    bot.send_message(message.chat.id, errr_text)
                    logging.error(errr_text)

                # удаляем файл
                os.remove(path_to_file)

            else:
                bot.reply_to(message, "Что-то пошло не так")

        else:
            text = "А вы вообще кто?"
            bot.send_message(message.chat.id, text)

    except Exception as e:
        errr_text = f"Ошибка: {e}"
        bot.send_message(message.chat.id, errr_text)
        logging.error(errr_text)


# запускаем бота
bot.infinity_polling()








