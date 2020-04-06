import sys
import copy
import intervals as I
import socket

from collections import OrderedDict
from crypting import *

global nbmsg
global UDPSocket, setpairs, moi, listmsg
setpairs = set()
listmsg = dict()

def ico(x, y) :
    return I.closedopen(x, y)

def getbounds(itv) :
    if itv == I.empty() :
        return (str(0) + " " + str(0) + " ")
    else :
        return(str(itv.lower) + " " + str(itv.upper) + " ")

def askip() :
    global UDPSocket, lui, moi
    print("votre ip, votre port, son ip, son port")
    UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    moi = (sys.stdin.readline().rstrip(), int(sys.stdin.readline().rstrip()))
    UDPSocket.bind(moi)
    setpairs.add((sys.stdin.readline().rstrip(), int(sys.stdin.readline().rstrip())))

def maj(adr):
    global listmsg
    for clessh in listmsg :
        for msg in listmsg[clessh] :
            UDPSocket.sendto(str.encode(clessh + " " + msg), adr)

def input() :
    global setpairs, listmsg
    while(1) :
        (line, adr) = UDPSocket.recvfrom(1024)
        if adr not in setpairs :
            setpairs.add(adr)
            maj(adr)
        for lui in setpairs.difference({adr, moi}) :
            UDPSocket.sendto(str.encode(line), lui)
        [clessh1, clessh2, corps] = line.split(' ', 2)
        [reste, signa] = corps.rsplit(' ', 1)
        clessh = clessh1 + " " + clessh2
        if checksign(clessh, reste, signa) :
            listmsg[clessh] = listmsg.get(clessh, set()).union({corps})
            print("msg", reste)
            monint = ascii_to_int(clessh) % 1000
            l = map(int, reste.split(" "))
            if l[0] >= monint and l[1] <= monint + 10 :
                return l

def output(compte, sender, receiver, nxtlvl) :
    global UDPSocket, setpairs, moi
    clessh = getssh()
    msg = getbounds(compte) + getbounds(sender) + getbounds(receiver) + str(nxtlvl)
    UDPSocket.sendto(str.encode(clessh + " " + msg + " " + masign(msg)), moi)
