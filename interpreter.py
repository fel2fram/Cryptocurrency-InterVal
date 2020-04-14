import sys
import copy
import intervals as I
import os, signal
from network import *

seuil = 0.66

class Compte :
    def __init__(self, piece, recu = False, density = 1, niveau = 0) :
        self.trans = dict()
        self.niveau = niveau
        self.piece = piece
        self.defense = set()
        self.recu = recu
        self.density = density

def ico(x, y) :
    return I.closedopen(x, y)

lc = dict()
lc[I.empty()] = Compte(I.empty())
lc[ico(893, 894)] = Compte(ico(893, 894))
lc[ico(894, I.inf) | ico(-I.inf, 893)] = Compte(I.empty())
global vivants, morts, actifs, maxlvl
vivants = ico(893, 894)
morts = I.empty()
actifs = {0 : ico(893, 894)}
maxlvl = 1

def maj_lvl() :
    global actifs, maxlvl
    print(actifs)
    maxtmp = 0
    for i in actifs :
        if i > maxtmp and sizeunion(actifs[i]) > seuil \
        * sizeunion(actifs[max(0,i - 3)]) :
            maxtmp = i
    maxlvl = maxtmp + 1
    print("new max lvl", maxlvl)

def sousinter(K, k, V) :
    if V == I.empty() or K == I.empty() or k == I.empty() :
        return(I.empty())
    offset = V.lower - K.lower
    v = I.empty()
    for i in list(k) :
       	v |= ico(i.lower + offset, i.upper + offset)
    return(v)

def adapte_coupe(K, k, compte) :
    newc = Compte(set(), compte.recu, compte.density, compte.niveau)
    for cle in compte.trans :
        newc.trans[sousinter(K, k, cle[0]), cle[1]] = compte.trans[cle]
    newc.piece = sousinter(K, k, compte.piece)
    for (sender, receiver, nxtlvl) in compte.defense :
        sender2 = sousinter(K, k, sender)
        receiver2 = sousinter(K, k, receiver)
        newc.defense.add((sender2, receiver2, nxtlvl))
    lc[k] = newc

def chop(k, v) :
    if k == I.empty() or (k in lc and v in lc) :
        return
    for (cle, compte) in lc.items() :
        kcommun = cle & k
        if kcommun != I.empty() :
            vcommun = sousinter(k, kcommun, v)
            k -= kcommun
            v -= vcommun
            if kcommun != cle :
                adapte_coupe(cle, kcommun, compte)
                adapte_coupe(cle, cle - kcommun, compte)
                lc.pop(cle)
            chop(vcommun, kcommun)
            chop(k, v)
            break
    chop(v, k)

def find_parts(k) :
    return [cle for cle in lc if k.contains(cle)]

def sizeunion(union) :
    if union == I.empty() :
        return 0
    s = 0
    for i in list(union) :
        s+= i.upper - i.lower
    return s

def activate(sender, receiver, nxtlvl) :
    global vivants, morts
    print("vote validant", receiver, "actifs", actifs, maxlvl)
    vivants = (vivants | receiver) - sender
    morts |= sender
    actifs[nxtlvl] = actifs.get(nxtlvl, I.empty()) | lc[sender].piece
    maj_lvl()
    lc[receiver].niveau = nxtlvl
    lc[receiver].piece = lc[sender].piece
    lc[receiver].density = lc[sender].density * [0.9,0.8][nxtlvl >= lc[sender].niveau + 2]
    print("new density", lc[receiver].density)
    for (s2, r2, n2) in lc[receiver].defense :
        decoupe(receiver, s2, r2, n2)
    for (r2, n2) in lc[receiver].trans :
        decoupe(I.empty(), receiver, r2, n2)

def add_vote(compte, sender, receiver, nxtlvl) :
    vs, rb = lc[sender].trans, (receiver, nxtlvl)
    vs[rb] = vs.get(rb, I.empty())
    lc[receiver].recu = True
    if nxtlvl - 1 <= lc[compte].niveau <= nxtlvl :
        vs[rb] |= lc[compte].piece & actifs.get(max(0, nxtlvl - 3), I.empty())
    if lc[sender].piece != I.empty() and lc[receiver].piece == I.empty()\
    and nxtlvl <= maxlvl + 1 and\
    sizeunion(vs[rb]) >= seuil * sizeunion(actifs.get(max(0,nxtlvl - 3), I.empty())) :
        activate(sender, receiver, nxtlvl)
    else :
        lc[compte].defense.add((sender, receiver, nxtlvl))

def decoupe(compte, sender, receiver, nxtlvl) :
    sender -= receiver
    receiver -= sender
    chop(compte, I.empty())
    chop(sender, receiver)
    f = find_parts(compte)
    newsender = I.empty()
    for senderj in find_parts(sender) :
        receiverj = sousinter(sender, senderj, receiver)
        if compte.contains(senderj) and not lc[senderj].trans\
        and not lc[receiverj].recu and maxlvl - 1 <= nxtlvl <= maxlvl and\
         lc[senderj].piece != I.empty() :
            newsender |= senderj
        for comptei in f:
            #print("debug compte", comptei, "sender", senderj, "receiver", receiverk, "parts", lc.keys())
            add_vote(comptei, senderj, receiverj, nxtlvl)
    return [newsender, sousinter(sender, newsender, receiver)]

def recep(compte, sender, receiver, nxtlvl) :
    [newsenderl, newreceiverl] = map(list, decoupe(compte, sender, receiver, nxtlvl))
    if newsenderl != [I.empty()] :
        for (i, senderk) in enumerate(newsenderl) :
            output(monint, senderk.lower, senderk.upper, newreceiverl[i].lower, nxtlvl)

def monfric(compte) :
    envie = compte & vivants
    somme = 0.
    for itv in lc :
        mapart = itv & envie
        if mapart != I.empty() :
            somme += sizeunion(mapart) * lc[itv].density
    return somme

if askip() :
    monint = distrib_init()
else :
    monint = createcompte()

while(1) :
    child = os.fork()
    if not child :
        while(1) :
            l = sys.stdin.readline().rstrip().split(" ")
            if len(l) == 3 :
                [sl, su, rl] = map(float,l)
                output(monint, sl, su, rl, maxlvl)
            else :
                print("ligne invalide")
    print("dead :", morts)
    print("position :", vivants)
    print("compte :", ico(monint, monint + 1))
    print("monfric :", monfric(ico(monint, monint + 1)))
    [compte, sl, su, rl, nxtlvl] = input()
    recep(ico(compte, compte + 1), ico(sl, su), ico(rl,rl + su - sl), nxtlvl)
    os.kill(child, signal.SIGTERM)
