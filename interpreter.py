import sys
import copy
import intervals as I
import os, signal
from network import *

nbpiece = 500
seuil = 1.8/500.

class Compte :
    def __init__(self, piece, niveau = 0) :
        self.trans = dict()
        self.niveau = niveau
        self.piece = piece
        self.defense = set()
        self.recep = False
        self.jump = False
        self.density = 1

def ico(x, y) :
    return I.closedopen(x, y)

lc = dict()
lc[ico(0, nbpiece)] = Compte(ico(0, nbpiece))
lc[ico(nbpiece, I.inf) | ico(-I.inf, 0)] = Compte(I.empty())
global comptes_vivants, comptes_morts, pieces_par_level, maxlvl
comptes_vivants = ico(0, nbpiece)
comptes_morts = I.empty()
pieces_par_level = {0 : ico(0, nbpiece)}
comptes_actifs = {1 : ico(0, nbpiece), 2 : ico(0, nbpiece)}
maxlvl = 1

def maj_lvl() :
    global pieces_par_level, maxlvl
    print(pieces_par_level)
    maxtmp = 0
    for i in pieces_par_level :
        if i > maxtmp and sizeunion(pieces_par_level[i]) > seuil * nbpiece :
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
    newc = Compte(set(), compte.niveau)
    for cle in compte.trans :
        newc.trans[sousinter(K, k, cle[0]), cle[1]] = compte.trans[cle]
    newc.piece = sousinter(K, k, compte.piece)
    for (sender, receiver, nxtlvl) in compte.defense :
        sender2 = sousinter(K, k, sender)
        receiver2 = sousinter(K, k, receiver)
        newc.defense.add((sender2, receiver2, nxtlvl))
    lc[k] = newc

def check(k, v) :
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
            check(vcommun, kcommun)
            check(k, v)
            break
    check(v, k)

def find_parts(k) :
    return [cle for cle in lc if k.contains(cle)]

def sizeunion(union) :
    if union == I.empty() :
        return 0
    l = list(union)
    s = 0
    for i in l :
        s+= i.upper - i.lower
    return s

def update(sender, ((receiver, nxtlvl), votants)) :
    global comptes_vivants, comptes_morts, pieces_par_level
    print("vote", votants, receiver, "actifs", comptes_actifs, maxlvl)
    if sizeunion(votants) < seuil * sizeunion(comptes_actifs[nxtlvl]) : #or votants & sender == I.empty():
        return False
    comptes_vivants |= receiver
    comptes_morts |= sender
    comptes_vivants -= sender
    pieces_par_level[nxtlvl] = pieces_par_level.get(nxtlvl, I.empty()).union(lc[sender].piece)
    maj_lvl()
    lc[receiver].niveau = nxtlvl
    lc[receiver].piece = lc[sender].piece
    lc[receiver].jump = lc[sender].jump
    lc[receiver].density = lc[sender].density * 0.9
    if nxtlvl == lc[sender].niveau + 1 :
        lc[receiver].jump = False
        niv = lc[receiver].niveau + 2
        comptes_actifs[niv] = comptes_actifs.get(niv, I.empty()) | lc[receiver].piece
    elif nxtlvl == lc[sender].niveau + 2 :
        lc[receiver].jump = True
        lc[receiver].density = lc[sender].density * 0.8
    print("new density", lc[receiver].density)
    for triplet in lc[receiver].defense :
        recep(receiver, triplet)
    for (receiver2, nxtlvl2) in lc[receiver].trans :
        if recep(I.empty(), (receiver, receiver2, nxtlvl2)) :
            break
    return True

def recep_aux(compte, sender, receiver, nxtlvl) :
    (vs, rb) = (lc[sender].trans, (receiver, nxtlvl))
    vs[rb] = vs.get(rb, I.empty())
    if compte != I.empty() and \
    nxtlvl - 1 <= lc[compte].niveau <= nxtlvl and\
    not lc[compte].jump :
        vs[rb] |= lc[compte].piece
    lc[receiver].recep = True
    if lc[sender].piece !=I.empty() and nxtlvl <= maxlvl and\
    update(sender, (rb, vs[rb])) :
        return True
    if compte != I.empty() :
        lc[compte].defense.add((sender, receiver, nxtlvl))
    return False

def recep(compte, (sender, receiver, nxtlvl)) :
    sender -= sender & receiver
    receiver -= sender & receiver
    check(compte, I.empty())
    check(sender, receiver)
    success = False
    f = find_parts(compte)
    if not f :
        f = [I.empty()]
    newsender, newreceiver = I.empty(), I.empty()
    for senderj in find_parts(sender) :
        receiverj = sousinter(sender, senderj, receiver)
        if senderj.upper - 1 <= compte <= senderj.lower and\
         (not lc[senderj].trans) and\
         (not lc[receiverj].recep) and nxtlvl == maxlvl and\
         lc[senderj].piece != I.empty() :
            newsender |= senderj
            newreceiver |= receiverj
        for comptei in f:
            #print("debug compte", comptei, "sender", senderj, "receiver", receiverk, "parts", lc.keys())
            success |= recep_aux(comptei, senderj, receiverj, nxtlvl)
    newsenderl, newreceiverl = list(newsender), list(newreceiver)
    if newsenderl != [I.empty()] :
        for (i, senderk) in enumerate(newsenderl) :
            output(monint, senderk.lower, senderk.upper, newreceiverl[i].lower, nxtlvl)
    return success

askip()
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
    print("dead :", comptes_morts)
    print("position :", comptes_vivants)
    print("compte :", ico(monint, monint + 1))
    [compte, sl, su, rl, nxtlvl] = input()
    recep(ico(compte, compte + 1), (ico(sl, su), ico(rl,rl + su - sl), nxtlvl))
    os.kill(child, signal.SIGTERM)
