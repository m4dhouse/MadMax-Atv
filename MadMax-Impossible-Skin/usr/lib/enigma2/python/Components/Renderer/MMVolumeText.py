# -*- coding: utf-8 -*-
# by digiteng...09.2020, 10.2020
# <widget render="FroidLiveVolumeText" source="global.CurrentTime" position="42,9" size="200,22" font="Regular; 18" zPosition="3" backgroundColor="background" transparent="1" />
from Components.Renderer.Renderer import Renderer
from enigma import eLabel, eTimer, ePoint, eDVBVolumecontrol
from Components.VariableText import VariableText
from skin import parseColor

class MMVolumeText(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.text = ""

		self.vol_timer = eTimer()
		self.vol_timer.callback.append(self.pollme)

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for attrib, value in self.skinAttributes:
			if attrib == "position":
				self.x = value.split(",")[0]
				self.y = value.split(",")[1]

		self.skinAttributes = attribs
		ret = Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = eLabel
	def changed(self, what):
		if not self.suspended:
			val = eDVBVolumecontrol.getInstance().getVolume()
			sz = self.instance.size().width()
			if val > 0:
				self.instance.clearForegroundColor()
				loc = int(sz/(100.0/val))
			else:
				loc = 0
				self.instance.setForegroundColor(parseColor("#ff2626"))

			self.instance.setHAlign(eLabel.alignLeft)
			actvLoc = ePoint(loc + int(self.x), int(self.y))
			self.instance.move(actvLoc)
			self.instance.show()
			self.text = str(val)

	def pollme(self):
		self.changed(None)
		return

	def onShow(self):
		self.suspended = False
		self.vol_timer.start(200)

	def onHide(self):
		self.suspended = True
		self.vol_timer.stop()
