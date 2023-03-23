import json
from telebot import types
from random import random

menuItems = ["▶️ Начать тест", "📊 Статистика", "🛠 Параметры"]
paramItems = [
  "Изменить тему изучения", "Изменить количество слов в тесте",
  "Изменить количество правильных ответов для запоминания слова"
]
menuTestItems = ["❓Пример использования слова❓", "⛔️Завершить тест⛔️"]


def initTest():
  with open(r'./test.json', 'r') as jsonRequest:
    request = json.load(jsonRequest)
  return (request)


def menuKeyboard():
  keyboard = types.ReplyKeyboardMarkup(row_width=1,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
  buttonStartTest = types.KeyboardButton(text=menuItems[0])
  buttonShowStat = types.KeyboardButton(text=menuItems[1])
  buttonParams = types.KeyboardButton(text=menuItems[2])
  keyboard.row(buttonStartTest)
  keyboard.row(buttonShowStat, buttonParams)
  return keyboard


# Параметры
def paramsKeyboard():
  keyboard = types.InlineKeyboardMarkup()
  changeTheme = types.InlineKeyboardButton(paramItems[0],
                                           callback_data='changeTheme')
  countWords = types.InlineKeyboardButton(paramItems[1],
                                          callback_data='changeCountWords')
  repeatWords = types.InlineKeyboardButton(paramItems[2],
                                           callback_data='changeCountRepeat')
  keyboard.row(changeTheme)
  keyboard.row(countWords)
  keyboard.row(repeatWords)
  return keyboard


def changeCountKeyboard(lenKeysList, flag):
  keyboard = types.InlineKeyboardMarkup()
  for i in range(lenKeysList):
    keyboard.add(
      types.InlineKeyboardButton(str(i + 1), callback_data=flag + str(i + 1)))
  keyboard.add(types.InlineKeyboardButton("Отмена", callback_data='cancel'))
  return (keyboard)

def changeThemeTest():
  keyboard = types.InlineKeyboardMarkup()
  json = initTest()
  themesTest = json.values()
  for iter in themesTest:
    themeName = 0
    for keys in json:
      if json[keys] == iter:
        themeName = keys
        break
    keyboard.add(types.InlineKeyboardButton(iter["theme"], callback_data=keys))
  keyboard.add(types.InlineKeyboardButton("Отмена", callback_data='cancel'))
  return (keyboard)
  

def testInlineKeyboard(question):
  keyboard = types.InlineKeyboardMarkup(row_width=1)
  randButtons = [0 for i in range(4)]
  randButtons[0] = types.InlineKeyboardButton(question["true"],
                                              callback_data='true')
  randButtons[1] = types.InlineKeyboardButton(question["f1"],
                                              callback_data='false')
  randButtons[2] = types.InlineKeyboardButton(question["f2"],
                                              callback_data='false')
  randButtons[3] = types.InlineKeyboardButton(question["f3"],
                                              callback_data='false')
  for i in range(1, len(randButtons)):
    if int(random() * 1000) % 2 == 0:
      tmpButton = randButtons[i]
      randButtons[i] = randButtons[i - 1]
      randButtons[i - 1] = tmpButton
  for i in range(0, len(randButtons)):
    keyboard.add(randButtons[i])
  buttonExample = types.InlineKeyboardButton(text=menuTestItems[0],
                                             callback_data='example')
  buttonEndTest = types.InlineKeyboardButton(text=menuTestItems[1],
                                             callback_data='endtest')

  keyboard.add(buttonExample, buttonEndTest)
  return keyboard
