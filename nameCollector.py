# -*- coding:utf-8 -*-

import socket
import random
import os
import time
import sys
from time import sleep
from random import randint
import re

#Todo
#Metodit: kMode, qMode, makeScreenList, makeSugList
#
#

class suggestion:
    name = ""
    count = 0

    def __repr__(self):
        return self.name + " - " + str(self.count)

    def __str__(self):
        return self.name + " - " + str(self.count)

    def __init__(self, name):
        self.name = name
        self.count = 0

class collector:

    def saveSettings(self):
        location = os.getcwd()
        location = location + '\\' + 'settings.txt'
        sFilu = open(location, 'w')
        sFilu.write("# CHN = Channel were the software connects. example #lazu_ or #vargskelethor\n")
        sFilu.write("# MOD = Colecting mode. This value uses only K or Q. K stands for keyword mode, where the software picks up suggestions if they follow a certain keyword and Q is for quote mode, where the software picks up suggestions in quotes.\n")
        sFilu.write("# KWD = keyword. The keyword you want the software to recognize while using the keyword mode. ONLY USE ASCII CHARACTERS IN YOUR KEYWORD!!!\n")
        sFilu.write("# MES = Use start and end messages. This value takes Y or N (Yes or No). If it's Y, the software will send messages to chat when it starts or stops collecting suggestions.\n")
        sFilu.write("# SME = Starting message. This is the message that the software will send to chat when it starts collecting suggestions. the %s stands for the spot where the collecting time (in seconds) will be shown.\n")
        sFilu.write("# EME = Ending message. This is the message that the software will send to chat when it stops collecting suggestions.\n")
        sFilu.write("# FIL = Filters. Every line under this is meant for suggestions that will bw filtered from the results. Write them all in lowercase.\n")
        sFilu.write("CHN:" + self.channel + "\n")
        sFilu.write("MOD:" + self.mode + "\n")
        sFilu.write("KWD:" + self.kWord + "\n")
        if self.useMessages:
            sFilu.write("MES:Y\n")
        else:
            sFilu.write("MES:N\n")
        sFilu.write("SME:" + self.stMessage + "\n")
        sFilu.write("EME:" + self.enMessage + "\n")
        sFilu.write("FIL:\n")
        for filt in self.filters:
            sFilu.write(filt + "\n")
        return

    def giveInfo(self):
        print "valittu suggi on: " + self.sug.name
        print "ruutuun tuleva lista on: " + self.screenList
        print self.sugList
        print "Tallessa oleva data on: "
        print self.backUp

    def isUnicode(self, text):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return True
        except UnicodeEncodeError:
            return True
        else:
            return False

    def cleanNonLetters(self, text):
        howLong = len(text)
        howLong -= 1
        i = 0
        switch = 0
        while i < howLong:
            char = text[i]
            uChar = unicode(char)
            try:
                char.decode('ascii')
            except UnicodeEncodeError or UnicodeDecodeError:
                if (u'ä' == uChar) or (u'ö' == uChar):
                    i += 1
                    continue
                else:
                    text = text.replace(char, "")
                    howLong -=1
            else:
                i += 1
                continue
        return text

    def cleanQList(self):
        goOn = True
        returnList = []
        aakkonen = False
        while goOn:
            aakkonen = False
            inspected = self.nameList[0]
            indx = inspected.find('"')
            inspected = inspected[(indx+1):len(inspected)]
            indx = inspected.find('"')
            if indx == -1:
                self.nameList.pop(0)
                if len(self.nameList) == 0:
                    goOn = False
                continue
            inspected = inspected[:indx]
            uinspect = unicode(inspected.lower())
            if (u'ä' in uinspect) or (u'ö' in uinspect):
                aakkonen = True
            if aakkonen:
                inspected = self.cleanNonLetters(inspected)
            if not aakkonen:
                if self.isUnicode(inspected):
                    self.nameList.pop(0)
                    if len(self.nameList) == 0:
                        goOn = False
                    continue
            if len(inspected) < 1:
                self.nameList.pop(0)
                if len(self.nameList) == 0:
                    goOn = False
                continue
            returnList.append(inspected)
            self.nameList.pop(0)
            if len(self.nameList) == 0:
                goOn = False
        if len(returnList) < 1:
            self.nameList = ['nothing found']
            return
        self.nameList = returnList

    def qMode(self, int_recordTime, start_time):
        #self.nameList= ['He-man', 'Joel', 'Joel', 'Lazu', 'Vinny', 'vinny', 'Lazu', 'Joel', 'Bonzi', 'Joel', 'Lazu']
        goOn = True
        while goOn:
            try:
                response = self.s.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                self.s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            if '"' in response:
                self.nameList.append(response)
            time_now = time.time()
            time_spent = time_now - start_time
            int_timeSpent = int(time_spent)
            self.timeLeft = str(int_recordTime - int_timeSpent)
            if int_timeSpent > int_recordTime:
                goOn = False
        if len(self.nameList) < 1:
            self.nameList.append('nothing found')
        else:
            self.cleanQList()

    def cleanTodo(self, todo, tunniste):
        for msg in todo:
            msg = msg[1:]
            indx = msg.find(':')
            msg = msg[(indx + 1):]
            if msg.startswith(tunniste):
                msg = msg[(len(self.kWord) + 1):-2]
                msg = self.cleanNonLetters(msg)
                if len(msg) < 1:
                    continue
                self.nameList.append(msg)

    def kMode(self, int_recordTime, start_time):
        #self.nameList= ['He-man', 'Joel', 'Joel', 'Lazu', 'Vinny', 'Joel', 'Bonzi', 'Joel']
        goOn = True
        MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
        tunniste = self.kWord + ' '
        todo = []
        while goOn:
            try:
                response = self.s.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                continue
            if response == "PING :tmi.twitch.tv\r\n":
                self.s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            try:
                cMessage = str(MSG.sub('', response))
                if cMessage.startswith(tunniste):
                    self.nameList.append(cMessage[(len(self.kWord) + 1):-2])
            except UnicodeEncodeError:
                uRespo = unicode(response)
                if (u'ä' in uRespo) or (u'ö' in uRespo):
                    todo.append(response)
            time_now = time.time()
            time_spent = time_now - start_time
            int_timeSpent = int(time_spent)
            self.timeLeft = str(int_recordTime - int_timeSpent)
            if int_timeSpent > int_recordTime:
                goOn = False
        if len(todo) > 0:
            self.cleanTodo(todo, tunniste)
        if len(self.nameList) < 1:
            self.nameList.append('nothing found')
    
    def tMode(self, int_recordTime, start_time):
        ehdotukset = ['Joel', 'Vinny', 'Lazu', 'Rev', 'Rampenator', 'Wilberssi', 'Robert_Cop', 'Bonzi buddy', 'Skeletor', 'Funeris']
        goOn = True
        while goOn:
            try:
                response = self.s.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                continue
            luku = randint(0,9)
            if response == "PING :tmi.twitch.tv\r\n":
                self.s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            if 'Kappa' in response:
                self.nameList.append(ehdotukset[luku])
            if 'kappa' in response:
                self.nameList.append(ehdotukset[luku])
            if 'PogChamp' in response:
                self.nameList.append(ehdotukset[luku])
            if 'ResidentSleeper' in response:
                self.nameList.append(ehdotukset[luku])
            if 'ulti' in response:
                self.nameList.append(ehdotukset[luku])
            if 'auto' in response:
                self.nameList.append(ehdotukset[luku])
            if 'Kreygasm' in response:
                self.nameList.append(ehdotukset[luku])
            if '"' in response:
                self.nameList.append(ehdotukset[luku])
            time_now = time.time()
            time_spent = time_now - start_time
            int_timeSpent = int(time_spent)
            self.timeLeft = str(int_recordTime - int_timeSpent)
            if int_timeSpent > int_recordTime:
                goOn = False
        if len(self.nameList) < 1:
            self.nameList.append('nothing found')

    def makeScreenList(self):
        self.screenList = ''
        counter = 1
        for member in self.sugList:
            entry = str(counter) + '. ' + member.name + ' - ' + str(member.count) + '\n'
            counter += 1
            self.screenList = self.screenList + entry

    def makeSugList(self):

        goOn_1 = True
        while goOn_1:
            try:
                sugge = suggestion(self.nameList[0])
            except IndexError:
                # nameList on tyhja, sugList on valmis
                goOn_1 = False
                continue
            self.countEm(sugge)
            self.sugList.append(sugge)

    def countEm(self, sugge):
        goOn_2 = True
        indx = 0
        while goOn_2:
                try:
                    if sugge.name.lower() == self.nameList[indx].lower():
                        sugge.count += 1
                        self.nameList.pop(indx)
                        continue
                    indx += 1
                except IndexError:
                # kaikki nimet on tarkistettu
                    goOn_2 = False
                    continue

    def isUnicode(self, text):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return True
        except UnicodeEncodeError:
            return True
        else:
            return False
    
    def filterEm(self):

        goOn = True
        indx = 0
        while goOn:
            try:
                #if (self.nameList[indx].lower() in self.filters) or (self.isUnicode(self.nameList[indx])):
                if (self.nameList[indx].lower() in self.filters): 
                    self.nameList.pop(indx)
                else:
                    indx += 1
            except IndexError:
                goOn = False
        if len(self.nameList) < 1:
            self.nameList.append('Nothing found')

    def collectNames(self, recordTime):
        self.sugList = []
        self.nameList = []
        if (len(self.backUp) < 1) or (self.backUp[0] == 'Nothing found'):
            self.backUp = []
            self.freshSearch = True
        if len(self.backUp) > 0:
            self.freshSearch = False
        if self.useMessages:
            if '%s' in self.stMessage:
                message = self.stMessage % recordTime
            else:
                message = self.stMessage
            self.s.send('PRIVMSG ' + self.channel + ' :' + message + '\r\n')
        int_recordTime = int(float(recordTime))
        start_time = time.time()
        if self.mode == 'K':
            self.kMode(int_recordTime, start_time)
        if self.mode == 'Q':
            self.qMode(int_recordTime, start_time)
        if self.mode == 'T':
            self.tMode(int_recordTime, start_time)
        if self.useMessages:
            message = self.enMessage
            self.s.send('PRIVMSG ' + self.channel + ' :' + message + '\r\n')
        if self.nameList[0] == 'nothing found':
            if self.freshSearch:
                self.sugList = [suggestion('nothing found')]
                self.sug = self.sugList[0]
                self.makeScreenList()
                return
            else:
                self.nameList = list(self.backUp)
                self.makeSugList()
                self.makeScreenList()
                self.sug = self.sugList[0]
                return
        self.filterEm()
        self.nameList = self.nameList + self.backUp
        self.backUp = list(self.nameList)
        self.makeSugList()
        self.sugList = sorted(self.sugList, key=lambda sug: sug.count, reverse=True)
        self.makeScreenList()
        self.sug = self.sugList[0]

    def pickOne(self):
        if len(self.sugList) < 1:
            self.sug = suggestion('No names to choose from...')
        else:
            randRange = len(self.sugList) - 1
            number = random.randint(0, randRange)
            self.sug = self.sugList[number] 

    def cleanUp(self):
        self.sug = suggestion('-')
        self.sugList = [self.sug]
        self.backUp = []
        self.screenList = '-\n-\n-'
        self.timeLeft = '0'

    def listFilters(self, userInput):
        goOn = True
        li = []
        while goOn:
            indx = userInput.find(',')
            if indx < 0:
                li.append(userInput.lower())
                goOn = False
                continue
            li.append((userInput[:(indx)]).lower())
            try:
                userInput = userInput[(indx + 2):]
            except IndexError:
                goOn = False
                continue
        print li
        return li

    def updateSettings(self, channel, mode, keyword, msgUsage, sMessage, eMessage, filters):
        self.channel = channel
        if mode[0] == 'Q':
            print "Q BONGATTU!"
            self.mode = 'Q'
            print self.mode
        if mode[0] == 'K':
            print "K BONGATTU!"
            self.mode = 'K'
        self.kWord = keyword
        if msgUsage == "Yes":
            self.useMessages = True
        if msgUsage == "No":
            self.useMessages = False
        self.stMessage = sMessage
        self.enMessage = eMessage
        li = self.listFilters(filters)
        self.filters = li

    def loadSettings(self):
        location = os.getcwd()
        location = location + '\\' + 'settings.txt'
        sFilu = open(location, 'r')
        goOn = True
        li = []
        
        while goOn:
            fLine = sFilu.readline()
            if fLine == '':
                sFilu.close()
                goOn = False
                continue
            if fLine.startswith('#'):
                continue
            if fLine.startswith('CHN:'):
                self.channel = fLine[4:-1]
                continue
            if fLine.startswith('MOD:'):
                if fLine[4] == "Q":
                    self.mode = 'Q'
                if fLine[4] == "K":
                    self.mode = 'K'
                if fLine[4] == "T":
                    self.mode = 'T'
                continue
            if fLine.startswith('KWD:'):
                self.kWord = fLine[4:-1]
                continue
            if fLine.startswith('MES:'):
                if fLine[4] == "Y":
                    self.useMessages = True
                if fLine[4] == "N":
                    self.useMessages = False
                continue
            if fLine.startswith('SME:'):
                self.stMessage = fLine[4:-1]
                continue
            if fLine.startswith('EME'):
                self.enMessage = fLine[4:-1]
                continue
            if fLine.startswith('FIL'):
                continue
            if fLine.endswith('\n'):
                li.append((fLine[:-1]).lower())
            else:
                li.append(fLine)

            if len(li) < 1:
                li.append('abc', '123')

            self.filters = li

# Olion kaynnistyessa maaritetaan muuttujat ja luodaan socketti twitchiin
    
    def __init__(self):
        self.sug = suggestion('-')
        self.sugList = [self.sug]
        self.nameList = []
        self.backUp = []
        self.screenList = '-\n-\n-'
        self.timeLeft = '0'
        self.filters = []
        self.channel = '#lazu_'
        self.useMessages = True
        self.stMessage = 'Starting to collect names'
        self.enMessage = 'Stopped collecting names'
        self.mode = 'Q'
        self.kWord = 'name'
        self.freshSearch = True
        self.loadSettings()

        HOST = "irc.twitch.tv"
        PORT = 6667
        NICK = "insert your twitch username here"
        PASS = "insert your twitch accounts streamkey here"
        CHAN = self.channel

        self.s = socket.socket()
        self.s.connect((HOST, PORT))
        self.s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        self.s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        self.s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))

"""

kollektori = collector()

print "This is the test UI."
print "[1_time] => start collecting names for set time [1_60]"
print "2 => Show collector status"
print "3 => Pick a new name"
print "4 => Show all the names"
print "5 => Clear the memory"
print "6 => Exit the program"

while True:
    syotto = raw_input('>>')
    if syotto[0] == "1":
        aika = syotto[2:]
        kollektori.collectNames(aika)
    if syotto == "2":
        print "randRangettu nimi on: " + kollektori.nimi
        print "Napatut nimet on:\n" + kollektori.nimet
    if syotto == "3":
        kollektori.arvoNimi()
        print "Uusi nimi on: " + kollektori.nimi
    if syotto == "4":
        print "Napatut nimet on: " + kollektori.nimet
    if syotto == "5":
        kollektori.cleanUp()
    if syotto == "6":
        sys.exit()

"""