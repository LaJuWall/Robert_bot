# -*- coding:utf-8 -*-

import random
from random import randint
import socket
import time
from time import sleep
from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import sys
from nameCollector import collector
from nameCollector import suggestion

Config.set('graphics', 'width', '275')
Config.set('graphics', 'height', '275')

Builder.load_string('''
<bGround>:
    Label:
        opacity: 0
        pos: 0, 0
        text: root.startUp()

<theGui>:
    GridLayout:
        rows: 5
        cols: 2
        Label:
            text: 'Chosen suggestion:'
            font_size: 15
        Label:
            text: root.name
            font_size: 15
        Label:
            text: 'Recording time:'
            font_size: 15
        TextInput:

            id: timeInSeconds
            pos: 0, 0
            text: root.timeS
        Button:
            text: 'Start collecting'
            on_press: root.begin(timeInSeconds.text)
        Button:
            text: 'Pick a suggestion'
            on_press: root.chooseOne()
        Button:
            text: 'Update list'
            on_press: root.refreshScreen()
        TextInput:
            id: theList
            text: root.names
        Button:
            text: 'Clear the memory'
            on_press: root.cleanUp()
        Button:
            text: 'Settings'
            on_press: root.openSettings()

<wait_Content>:

    GridLayout:

        cols: 1
        rows: 1

        Button:
            text: 'START'
            on_press: root.startUp(root.myparent.myparent.kollector)

<optionsWindow>:

    GridLayout:

        cols: 2
        rows: 8

        Label:
            text: 'Channel:'

        TextInput:
            id: setChannel
            multiline: False
            text: root.CHN

        Label:
            text: 'Mode'

        TextInput:
            id: setMode
            multiline: False
            text: root.MOD

        Label:
            text: 'Keyword'

        TextInput:
            id: setKeyword
            multiline: False
            text: root.KWR

        Label:
            text: 'Allow messages?'

        TextInput:
            id: setMsgUsage
            multiline: False
            text: root.UMS

        Label:
            text: 'Starting message'

        TextInput:
            id: setStMessage
            multiline: False
            text: root.SMS

        Label:
            text: 'Ending message'

        TextInput:
            id: setEnMessage
            multiline: False
            text: root.EMS

        Label:
            text: 'Filters'

        TextInput:
            id: setFilters
            multiline: False
            text: root.FIL

        Button:
            text: 'Apply settings'
            on_press: root.updateSettings(setChannel.text, setMode.text, setKeyword.text, setMsgUsage.text, setStMessage.text, setEnMessage.text, setFilters.text)

        Button:
            text: 'Exit'
            on_press: root.myparent.closeDown()


''')

class wait_Content(BoxLayout):
    rTime = ''

    def startUp(self, kerain):
        timee = str(self.rTime)
        kerain.collectNames(timee)
        self.myparent.closeDown()
        return

    def __init__(self, parent, kerain, iTime):
        BoxLayout.__init__(self)
        self.myparent = parent
        self.status = 'START'
        self.rTime = iTime

class wait_Popup(Popup):
    def closeDown(self):
        self.myparent.refreshScreen()
        self.dismiss()

    def __init__(self, parent, kerain, rTime):
        self.myparent = parent
        Popup.__init__(self, title="Click the start button only once!", separator_color=[0.15, 0.15, 0.15, 0.15])
        self.content = wait_Content(self, kerain, rTime)

class optionsWindow(BoxLayout):
    CHN = StringProperty()
    MOD = StringProperty()
    KWR = StringProperty()
    UMS = StringProperty()
    SMS = StringProperty()
    EMS = StringProperty()
    FIL = StringProperty()

    def updateSettings(self, channel, mode, keyword, msgUsage, sMessage, eMessage, filters):
        onko = True
        if channel[0] != '#':
            self.CHN = "input was wrong! #example"
            onko = False
        if (mode == "Q") or (mode == "K"):
            print " "
        else:    
            self.MOD = "Insert Q or K"
            onko = False
        if len(keyword) < 1:
            keyword = "keyword"
        if (msgUsage == "Yes") or (msgUsage == "No"):
            print " "
        else:
            self.UMS = "Insert Yes or No"
            onko = False
        if len(sMessage) < 1:
            sMessage = " "
        if len(eMessage) < 1:
            eMessage = " "
        if len(filters) < 1:
            filters = " "
        if not onko:
            return
        self.myparent.myparent.updateSettings(channel, mode, keyword, msgUsage, sMessage, eMessage, filters)

    def __init__(self, parent):
        self.myparent = parent
        self.CHN = self.myparent.myparent.kollector.channel
        self.MOD = self.myparent.myparent.kollector.mode
        self.KWR = self.myparent.myparent.kollector.kWord
        if self.myparent.myparent.kollector.useMessages:
            self.UMS = "Yes"
        else:
            self.UMS = "No"
        self.SMS = self.myparent.myparent.kollector.stMessage
        self.EMS = self.myparent.myparent.kollector.enMessage
        for filt in self.myparent.myparent.kollector.filters:
            self.FIL = self.FIL + filt + ", "
        self.FIL = self.FIL[:(len(self.FIL) - 2)]
        BoxLayout.__init__(self)

class options_Popup(Popup):
    def closeDown(self):
        self.myparent.kollector.saveSettings()
        self.dismiss()

    def __init__(self, parent):
        self.myparent = parent
        Popup.__init__(self, title="Settings", separator_color=[0.15, 0.15, 0.15, 0.15])
        self.content = optionsWindow(self)

class theGui(FloatLayout):
    name = StringProperty()
    names = StringProperty()
    timeS = StringProperty()
    kollector = collector()

    def __init__(self, parent):
        self.kollector = collector()
        self.refreshScreen()
        self.timeS ='60'
        FloatLayout.__init__(self)
        self.myparent = parent
        
    def updateSettings(self, channel, mode, keyword, msgUsage, sMessage, eMessage, filters):
        self.kollector.updateSettings(channel, mode, keyword, msgUsage, sMessage, eMessage, filters)

    def openSettings(self):
        poppi = options_Popup(self)
        poppi.open()

    def begin(self, rTime):
        try:
            int(float(rTime))
        except ValueError:
            self.timeS = ' '
            self.timeS = 'That was not a number! You silly :P' 
            return
        poppi = wait_Popup(self, self.kollector, rTime)
        poppi.open()

    def chooseOne(self):
        self.kollector.pickOne()
        self.name = ' '
        self.name = self.kollector.sug.name

    def closeDown(self):
        sys.exit()

    def refreshScreen(self):
        self.names = ' '
        self.names = self.kollector.screenList
        self.name = ' '
        self.name = self.kollector.sug.name

    def cleanUp(self):
        self.kollector.cleanUp()
        self.refreshScreen()

class bGround(FloatLayout):

    def startUp(self):
        content = theGui(self)
        self.add_widget(content)
        return " "

class Robert_bot(App):

    def build(self):
        return bGround()

if __name__== '__main__':
    Robert_bot().run()