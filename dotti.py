
import sys
import ast
import time
import struct

from connector import Connector
from logger import Logger as logger

class Dotti():
	"""
	DOTTI interfacing

	Small class that allow to set Hour mode or fill all pixel with a specific color 
	
	Requirements:
		- see https://github.com/MartyMacGyver/dotti-interfacing
	"""

	def __init__(self, mac):
		self.name = 'dotti'
		self.mac = mac

	def __twoDigitHex(self, number):
		return '%02x' % number

	def mode(self, mode = 'hour', color = [0, 0, 0]):
		"""
		Update Dotti to the given mode
		
		Args:
			mode (str): either 'hour' or 'color'
			color (arr[int, int, int]): R,G,B color to use
		"""

		conn = Connector(self.mac)
		conn.connect()

		if not conn.isconnected:
			conn.connect()
			if not conn.isconnected:
				return
		
		try:
			if mode == 'color':
				conn.writeCharacteristic('0x2a', '0601'+self.__twoDigitHex(int(color[0]))+self.__twoDigitHex(int(color[1]))+self.__twoDigitHex(int(color[2]))+'00')
			elif mode == 'hour':
				conn.writeCharacteristic('0x2a', '040502')

		except Exception as error:
			logger.error(str(error))

		conn.disconnect()
		return

"""
	Just for testing purpose without mqtt
"""
if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit("Usage:\n  %s <mac-address> [<hour|color>]" % sys.argv[0])

	device_mac = sys.argv[1]
	color = [0, 0, 0]

	if len(sys.argv) == 2:
		mode = 'hour'
	else:
		mode = str(sys.argv[2])

	if mode == 'color':
		if len(sys.argv) < 4:
			sys.exit("Usage:\n  %s <mac-address> color [r, g, b]" % sys.argv[0])

		color = ast.literal_eval(sys.argv[3])
	
	# start the magic
	dotti = Dotti(device_mac)
	dotti.mode(mode, color)
