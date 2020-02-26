from Crypto.Cipher import AES

import base64

import hashlib
from common.utils import SmLogger



BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-s[-1]]

key = "m9nm13gwsali72jdhhicf77elte8nnyw"; # 32bit
iv = 'y8vweyjjem8kj9l2' # 16bit

beforeCipher = 'sf3157975311!'
SmLogger.info (SmLogger, 'Input string: ' + beforeCipher)

cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, IV=iv.encode('utf8'))
beforeCipher = pad(beforeCipher)
afterCipher = base64.b64encode(cipher.encrypt(beforeCipher.encode('utf8')))
SmLogger.info (SmLogger, 'Cipher string: ' + str (afterCipher)[2:-1])

cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, IV=iv.encode('utf8'))
deciphed = cipher.decrypt(base64.b64decode(afterCipher))
deciphed = unpad(deciphed)

SmLogger.info (SmLogger, 'Deciphed string: [' + str (deciphed)[2:-1] +']')