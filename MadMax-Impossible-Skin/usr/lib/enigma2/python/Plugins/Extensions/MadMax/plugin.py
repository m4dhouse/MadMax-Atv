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
from requests import exceptions, get

Python = sys.version_info.major
PY3 = False
if Python == 3:
	PY3 = True

Header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

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
		link = get(url, headers=Header, allow_redirects=True, timeout=(3, 2))
		if link.status_code == 200 and link.content:
			return link.content
		else:
			print("[DownloadInfo] Error: DownloadInfo lookup returned a status code of %d!" % link.status_code)
			return
	except exceptions.RequestException as err:
		print("[DownloadInfo] Error: DownloadInfo server connection failure! (%s)" % str(err))
	except ValueError:
		print("[DownloadInfo] Error: DownloadInfo data returned can not be processed!")
	except Exception as err:
		print("[DownloadInfo] Error: Unexpected error! (%s)" % str(err))

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
		self.VerGit = ""
		self.downvr = DownloadInfo('https://github.com/m4dhouse/MadMax-Atv/raw/main/version')
		try:
			if float(self.downvr) > float(version):
				if PY3:
					self.VerGit = str(self.downvr, "utf-8")
				else:
					self.VerGit = str(self.downvr)
				self.session.openWithCallback(self.down_inst, MessageBox, _('New version available!\n\nMadMax Impossible Skin update'), MessageBox.TYPE_INFO, timeout=5, default=True)
			elif float(self.downvr) == float(version):
				self.session.open(MessageBox, _('No updates available!'), MessageBox.TYPE_INFO, timeout=5)
				self.close()
		except Exception as error:
			print("Error", error)

	def down_inst(self, result):
		os.system('mkdir -p /tmp/madmax')
		if bool(self.VerGit):
			try:
				self.dlfile = '/tmp/madmax/madmax.ipk'
				url_ipk = 'https://github.com/m4dhouse/MadMax-Atv/blob/main/'
				self.updateoea = url_ipk + 'enigma2-plugin-skins-madmax-impossible_' + self.VerGit + '_all.ipk?raw=true'
				self.download = downloadWithProgress(self.updateoea, self.dlfile)
				self.download.addProgress(self.downloadProgress)
				self.download.start().addCallback(self.instSkin).addErrback(self.downloadfailed)
			except:
				pass
		else:
			pass

	def instSkin(self, string = ''):
		cmd4 = 'opkg --force-downgrade --force-reinstall --force-overwrite install /tmp/madmax/madmax.ipk'
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
