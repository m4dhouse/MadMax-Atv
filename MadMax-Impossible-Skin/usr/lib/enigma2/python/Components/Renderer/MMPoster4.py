# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import iPlayableServicePtr, eServiceReference
from enigma import ePixmap, ePicLoad, eTimer
try:
    from urllib.request import urlopen, quote
except ImportError:
    from urllib2 import urlopen, quote
import json, os, re, socket
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists

folder_path = "/tmp/MMPoster/"

api_key = 'f23c2bd91113daf777dcba03990aea77'
leng = open('/tmp/language.txt', 'r').readline().replace('config.osd.language=', '').replace('_', '-').replace('\n', '')

class MMPoster4(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.timer10 = eTimer()

    def intCheck(self):
        try:
            socket.setdefaulttimeout(0.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return False

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

    def infos(self):
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
        rep_name = ["(", ")", "[", "]", "u-", "3d", "-", "'", " S01 ", " S02 ", " S03 ", " S04 ", " S05 ", " S06 ", " S07 ", " S08 ", " S09 ", " S10 ", " S11 ", " S12 ", " S13 ", " S14 ",
                     " S15 ", " S16 ", "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14",  "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", ]
        for j in range (1900, 2025):
            rep_name.append(str(j))

        for i in rep_name:
            name = name.replace(i, '')
        if service or info:
            evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)", "", str(name))
            self.evntNm = evntN
            self.pstrNm = "/tmp/MMPoster/{}.jpg".format(self.evntNm)
            if self.intCheck():
                try:
                    self.instance.hide()
                    url = 'http://api.themoviedb.org/3/search/tv?api_key={}&query={}'.format(api_key,quote(self.evntNm))
                    url2 = urlopen(url).read().decode('utf-8')
                    jurl = json.loads(url2)
                    if 'results' in jurl:
                        if 'id' in jurl['results'][0]:
                            ids = jurl['results'][0]['id']
                    url_2 = 'http://api.themoviedb.org/3/tv/' + str(ids) + '?api_key={}&language={}'.format(api_key,str(leng))
                    url_3 = urlopen(url_2).read().decode('utf-8')
                    data2 = json.loads(url_3)
                    poster = data2['poster_path']
                    if poster:
                        self.url_poster = "http://image.tmdb.org/t/p/w185{}".format(poster)
                        self.savePoster()
                    self.timer10.stop()
                except:
                    try:
                        self.instance.hide()
                        url = 'http://api.themoviedb.org/3/search/movie?api_key={}&query={}'.format(api_key,quote(self.evntNm))
                        url2 = urlopen(url).read().decode('utf-8')
                        jurl = json.loads(url2)
                        if 'results' in jurl:
                            if 'id' in jurl['results'][0]:
                                ids = jurl['results'][0]['id']
                        url_2 = 'http://api.themoviedb.org/3/movie/' + str(ids) + '?api_key={}&language={}'.format(api_key,str(leng))
                        url_3 = urlopen(url_2).read().decode('utf-8')
                        data2 = json.loads(url_3)
                        poster = data2['poster_path']
                        if poster:
                            self.url_poster = "http://image.tmdb.org/t/p/w185{}".format(poster)
                            self.savePoster()
                        self.timer10.stop()
                    except:
                        self.timer10.stop()
                        pass
            else:
                return

    def delay(self):
        self.downloading = False
        try:
            self.timer10.callback.append(self.infos)
        except:
            self.timer10_conn = self.timer10.timeout.connect(self.infos)
        self.timer10.start(450, False)

    def showPoster(self):
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
                size = self.instance.size()
                self.picload = ePicLoad()
                sc = AVSwitch().getFramebufferScale()
                if self.picload:
                    self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'))
                result = self.picload.startDecode(self.pstrNm, 0, 0, False)
                if result == 0:
                    ptr = self.picload.getData()
                    if ptr != None:
                        self.instance.setPixmap(ptr)
                        self.instance.show()
                else:
                    self.instance.hide()

    def savePoster(self):
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        try:
            pic_image = urlopen(self.url_poster)
            respimage = pic_image.read()
            image = open(self.pstrNm, "wb")
            image.write(respimage)
            image.close()
            self.showPoster()
        except:
            pass
