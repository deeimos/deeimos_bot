import os
from flask import Flask, request
import telebot
import time
from keyboard import menuItems, menuKeyboard, initTest, paramsKeyboard, testInlineKeyboard, changeCountKeyboard, changeThemeTest
from database import DataBase

import zoneinfo

secret = os.getenv("KEY")
bot = telebot.TeleBot(os.getenv("TOKEN"))
jsonThemes = initTest()  # загрузка теста из json файла
db = DataBase()
zone = zoneinfo.ZoneInfo("Europe/Moscow")
maxRepeats = 10


bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=f'{os.getenv("URL")}')

app = Flask("deeimosbot")


@app.route('/', methods=["POST"])
def webhook():
  bot.process_new_updates(
    [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "ok", 200


# Первый запуск бота у пользователя
@bot.message_handler(commands=['start'])
def startCommand(message):
  db.addUser(message.from_user)
  bot.send_message(message.chat.id,
                   'Hi *' + message.chat.first_name +
                   '*! Выбери пункт из меню.',
                   parse_mode='Markdown',
                   reply_markup=menuKeyboard())


# Параметры
def params(message):
  user = db.getUser(message.chat.id)
  bot.send_message(message.chat.id,
                   menuItems[2] + ":\n",
                   reply_markup=menuKeyboard())
  stat = "Выбранная тема:  " + str(user["choisedTheme"]["theme"]) +\
       "\nКоличество слов в тесте:  " + str(user["countWords"]) +\
       "\nКоличество  правильных ответов для запоминания слова:  " + str(user["countRepeat"]) + "\n"
  bot.send_message(message.chat.id, stat, reply_markup=paramsKeyboard())


# Статистика
def showStat(message):
  user = db.getUser(message.chat.id)
  bot.send_message(message.chat.id,
                   menuItems[1] + ":\n",
                   reply_markup=menuKeyboard())
  stat = "Всего выучено слов:  " + str(db.getCountLearnedWords(user)) +\
       "\nВыбранная тема:  " + str(user["choisedTheme"]["theme"]) +\
       "\nСлов в выбранной теме:  " + str(len(user["choisedTheme"]["test"])) +\
       "\nПоследнее прохождение теста:  "
  if user["lastTest"]:
    stat += str(user["lastTest"]) + "\n"
  else:
    stat += "-\n"
  bot.send_message(message.chat.id, stat, reply_markup=menuKeyboard())


def startTest(message):
  user = db.getUser(message.chat.id)
  count = user["count"]
  countWords = user["countWords"]
  beingInTest = user["beingInTest"]
  test = user["choisedTheme"]["test"]
  
  for keys in test:
    if count < countWords and not keys in beingInTest:
      db.isTest(user, keys)
      bot.send_message(message.chat.id,
                       f'Перевод слова "{keys}"',
                       reply_markup=testInlineKeyboard(test[keys]))
      break


def checkFinishTest(message):
  user = db.getUser(message.chat.id)
  countWords = user["countWords"]
  count = user["count"]
  count += 1
  db.incTest(user, 1)

  if count >= countWords:
    db.endTest(user)
    bot.send_message(message.chat.id,
                     text="❎ Тест завершен",
                     reply_markup=menuKeyboard())
  else:
    startTest(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  if call.message:
    user = db.getUser(call.message.chat.id)
    lastWord = user["lastWord"]
    count = user["count"]
    countWords = user["countWords"]
    choisedTheme = user["choisedTheme"]
    test = user["choisedTheme"]["test"]
    
    if call.data == "changeCountRepeat":
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Изменить количество правильных ответов для запоминания слова")
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=changeCountKeyboard(maxRepeats, "repeat"))
      
    elif call.data == "changeCountWords":
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Изменить количество слов в тесте")
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=changeCountKeyboard(len(choisedTheme["test"]), "count"))
      
    elif call.data == "changeTheme":
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Изменить тему изучения")
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=changeThemeTest())
      
    elif call.data == "true":
      db.incWord(user)
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="✅ Правильный ответ")
      checkFinishTest(call.message)
      
    elif call.data == "false":
      db.clearWord(user)
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="❌ Вы ошиблись")
      checkFinishTest(call.message)
      
    elif call.data == "example":
      bot.send_message(chat_id=call.message.chat.id,
                       text=test[lastWord]["example"])
      
    elif call.data == "endtest":
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      db.incTest(user, countWords)
      checkFinishTest(call.message)
      
    elif call.data in jsonThemes.keys():
      db.changeTheme(user, jsonThemes[call.data])
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Успешно измененено✅")
      params(call.message)
      
    elif call.data > 'count0' and call.data < 'count999':
      db.changeCountWordsOrRepeat(user, int(call.data[5:]), "countWords")
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Успешно измененено✅")
      params(call.message)
      
    elif call.data > 'repeat0' and call.data < 'repeat999':
      db.changeCountWordsOrRepeat(user, int(call.data[6:]), "countRepeat")
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Успешно измененено✅")
      params(call.message)
      
    elif call.data == "cancel":
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Отменено❎")
      params(call.message)
    

@bot.message_handler()
def controller_msg(message):
  db.msgController(message.from_user, jsonThemes)
  if (message.text == menuItems[0]):
    bot.send_message(message.chat.id, "Удачи🍀", reply_markup=None)
    startTest(message)
  elif (message.text == menuItems[1]):
    showStat(message)
  elif (message.text == menuItems[2]):
    params(message)
  print(message.json)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
