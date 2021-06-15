# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad, eTimer
import re
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists

class MMinfoEvent3(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.timer10 = eTimer()

    GUI_WIDGET = ePixmap
    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            self.delay()

    def info(self):
        if self.downloading:
            return
        self.downloading = True
        self.event = self.source.event
        if self.event:
            evnts = self.event.getEventName()
            evnt = evnts.replace('FILM ', '').replace('FILM - ', '').replace('film - ', '').replace('TELEFILM ', '').replace('TELEFILM - ', '').replace('telefilm - ', '')
            evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", evnt).rstrip()
            self.evntNm = evntN
            self.pstrNm = "/tmp/MMPoster/{}.jpg".format(self.evntNm)
            if fileExists(self.pstrNm):
                self.showPoster()
                self.timer10.stop()
            else:
                self.instance.hide()
#                self.showPosters()
                self.timer10.stop()
        else:
            self.instance.hide()
#            self.showPosters()
            self.timer10.stop()

    def delay(self):
        self.downloading = False
        try:
            self.timer10.callback.append(self.info)
        except:
            self.timer10_conn = self.timer10.timeout.connect(self.info)
        self.timer10.start(450, False)

    def showPoster(self):
        self.bord_cover = '/usr/share/enigma2/MadMax/box/mmcase_bluray.png'
        size = self.instance.size()
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        if self.picload:
            self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'))
        result = self.picload.startDecode(self.bord_cover, 0, 0, False)
        if result == 0:
            ptr = self.picload.getData()
            if ptr != None:
                self.instance.setPixmap(ptr)
                self.instance.show()
        else:
            self.instance.hide()

    def showPosters(self):
        self.bord_nocover = '/usr/share/enigma2/MadMax/box/mmcase_bluray_nocover.png'
        size = self.instance.size()
        self.picload = ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        if self.picload:
            self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'))
        result = self.picload.startDecode(self.bord_nocover, 0, 0, False)
        if result == 0:
            ptr = self.picload.getData()
            if ptr != None:
                self.instance.setPixmap(ptr)
                self.instance.show()
        else:
            self.instance.hide()
