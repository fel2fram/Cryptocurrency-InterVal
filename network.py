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
    #print("avez-vous une clé privée ?")
    clepv = 0 #sys.stdin.readline().rstrip()
    if clepv :
        return custom_compte(clepv)
    elif moi[1] >= 3000 :
        return distrib_init()
    else :
        return createcompte()

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
        [n, e, corps] = line.decode().split(' ', 2)
        [reste, signa] = corps.rsplit(' ', 1)
        l = list(map(float, reste.split(" ")))
        cle = n + ' ' + e
        if checksign(int(n), int(e), reste, int(signa, 16)) and\
        (cle not in listmsg or not corps in listmsg[cle]) :
            print("msg accepte")
            for lui in setpairs.difference({adr, moi}) :
                UDPSocket.sendto(line, lui)
            listmsg[cle] = listmsg.get(cle, set()).union({corps})
            return [int(n) % 1000] + l
        return 0

def output(monint, sg, sd, rg, nxtlvl) :
    global UDPSocket, setpairs, moi
    (n,e) = getpb()
    msg = str(float(sg)) + " " + \
    str(float(sd)) + " " + str(float(rg)) + " " + str(float(nxtlvl))
    UDPSocket.sendto(str.encode(str(n) + " " + str(e) + " " + msg + " " + masign(msg)), moi)
