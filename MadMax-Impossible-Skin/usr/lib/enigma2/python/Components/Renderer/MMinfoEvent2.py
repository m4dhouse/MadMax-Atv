# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, ePicLoad, eTimer
try:
    from urllib.request import urlopen, quote
except ImportError:
    from urllib2 import urlopen, quote
import json, re, os, socket, shutil
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists

folder_path = "/tmp/MMPoster/"

try:
    folder_size=sum([sum(map(lambda fname: os.path.getsize(os.path.join(folder_path, fname)), files)) for folder_path, folders, files in os.walk(folder_path)])
    mmposter = "%0.f" % (folder_size/(1024*1024.0))
    if mmposter >= "5":
        shutil.rmtree(folder_path)
except:
    pass

api_key = 'f23c2bd91113daf777dcba03990aea77'
os.system("cat /etc/enigma2/settings | grep config.osd.language|sed '/^config.osd.language=/!d' > /tmp/language.txt")
leng = open('/tmp/language.txt', 'r').readline().replace('config.osd.language=', '').replace('_', '-').replace('\n', '')

class MMinfoEvent2(Renderer):

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
                if self.intCheck():
                    try:
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
        if os.path.exists(self.pstrNm):
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
        if not os.path.exists(folder_path):
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
