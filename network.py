import sys
import copy
import intervals as I
import socket

from collections import OrderedDict
from crypting import *

global nbmsg
global UDPSocket, setpairs, moi, listmsg, nbmsg
setpairs = set()
listmsg = dict()
nbmsg = 0

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

def input(mes_comptes) :
    global setpairs, listmsg, nbmsg
    while(1) :
        (line, adr) = UDPSocket.recvfrom(1024)
        if adr not in setpairs :
            setpairs.add(adr)
            maj(adr)
        [clessh1, clessh2, corps] = line.split(' ', 2)
        [reste, signa] = corps.rsplit(' ', 1)
        clessh = clessh1 + " " + clessh2
        print("nbmessages", nbmsg)
        if checksign(clessh, reste, signa) :
            if clessh not in listmsg or not corps in listmsg[clessh] :
                for lui in setpairs.difference({adr, moi}) :
                    UDPSocket.sendto(str.encode(line), lui)
                nbmsg +=1
                if nbmsg % 20 == 3 :
                    mes_comptes.append(createcompte())
                    output(mes_comptes[-2], mes_comptes[-2], mes_comptes[-2] + 1, mes_comptes[-1] , nbmsg/20 + 1)
                listmsg[clessh] = listmsg.get(clessh, set()).union({corps})
                print("msg", reste)
                monint = int(ascii_to_int(clessh) % 1000)
                l = map(float, reste.split(" "))
                if l[0] == monint :
                    return l

def output(monint, sg, sd, rg, nxtlvl) :
    global UDPSocket, setpairs, moi
    clessh = getssh(monint)
    msg = str(float(monint)) + " "  + str(float(sg)) + " " + \
    str(float(sd)) + " " + str(float(rg)) + " " + str(float(nxtlvl))
    UDPSocket.sendto(str.encode(clessh + " " + msg + " " + masign(msg, monint)), moi)
