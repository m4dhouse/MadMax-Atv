#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
import sys
from Components.Sources.Progress import Progress
from Tools.Downloader import downloadWithProgress
from Tools.Directories import SCOPE_LANGUAGE, resolveFilename
from Components.Language import language
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
import gettext
try:
    py_version = sys.version_info.major
except:
    py_version = 3
try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, Request, HTTPError, URLError

version = open('/usr/share/enigma2/MadMax/version','r').read()

PluginLanguageDomain = 'madmax'
PluginLanguagePath = '/usr/lib/enigma2/python/Plugins/Extensions/MadMax/locale'

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE, ''))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext('enigma2', txt)
    return t

localeInit()
language.addCallback(localeInit)

skin_madmax = """
        <screen name="updatemadmax" position="center,center" size="600,60" backgroundColor="#ff000000" flags="wfNoBorder">
          <widget source="progress" zPosition="1" render="Progress" position="0,0" size="600,60" transparent="1" borderWidth="0" backgroundColor="#ff000000" foregroundColor="#49bbff" />
          <widget source="progresstext" render="Label" position="0,0" zPosition="1" font="Regular;40" valign="center" halign="center" transparent="1" size="600,60" foregroundColor="#ffffff" backgroundColor="#ff000000" />
        </screen>"""

def DownloadInfo(url):
    try:
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urlopen(req)
        if py_version == 2:
            link = response.read()
        else:
            link = response.read().decode('utf-8')
        return link
    except URLError as e:
        print('URL Error: ', e.reason)
    except HTTPError as e:
        print('HTTP Error code: ', e.code)
    response.close()

class updatemadmax(Screen):
    def __init__(self, session):
        self.session = session
        self.skin = skin_madmax
        Screen.__init__(self, session)
        self['progress'] = Progress()
        self['progresstext'] = StaticText()
        self['actions'] = ActionMap(['SetupActions',
         'ColorActions'], {'exit': self.close,
         'red': self.close,
         'cancel': self.close}, -1)
        self.onFirstExecBegin.append(self.Update)

    def Update(self):
        file_vers = open('/usr/share/enigma2/MadMax/version', 'r').read()
        try:
            read_version_git = 'http://raw.githubusercontent.com/m4dhouse/MadMax-Atv/main/version.txt'
            self.update_version = DownloadInfo(read_version_git)
            if float(self.update_version) > float(file_vers):
                self.session.openWithCallback(self.down_inst, MessageBox, _('New version available!\n\nMadMax Impossible Skin update'), MessageBox.TYPE_INFO, timeout=5, default=True)
            elif float(self.update_version) == float(file_vers):
                self.session.open(MessageBox, _('No updates available!'), MessageBox.TYPE_INFO, timeout=5)
                self.close()
        except:
            pass

    def down_inst(self, result):
        os.system('mkdir -p /tmp/madmax')
        try:
            self.dlfile = '/tmp/madmax/madmax.ipk'
            url_ipk = 'http://raw.githubusercontent.com/m4dhouse/MadMax-Atv/main/'
            self.updateoea = url_ipk + 'enigma2-plugin-skins-madmax-impossible_' + str(self.update_version) + '_all.ipk'
            self.download = downloadWithProgress(self.updateoea, self.dlfile)
            self.download.addProgress(self.downloadProgress)
            self.download.start().addCallback(self.instSkin).addErrback(self.downloadfailed)
        except:
            pass

    def instSkin(self, string = ''):
        cmd4 = 'opkg --force-maintainer --force-reinstall --force-overwrite --force-downgrade install /tmp/madmax/madmax.ipk'
        self.session.openWithCallback(self.pre_gui, Console, title=_('Update MadMax Skin...'), cmdlist=[cmd4], closeOnSuccess=True)

    def pre_gui(self, string=""):
        self.session.openWithCallback(self.gui_restart, MessageBox, _('For the changes to take effect\nDo you want to restart the GUI?'))

    def downloadfailed(self, string = ''):
        self.session.open(MessageBox, _('Download Failed!'), MessageBox.TYPE_INFO, timeout=5)

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def gui_restart(self, result):
        os.remove('/tmp/madmax/madmax.ipk')
        if result:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

def main(session, **kwargs):
    try:
        socket.setdefaulttimeout(5.0)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        session.open(updatemadmax)
    except:
        self.session.open(MessageBox, _("1) Check the LAN cable behind the Stb\n\n2) Check the Internet connection\n\n3) Reopen MadMax"), MessageBox.TYPE_INFO)

def Plugins(**kwargs):
    list = []
    list.append(PluginDescriptor(name=(_('MadMax Skin version installed %s') % version), description=_('Check for updates online'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main))
    list.append(PluginDescriptor(name=(_('MadMax Skin version installed %s') % version), description=_('Check for updates online'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main))
    return list
