import os
import pymongo
from keyboard import initTest
from datetime import datetime
import zoneinfo
'''
---> пользователи
USERS:
_id           - ключ к записи
userId        - id в tg
username      - ник в tg
name          - имя в tg(необязательно)
countRepeat   - количество повторений 
choisedTheme  - выбранная тема для изучения
countWords    - количество слов в тесте
lastTest      - время последнего прохождения теста
--- также users, костыль вместо глобальных переменных (должно решить проблему одновременного для нескольких пользователей теста)
beingInTest   - список куда вносятся слова, которые были в текущем тесте
lastWord      - последнее или текущее слово
count         - счетчик для контроля слов в тесте

---> слова знакомые пользователю
LERNING:
_id           - ключ к записи
user          - ссылка на запись пользователя
word          - слово
countTrue     - количество повторений
lastRepeat    - последнее повторение в тесте
'''

zone = zoneinfo.ZoneInfo("Europe/Moscow")


class DataBase():

  def __init__(self):
    self.cluster = pymongo.MongoClient(os.getenv("MONGO_DB_URL"))
    self.db = self.cluster.bot
    self.users = self.db.users
    self.learning = self.db.learning

  def getUser(self, id):
    user = self.users.find_one({"userId": id})
    return (user)

  def addUser(self, userData):
    if (self.getUser(userData.id)):
      return
    test = initTest()  # загрузка теста из json файла
    user = {
      "userId": userData.id,
      "username": userData.username,
      "name": userData.first_name,
      "countRepeat": 3,
      "choisedTheme": test["study"],
      "countWords": 3,
      "lastTest": None,
      "beingInTest": [],
      "lastWord": "",
      "count": 0
    }
    self.users.insert_one(user)

  def updateUser(self, user, value):
    self.users.update_one({"userId": user["userId"]}, {"$set": value})

  def isTest(self, user, word):
    beingInTest = user["beingInTest"]
    beingInTest.append(word)
    value = {"beingInTest": beingInTest, "lastWord": word}
    self.updateUser(user, value)

  def incTest(self, user, inc):
    count = user["count"]
    count += inc
    value = {"count": count}
    self.updateUser(user, value)

  def endTest(self, user):
    lastTest = datetime.now(zone).strftime("%d.%m.%Y %H:%M")
    value = {
      "beingInTest": [],
      "lastWord": "",
      "count": 0,
      "lastTest": lastTest
    }
    self.updateUser(user, value)

  def changeTheme(self, user, choisedTheme):
    countWords = user["countWords"]
    if countWords > len(choisedTheme["test"]):
      countWords = len(choisedTheme["test"])
    self.updateUser(user, {
      "choisedTheme": choisedTheme,
      "countWords": countWords
    })

  def changeCountWordsOrRepeat(self, user, count, flag):
    self.updateUser(user, {flag: count})

  def msgController(self, userData, jsonThemes):
    user = self.getUser(userData.id)
    if user:
      # обновление темы в случае изменения json файла
      if user["choisedTheme"] not in jsonThemes.values():
        if user["choisedTheme"]["theme"] in list(
            map(lambda item: item["theme"], jsonThemes.values())):
          for iter in jsonThemes.values():
            if iter["theme"] == user["choisedTheme"]["theme"]:
              self.updateUser(user, {"choisedTheme": iter})
              break
        else:
          self.updateUser(user, {
            "choisedTheme": jsonThemes["study"],
            "countWords": 3
          })

    else:
      self.addUser(userData)

  def getWord(self, user):
    result = self.learning.find_one({
      "user": user["_id"],
      "word": user["lastWord"]
    })
    return result

  def addWord(self, user):
    lastTest = datetime.now(zone).strftime("%d.%m.%Y %H:%M")
    word = {
      "user": user["_id"],
      "word": user["lastWord"],
      "countTrue": 1,
      "lastRepeat": lastTest
    }
    self.learning.insert_one(word)

  def updateWord(self, word, value):
    self.learning.update_one({"_id": word["_id"]}, {"$set": value})

  def incWord(self, user):
    resWord = self.getWord(user)
    if (resWord):
      countTrue = resWord["countTrue"]
      countTrue += 1
      self.updateWord(resWord, {"countTrue": countTrue})
    else:
      self.addWord(user)

  def clearWord(self, user):
    resWord = self.getWord(user)
    if (resWord):
      self.learning.delete_one({"_id": resWord["_id"]})
      # self.updateWord(resWord, {"countTrue": 0, "lastRepeat": 0})

  def getCountLearnedWords(self, user):
    countRepeat = user["countRepeat"]
    countLearnedWords = 0
    words = self.learning.find({"user": user["_id"]})
    for word in words:
      if word["countTrue"] >= countRepeat:
        countLearnedWords += 1
    return countLearnedWords


# перенести отправку count из starttest в check или callback                              --- сделано
# сделать в callback отправку данных в бд                                                 --- сделано
# сделать отправку последнего прохождения теста                                           --- сделано
# сделать возможным смену количества слов в тесте и повторений                            --- сделано
# сделать возможным смену темы (для этого необходимо сделать еще один тест в json)        --- сделано
# вносить данные в таблицу learning                                                       --- сделано
