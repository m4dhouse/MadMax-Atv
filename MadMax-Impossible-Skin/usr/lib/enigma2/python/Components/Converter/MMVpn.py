from os import path, popen, listdir
from Components.Converter.Converter import Converter
from Components.Element import cached

class MMVpn(Converter):
	VPNLOAD = 0

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == 'vpn':
			self.type = self.VPNLOAD

	@cached
	def getBoolean(self):
		tun_vpn = False
		if "openvpn" in str(listdir("/var/run")):
			try:
				check_tun = popen("ip tuntap show").read().split()[0]
				if 'tun0:' in check_tun:
					tun_vpn = True
			except IndexError:
				pass
		if path.exists("/var/run/resolvconf/interfaces"):
			if "wg0" in str(listdir("/var/run/resolvconf/interfaces")):
				try:
					check_wireguard = popen("wg show").read().split()
					if "handshake:" in check_wireguard:
						tun_vpn = True
				except IndexError:
					pass
		return tun_vpn

	boolean = property(getBoolean)

	def changed(self, what):
		Converter.changed(self, what)
