'''
Benecoding Decoder Programme

Accepts bytes values only, as this is the optimal way for reading 
.torrent files which this programme is mainly for
'''
class Bendecoder:
	def __init__(self, metainfo:bytes):
		if not(isinstance(metainfo, bytes)):
			raise TypeError("Encoding needs to be of type 'bytes' ")
		self.metainfo_original = metainfo
		self.metainfo = metainfo

	def decode(self):
		if(self.metainfo == None):
			raise EOFError("Unexpected End of File")
		elif self.metainfo[0] in b'0123456789': #if a string needs to be decoded
			return self.decode_string()
		elif self.metainfo[0:1] == b'i': #if an integer needs to be decoded
			return self.decode_int()
		elif self.metainfo[0:1] == b'l': #if a list needs to be decoded
			return self.decode_list()
		elif self.metainfo[0:1] == b'd': #if a dictionary needs to be decoded
			return self.decode_dictionary()
		else: #
			error_loc = self.find_error_location(self.metainfo)
			raise RuntimeError("invalid token at location {0}".format(str(error_loc)))


	def decode_string(self):
		colon_loc = bytes.find(self.metainfo, b':') # find the location of the first : after the start of the string encoding
		length = int(self.metainfo[0: colon_loc]) #returns the values between the start of the encoding and the first :(length of the string)
		strng_value = str(self.metainfo[colon_loc + 1 : colon_loc+ 1 + length])#converts the bytes array of the string into a python string type 
		self.metainfo = self.metainfo[colon_loc+ 1 + length:]#returns the rest of the byte string to be decoded 
		return strng_value[2:len(strng_value)-1] #returns the string removing the b' '

	def decode_int(self):
		end_loc = bytes.find(self.metainfo, b'e') #find the location of the first e, which is the end of the integer
		# print(self.metainfo[1:2])
		if self.metainfo[1:2] == b'e': #if the encoded integer has the form ie
			error_loc = self.find_error_location(self.metainfo)
			raise RuntimeError("Invalid format of integer, no value between i and e at location {0}".format(error_loc))
		if (self.metainfo[1:2] == b'0' and len(self.metainfo) > 3) or (self.metainfo[1:3] == b'-0') : #if the encoded integer is of the form 0x, -0x, -0
			error_loc = self.find_error_location(self.metainfo)
			raise RuntimeError("Invalid integer, cannot have a value 0x, or -0x, or -0 at location {0}".format(error_loc))
		int_value = int(self.metainfo[1:end_loc]) #gets the decoded integer
		self.metainfo = self.metainfo[end_loc+1:] #returns the rest of the byte string to be decoded
		# print(self.metainfo)
		return int_value 

	def decode_list(self):
		list_of_values = [] 
		self.metainfo = self.metainfo[1:] # drop the b'l'
		while self.metainfo[0:1] != b'e': #loop  till the end of the list is found at b'e'
			list_of_values.append(self.decode()) #decodes the value (and appends it to the list) at the front of the string, the value after decoding as indicated in lies 33 and 44 so the next value in the list can be decoded
		self.metainfo = self.metainfo[1:] #returns the rest of the byte string, useful when list is contained in another list or a dictionary
		print(self.metainfo)
		return list_of_values
	
	def decode_dictionary(self):
		dict_of_values = {} 
		self.metainfo = self.metainfo[1:] #drop the b'd'
		while self.metainfo[0:1] != b'e': #loop till the end of the dictionary is found at b'e'
			if not(self.metainfo[0:1] in b'0123456789'): #To ensure that the key's are strings
				error_loc = self.find_error_location(self.metainfo)
				raise RuntimeError("Dictionary keys must be strings, error found at locaiton {0}".format(error_loc))
			key = self.decode() #decode the first value in the string(the key)
			val = self.decode()#decode the following value in the string(the key-value)
			dict_of_values[key] = val 
		self.metainfo = self.metainfo[1:] #returns the rest of the byte string useful for when dictionary is contained in  a list or another dictionary
		print(self.metainfo)
		return dict_of_values


	def find_error_location(self, error : bytes): 
		return bytes.find(self.metainfo_original, error)

	def print_code(self):
		print(type(self.metainfo[0:4]))

