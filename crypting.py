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

def distrib_init() :
    clessh = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCw5znDPG+7Lc3Vlbu739ASlh1mSnmiiioiCmOq45oCvfIvTXBdO036+Go5PZv0KzFRQSsW8pnlh+J6WCqM4vQ33PXk64IcgAVw2CGoVQuvqCTQYTTaxLDE/ltsGj6hHk5ZXc6PKHeFABfjV+y6OooxHtzKbbMaEvZb5p4f7AVP1Q=="
    pv = RSA.importKey("-----BEGIN RSA PRIVATE KEY-----\nMIICXQIBAAKBgQCw5znDPG+7Lc3Vlbu739ASlh1mSnmiiioiCmOq45oCvfIvTXBd\nO036+Go5PZv0KzFRQSsW8pnlh+J6WCqM4vQ33PXk64IcgAVw2CGoVQuvqCTQYTTa\nxLDE/ltsGj6hHk5ZXc6PKHeFABfjV+y6OooxHtzKbbMaEvZb5p4f7AVP1QIDAQAB\nAoGBAJB4pfHOH6mL5LfzitgKFpG3StdJJ0EY+QPH3FGpgxOOMIV1Brj9P9ggnA+X\nQxALXkFvqVMaWZjcepdT/ZwFlU/WJEJpI/WgU/XejNbnRXd0Y4GVwrnK0AKCpmtY\nb6H7e7V/Du5Q/lFIEde6msAQBRymnZiKOdHMe2iXYTwEPMGZAkEAzIBiHj9dbELN\nlbw7ZHWyzWTXgCGhnQcM1tc4Hn2pJI3Z2TKT5+gh67ORKDym1FMKy+YpNXII0VIi\nCMhf//VuewJBAN1zqXsMIShbtHT1o1Ua9qMeOklatCioprPY+ATFHk1Gi0Vpx/8/\nt/8haB6NcW5SaPkKUip1QqA8SNpajM2XEe8CQQCMV87+Ux4aHf5YtEVOPDfpHTuH\ng40V5rC5ABpTUomxvGe01zEKBhTBXQpRQs57CEJwjBPbydajUGpq/JhlYFnhAkAe\n40QPYpi5XVklOyHF/BXMmKm+k4Uvap6d1TR6zde1JZLFYsS/iG6sikdQg5//qET1\n/4eIXoSlfuMWeazL/DdHAkB8pT/RN29gUoVF07dI8ckc/orxehw0QkmGC6u+3W+r\neLQJDPLyYcOPDYaErb5i+d4/kIURYOLzSwl1Q5pNzjJy\n-----END RSA PRIVATE KEY-----")
    pb = RSA.importKey(clessh)
    monint = int(ascii_to_int(clessh)) % 1000
    comptes[monint] = (pv, pb, clessh)
    return monint

def createcompte() :
    pv, pb = rsakeys()
    clessh = pb.exportKey(format='OpenSSH')
    pbssh = pv.exportKey(format='OpenSSH')
    #pbsshb = pv.exportKey()
    #print(clessh, pbsshb)
    monint = int(ascii_to_int(clessh)) % 1000
    print("votre compte est", monint, monint+1)
    comptes[monint] = (pv, pb, clessh)
    return monint
