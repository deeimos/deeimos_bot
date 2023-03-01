import os
from flask import Flask, request
import telebot
# from telebot import types
import time
from keyboard import menuItems, menuKeyboard, initTest, paramsKeyboard, testInlineKeyboard
# import pymongo
from pymongo import MongoClient

secret = os.getenv("KEY")
bot = telebot.TeleBot(os.getenv("TOKEN"))
db = ''
json = initTest()  # загрузка теста из json файла
test = json
#dev temp
testInd = []
countWords = 7
count = 0
currentWord = ""

def connectMongoDB(db):
  db = MongoClient(os.getenv("MONGO_DB_URL"))
  return db


bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=f'{os.getenv("URL")}')

app = Flask("deeimosbot")
db = connectMongoDB(db)
if db:
  print("MongoDB connected!")
else:
  exit(-1)


@app.route('/', methods=["POST"])
def webhook():
  bot.process_new_updates(
    [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "ok", 200


# Первый запуск бота у пользователя
@bot.message_handler(commands=['start'])
def startCommand(message):
  bot.send_message(message.chat.id,
                   'Hi *' + message.chat.first_name +
                   '*! Выбери пункт из меню.',
                   parse_mode='Markdown',
                   reply_markup=menuKeyboard())


#Статистика
def showStat(message):
  bot.send_message(
    message.chat.id, menuItems[1] +
    ":\nСлов выучено: 0\nСлов в выбранной теме: 0\nПоследнее прохождение теста: -\n", reply_markup=menuKeyboard()
  )


def startTest(message):
  global count, testInd, currentWord, test
  for keys in test:
    if count < countWords and not keys in testInd:
      currentWord = keys
      bot.send_message(message.chat.id,
                       f'Перевод слова "{keys}"',
                       reply_markup=testInlineKeyboard(test[keys]))
      # test.pop(keys)
      count += 1
      testInd.append(keys)
      break


def endTest(call=None):
  global count, testInd, currentWord
  count = 0
  currentWord = ""
  testInd = []

def checkFinishTest(message):
  if count == countWords:
    endTest()
    bot.send_message(message.chat.id, text="❎ Тест завершен", reply_markup=menuKeyboard())
  else:
    startTest(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  global test, count
  if call.message:
    if call.data == "true":
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.send_message(chat_id=call.message.chat.id, text="✅ Правильный ответ")
      checkFinishTest(call.message)
    elif call.data == "false":
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      bot.send_message(chat_id=call.message.chat.id, text="❌ Вы ошиблись")
      checkFinishTest(call.message)
    elif call.data == "example":
      bot.send_message(chat_id=call.message.chat.id,
                       text=test[currentWord]["example"])
    elif call.data == "endtest":
      bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=None)
      count = countWords
      checkFinishTest(call.message)


@bot.message_handler()
def controller_msg(message):
  global test, count, currentWord
  if (message.text == menuItems[0]):
    # bot.send_message(message.chat.id, "Удачи💕", reply_markup=None)
    bot.send_message(message.chat.id, "Удачи🍀", reply_markup=None)
    test = json["study"]["test"]
    startTest(message)
  elif (message.text == menuItems[1]):
    showStat(message)
  elif (message.text == menuItems[2]):
    bot.send_message(message.chat.id,
                     menuItems[2],
                     reply_markup=menuKeyboard())
    bot.send_message(message.chat.id,
                     menuItems[2],
                     reply_markup=paramsKeyboard())
  print(message.json)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
