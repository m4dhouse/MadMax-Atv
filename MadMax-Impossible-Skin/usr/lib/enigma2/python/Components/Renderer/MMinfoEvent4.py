# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad, eTimer, iPlayableServicePtr, eServiceReference
import re
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists

class MMinfoEvent4(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.timer10 = eTimer()

    GUI_WIDGET = ePixmap
    def changed(self, what):
        try:
            refer = self.source.serviceref.toString()
            if refer.startswith('4097'):
                if what[0] == self.CHANGED_CLEAR:
                    self.instance.hide()
                if what[0] != self.CHANGED_CLEAR:
                    self.delay()
            else:
                if refer.startswith('5002'):
                    if what[0] == self.CHANGED_CLEAR:
                        self.instance.hide()
                    if what[0] != self.CHANGED_CLEAR:
                        self.delay()
                else:
                    pass
        except:
            pass

    def info(self):
        if self.downloading:
            return
        self.downloading = True
        service = self.source.service
        info = None
        if isinstance(service, iPlayableServicePtr):
            info = service and service.info()
            service = None
        if not info:
            return ''
        name = service and info.getName(service)
        if name is None:
            name = info.getName()
        name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
        rep_name = ["sd", "hd", "fhd", "uhd", "4k", "vod", "1080p", "720p", "blueray", "x264", "aac", "ozlem", "hindi", "hdrip", "(cache)", "(kids)", "[3d-en]", "[iran-dubbed]", "imdb", "top250", "multi-audio",
                     "multi-subs", "multi-sub", "[audio-pt]", "[nordic-subbed]", "[nordic-subbeb]",

                     "ae:", "al:", "ar:", "at:", "ba:", "be:", "bg:", "br:", "cg:", "ch:", "cz:", "da:", "de:", "dk:", "ee:", "en:", "es:", "ex-yu:", "fi:", "fr:", "gr:", "hr:", "hu:", "in:", "ir:", "it:", "lt:", "mk:",
                     "mx:", "nl:", "no:", "pl:", "pt:", "ro:", "rs:", "ru:", "se:", "si:", "sk:", "tr:", "uk:", "us:", "yu:",

                     "[ae]", "[al]", "[ar]", "[at]", "[ba]", "[be]", "[bg]", "[br]", "[cg]", "[ch]", "[cz]", "[da]", "[de]", "[dk]", "[ee]", "[en]", "[es]", "[ex-yu]", "[fi]", "[fr]", "[gr]", "[hr]", "[hu]", "[in]", "[ir]", "[it]", "[lt]", "[mk]",
                     "[mx]", "[nl]", "[no]", "[pl]", "[pt]", "[ro]", "[rs]", "[ru]", "[se]", "[si]", "[sk]", "[tr]", "[uk]", "[us]", "[yu]",

                     "-ae-", "-al-", "-ar-", "-at-", "-ba-", "-be-", "-bg-", "-br-", "-cg-", "-ch-", "-cz-", "-da-", "-de-", "-dk-", "-ee-", "-en-", "-es-", "-ex-yu-", "-fi-", "-fr-", "-gr-", "-hr-", "-hu-", "-in-", "-ir-", "-it-", "-lt-", "-mk-",
                     "-mx-", "-nl-", "-no-", "-pl-", "-pt-", "-ro-", "-rs-", "-ru-", "-se-", "-si-", "-sk-", "-tr-", "-uk-", "-us-", "-yu-",

                     "|ae|", "|al|", "|ar|", "|at|", "|ba|", "|be|", "|bg|", "|br|", "|cg|", "|ch|", "|cz|", "|da|", "|de|", "|dk|", "|ee|", "|en|", "|es|", "|ex-yu|", "|fi|", "|fr|", "|gr|", "|hr|", "|hu|", "|in|", "|ir|", "|it|", "|lt|", "|mk|",
                     "|mx|", "|nl|", "|no|", "|pl|", "|pt|", "|ro|", "|rs|", "|ru|", "|se|", "|si|", "|sk|", "|tr|", "|uk|", "|us|", "|yu|",

                     "(", ")", "[", "]", "u-", "3d", "-", "'", " S01 ", " S02 ", " S03 ", " S04 ", " S05 ", " S06 ", " S07 ", " S08 ", " S09 ", " S10 ", " S11 ", " S12 ", " S13 ", " S14 ",
                     " S15 ", " S16 ", "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14",  "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", ]
        for j in range (1900, 2025):
            rep_name.append(str(j))

        for i in rep_name:
            name = name.replace(i, '')
        if service or info:
            evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)", "", str(name))
            self.evntNm = evntN
            self.pstrNm = "/tmp/MMPoster/{}.jpg".format(self.evntNm)
            if fileExists(self.pstrNm):
                self.showPoster()
                self.timer10.stop()
            else:
                self.instance.hide()
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
