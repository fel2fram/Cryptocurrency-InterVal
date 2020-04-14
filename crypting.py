from Crypto.PublicKey import RSA
from hashlib import sha512

global keyPair

def getpb():
    return(keyPair.n, keyPair.e)

def masign(msg) :
    global keyPair
    hash = int.from_bytes(sha512(msg.encode()).digest(), byteorder='big')
    signature = pow(hash, keyPair.d, keyPair.n)
    return hex(signature)

def checksign(e, n, str, signature) :
    hash = int.from_bytes(sha512(str.encode()).digest(), byteorder='big')
    hashFromSignature = pow(signature, n, e)
    return (hash == hashFromSignature)

def distrib_init() : #pour plus tard
    global keyPair
    keyPair = RSA.importKey('-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQCTzcBNMUeaXWkd3XeCE02LUp1jp7m3yWYBHXRSA6QDNZRr45or\nArs5kTp+QAWISAc41ZwZRQWcXsGsZ12BvdsCVcrJTzQxaukW/a+ESk9wgXHhA9vR\nlFWhtu9xxu4zrj5LR6mxgxMdPzyaxCdizD5Bblk7DgCALF84I93awKatgwIDAQAB\nAoGAG+F7jXQm0CEfw5DzyrcucQIYC2TnvRoCImK2fwQNy8cvJLzt54Af5ieVk5wr\nDv6bUibFR+UDvnAHc6iZ9G/mYHxaeAddQ2ZlseMoC0Tl/sSWHWYuDvG2yN+0dbWV\n5w+9avtwC0+qYVLpvpqjiDAnDpsd0P6tGXMFjSZ4jXWuWUECQQC2ihrQXV1cpYod\nRlFOIBFXynVSuRh7LPhpceb+wChQbIRVSIsQNm2QqQD7Yja98Ck9+xlWqXdXbZmn\nH6816cxBAkEAz0kKJs3ofbDEgtrFxf9mESthnzF248zsjSuXw8mZJlVW5mOenzl6\nYmbMj+oGclwo+rcm9JTQRr5ShTKh0eoYwwJAcS1rtqlMy7avzbrdim0Dk8UpvSKa\ndTTKyMYgjO8jj8nYuvABmQnGIR1ISJT6kAWp7I4VhdAI+KIx1JcmkWzmgQJBAL3z\n5/qhbPFpwNtNUjncjxMi1wYEVTfyPcAsd5oyr0bio4zjM6QkDxQHsmQbiKbZ76+5\nkVhG2wpJNOPc/0+XH/MCQGLWDUIqa5K/bnJUwlrUJhno+CJ4SCG7SPvXwpGua0Dk\n7L6pP5eFZFfFmcUc1olw58Ycj74F4Q4gWsbvWX6K+H4=\n-----END RSA PRIVATE KEY-----')
    monint = int(keyPair.n) % 1000
    return monint

def createcompte() :
    global keyPair
    keyPair = RSA.generate(bits=1024)
    clessh = str(keyPair.n) + " " + str(keyPair.e)
    print("votre clé", keyPair.exportKey('PEM'))
    monint = int(keyPair.n) % 1000
    return monint
