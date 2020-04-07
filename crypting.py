import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import binascii
import intervals as I

comptes = dict()

def getssh(compte) :
    return comptes[compte][2]

def rsakeys():
     length=1024
     privatekey = RSA.generate(length, Random.new().read)
     publickey = privatekey.publickey()
     return privatekey, publickey

def sign(privatekey,data):
    return base64.b64encode(str((privatekey.sign(data,''))[0]).encode())

def verify(publickey,data,sign):
     return publickey.verify(data,(int(base64.b64decode(sign)),))

def masign(msg, compte) :
    return(sign(comptes[compte][0], msg))

def checksign(user, str, signa) :
    userkey = RSA.importKey(user)
    return verify(userkey, str, signa)

def ascii_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + ord(b)
    return result

def int_to_ascii(entier):
    bytes = ''
    while entier :
        bytes = chr(entier % 256) +bytes
        entier /= 256
    return bytes

def createcompte() :
    pv, pb = rsakeys()
    clessh = pb.exportKey(format='OpenSSH')
    monint = int(ascii_to_int(clessh)) % 1000
    print("votre compte est", monint, monint+1)
    comptes[monint] = (pv, pb, clessh)
    return monint
