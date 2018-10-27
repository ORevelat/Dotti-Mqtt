import time
import struct
import bluepy.bluepy.btle as btle

from logger import Logger as logger

class Connector():
	"""
	This class is from the Jeedom plugin BLEA

	Just removed not necessary code.	
	"""

	def __init__(self,mac):
		self.name = 'connector'
		self.mac = mac
		self.conn = ''
		self.isconnected = False

	def connect(self, retry=3):
		logger.debug('CONNECTOR------Connecting : '+str(self.mac))
		i=0
		timeout = time.time() + 15
		while time.time()<timeout:
			i = i + 1
			try:
				connection = btle.Peripheral(self.mac, btle.ADDR_TYPE_PUBLIC)
				self.isconnected = True
				break
			except Exception as e:
				logger.debug('CONNECTOR------'+str(e) + ' attempt ' + str(i) )
				if i >= retry:
					self.isconnected = False
					self.disconnect()
					logger.debug('CONNECTOR------Issue connecting to : '+str(self.mac) + ' the device is busy or too far')
					return
				time.sleep(1)
		if self.isconnected:
			self.conn = connection
			logger.debug('CONNECTOR------Connected... ' + str(self.mac))
		return
		
	def disconnect(self,force=False):
		logger.debug('CONNECTOR------Disconnecting... ' + str(self.mac))
		i=0
		while True:
			i = i + 1
			try:
				self.conn.disconnect()
				break
			except Exception as e:
				if 'str' in str(e) and 'has no attribute' in str(e):
					self.isconnected = False
					return
				logger.debug('CONNECTOR------'+str(e) + ' attempt ' + str(i) )
				if i >= 2:
					self.isconnected = False
					return
		self.isconnected = False
		logger.debug('CONNECTOR------Disconnected...'+ str(self.mac))

	def readCharacteristic(self,handle,retry=1,type='public'):
		logger.debug('CONNECTOR------Reading Characteristic...'+ str(self.mac))
		ireadCharacteristic=0
		while True:
			ireadCharacteristic = ireadCharacteristic + 1
			try:
				result = self.conn.readCharacteristic(int(handle,16))
				break
			except Exception as e:
				logger.debug(str(e))
				if ireadCharacteristic >= retry:
					self.disconnect(True)
					return False
				logger.debug('CONNECTOR------Retry connection '+ str(self.mac))
				self.connect(type=type)
		logger.debug('CONNECTOR------Characteristic Readen .... ' + str(self.mac))
		return result

	def writeCharacteristic(self,handle,value,retry=1,response=False,type='public'):
		logger.debug('CONNECTOR------Writing Characteristic... ' + str(self.mac))
		iwriteCharacteristic=0
		while True:
			iwriteCharacteristic = iwriteCharacteristic + 1
			try:
				arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
				result = self.conn.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue),response)
				break
			except Exception as e:
				logger.debug(str(e))
				if iwriteCharacteristic >= retry:
					self.disconnect(True)
					return False
				logger.debug('CONNECTOR------Retry connection ' + str(self.mac))
				self.connect(type=type)
		logger.debug('CONNECTOR------Characteristic written... ' + str(self.mac))
		if result :
			logger.debug(str(result))
		return True
	
	def getCharacteristics(self,handle='',handleend='',retry=1,type='public'):
		logger.debug('CONNECTOR------Getting Characteristics... ' + str(self.mac))
		if handleend == '':
			handleend = handle
		igetCharacteristics=0
		while True:
			igetCharacteristics = igetCharacteristics + 1
			try:
				if handle == '':
					char = self.conn.getCharacteristics()
					break
				else:
					char = self.conn.getCharacteristics(int(handle,16), int(handleend,16)+4)
					break
			except Exception as e:
				logger.debug(str(e))
				if igetCharacteristics >= retry:
					self.disconnect(True)
					return False
				logger.debug('CONNECTOR------Retry connection ' + str(self.mac))
				self.connect(type=type)
		logger.debug('CONNECTOR------Characteristics gotten... '+ str(self.mac))
		return char
		
	def helper(self):
		logger.debug('CONNECTOR------Helper for : ' + str(self.mac))
		characteristics = self.getCharacteristics()
		listtype=['x','c','b','B','?','h','H','i','I','l','L','q','Q','f','d','s','p','P']
		for char in characteristics:
			handle = str(hex(char.getHandle()))
			if char.supportsRead():
				logger.debug('CONNECTOR------'+handle + ' readable')
			else:
				logger.debug('CONNECTOR------'+handle + ' not readable (probably only writable)')
			if char.supportsRead():
				try:
					value = char.read()
					for type in listtype:
						for i in range(1,256):
							try:
								logger.debug('CONNECTOR------value for handle (decrypted with ' + type + ' lenght ' + str(i) +') : ' + handle + ' is : ' + str(struct.unpack(str(i)+type,value)))
							except:
								continue
					logger.debug('CONNECTOR------value for handle (undecrypted) : ' + handle + ' is : ' + value)
				except Exception as e:
					logger.debug('CONNECTOR------unable to read value for handle (probably not readable) '+handle+ ' : '+str(e))
					continue
		return
