import sys
import copy
import intervals as I
import socket

from collections import OrderedDict
from crypting import *

global UDPSocket, setpairs, moi, listmsg, nbmsg
setpairs = set()
listmsg = dict()

def askip() :
    global UDPSocket, lui, moi
    print("votre ip, votre port, son ip, son port")
    UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    moi = (sys.stdin.readline().rstrip(), int(sys.stdin.readline().rstrip()))
    UDPSocket.bind(moi)
    setpairs.add(moi)
    setpairs.add((sys.stdin.readline().rstrip(), int(sys.stdin.readline().rstrip())))
    if moi[1] == 3000 :
        return True
    return False

def maj(adr):
    global listmsg
    for clessh in listmsg :
        for msg in listmsg[clessh] :
            UDPSocket.sendto(str.encode(clessh + " " + msg), adr)

def input() :
    global setpairs, listmsg, nbmsg
    while(1) :
        (line, adr) = UDPSocket.recvfrom(1024)
        if adr not in setpairs :
            setpairs.add(adr)
            print("new peer", adr)
            maj(adr)
        [clessh1, clessh2, corps] = line.split(' ', 2)
        [reste, signa] = corps.rsplit(' ', 1)
        clessh = clessh1 + " " + clessh2
        l = map(float, reste.split(" "))
        print("msg", int(ascii_to_int(clessh) % 1000), reste)
        if checksign(clessh, reste, signa) and\
        clessh not in listmsg or not corps in listmsg[clessh]:
            print("msg accepte")
            for lui in setpairs.difference({adr, moi}) :
                UDPSocket.sendto(str.encode(line), lui)
            listmsg[clessh] = listmsg.get(clessh, set()).union({corps})
            return [int(ascii_to_int(clessh) % 1000)] + l

def output(monint, sg, sd, rg, nxtlvl) :
    global UDPSocket, setpairs, moi
    clessh = getssh(monint)
    msg = str(float(sg)) + " " + \
    str(float(sd)) + " " + str(float(rg)) + " " + str(float(nxtlvl))
    UDPSocket.sendto(str.encode(clessh + " " + msg + " " + masign(msg, monint)), moi)
