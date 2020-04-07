import sys
import copy
import intervals as I
import os, signal
from network import *

nbpiece = 500
seuil = 2

class Compte :
    def __init__(self, piece, niveau) :
        self.trans = dict()
        self.niveau = niveau
        self.piece = piece
        self.defense = set()

def ico(x, y) :
    return I.closedopen(x, y)

lc = dict()
lc[ico(0, nbpiece)] = Compte({ico(0, nbpiece)}, {0})
lc[ico(nbpiece, I.inf) | ico(-I.inf, 0)] = Compte(set(), set())
global comptes_actifs, comptes_morts
comptes_actifs = ico(0, nbpiece)
comptes_morts = I.empty()
mes_comptes = list()

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
    for piece in compte.piece :
        newc.piece.add(sousinter(K, k, piece))
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

def update(param) :
    sender, ((receiver, nxtlvl), votants) = param
    global comptes_actifs, comptes_morts
    if lc[sender].niveau and min(lc[sender].niveau) > nxtlvl \
    or lc[sender].piece.issubset(lc[receiver].piece) :
        return False
    union = I.empty()
    selfvote = False
    for part in find_parts(votants):
        selfvote |= (part & sender != I.empty())
        if lc[part].niveau.intersection(lc[sender].niveau) :
            for piece in lc[part].piece :
                union |= piece
    #print("sizeunion", union, sizeunion(union), seuil)
    if sizeunion(union) < seuil or not selfvote:
        return False
    if not lc[receiver].piece :
        comptes_actifs |= receiver
    comptes_morts |= sender
    comptes_actifs -= sender
    lc[receiver].niveau.add(nxtlvl)
    lc[receiver].piece = lc[receiver].piece.union(lc[sender].piece)
    for triplet in lc[receiver].defense :
        recep(receiver, triplet)
    for (receiver2, nxtlvl2) in lc[receiver].trans :
        if recep(I.empty(), (receiver, receiver2, nxtlvl2)) :
            break
    return True

def recep_aux(compte, sender, receiver, nxtlvl) :
    (vs, rb) = (lc[sender].trans, (receiver, nxtlvl))
    vs[rb] = vs.get(rb, I.empty()).union(compte)
    if update(sender, (rb, vs[rb])) :
        return True
    if compte != I.empty() :
        lc[compte].defense.add((sender, receiver, nxtlvl))
    return False

def recep(param) :
    compte, (sender, receiver, nxtlvl)
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
         (senderj not in lc or not lc[senderj].trans) :
            newsender |= senderj
            newreceiver |= receiverj
        for comptei in f:
            #print("debug compte", comptei, "sender", senderj, "receiver", receiverk, "parts", lc.keys())
            success |= recep_aux(comptei, senderj, receiverj, nxtlvl)
    newsenderl, newreceiverl = list(newsender), list(newreceiver)
    if newsenderl != [I.empty()] :
        for (i, senderk) in enumerate(newsenderl) :
            for j in mes_comptes :
                output(j, senderk.lower, senderk.upper, newreceiverl[i].lower, nxtlvl)
    return success

askip()
monint = createcompte()
mes_comptes.append(monint)

while(1) :
    child = os.fork()
    if not child :
        while(1) :
            l = sys.stdin.readline().rstrip().split(" ")
            if len(l) == 4 :
                [sl, su, rl, nxtlvl] = map(float,l)
                output(mes_comptes[-1], sl, su, rl, nxtlvl)
            else :
                print("ligne invalide")
    print("dead :", comptes_morts)
    print("position :", comptes_actifs)
    print("compte :", ico(mes_comptes[-1], mes_comptes[-1] + 1))
    [compte, sl, su, rl, nxtlvl] = input(mes_comptes)
    recep(ico(compte, compte + 1), (ico(sl, su), ico(rl,rl + su - sl), nxtlvl))
    os.kill(child, signal.SIGTERM)
