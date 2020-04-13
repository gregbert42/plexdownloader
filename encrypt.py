#!/usr/bin/python3
import json

def writeout (fname,linesout):
   with open(fname, 'w') as writeFile:
      if (fname[-5:]==".json"): json.dump(linesout,writeFile,indent=4)
      elif (fname[-4:]==".csv"): csv.writer(writeFile).writerows(linesout)
   writeFile.close()
   return fname

from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)

query = input('To Encypt: ')   				#get the input
b = query.encode('utf-8')  				#convert from string to bytes
encrypted_input = f.encrypt(b)				#encrypt using Fernet

key=key.decode('utf-8')					#decode the key from bytes to string (to be able to put in json)
encrypted_input=encrypted_input.decode('utf-8')	#decode the input frm bytes to string (actually equal to original query)

lines={}						#create a dictionary
lines['key']=key
lines['encrypted']=encrypted_input
print (lines)
writeout('encrypted.json',lines)			#write out dictionary to json
