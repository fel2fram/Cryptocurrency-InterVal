import sys
import copy
import intervals as I
import os, signal
from network import *

nbpiece = 500
seuil = 10

class Compte :
    def __init__(self, piece, niveau) :
        self.trans = dict()
        self.niveau = niveau
        self.piece = piece
        self.defense = set()

lc = dict()
lc[ico(0, nbpiece)] = Compte({ico(0, nbpiece)}, {0})
lc[ico(nbpiece, I.inf) | ico(-I.inf, 0)] = Compte(set(), set())
global comptes_actifs, comptes_morts, moncompte
comptes_actifs = ico(0, nbpiece)
comptes_morts = I.empty()
askip()

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

def update(sender, ((receiver, nxtlvl), votants)) :
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

def recep(compte, (sender, receiver, nxtlvl)) :
    if sizeunion(sender) != sizeunion(receiver) :
        receiver = sousinter(sender, sender, receiver)
        print("taille receiver corrigee", receiver)
    sender -= sender & receiver
    receiver -= sender & receiver
    check(compte, I.empty())
    check(sender, receiver)
    success = False
    f = find_parts(compte)
    if not f :
        f = [I.empty()]
    newsender = I.empty()
    newreceiver = I.empty()
    for senderj in find_parts(sender) :
        receiverj = sousinter(sender, senderj, receiver)
        if senderj not in lc or not lc[senderj].trans :
            newsender |= senderj
            newreceiver |= receiverj
        for comptei in f:
            #print("debug compte", comptei, "sender", senderj, "receiver", receiverk, "parts", lc.keys())
            success |= recep_aux(comptei, senderj, receiverj, nxtlvl)
    newsenderl = list(newsender)
    newreceiverl = list(newreceiver)
    if newsenderl != [I.empty()] :
        for (i, senderk) in enumerate(newsenderl) :
            output(moncompte, senderk, newreceiverl[i], nxtlvl)
    return success

moncompte = createcompte()
while(1) :
    child = os.fork()
    if not child :
        while(1) :
            l = sys.stdin.readline().rstrip().split(" ")
            if len(l) == 4 :
                [sl, su, rl, nxtlvl] = map(int,l)
                sg, sd = min(sl, su), max(sl, su)
                rg, rd = min(rl, rl + sd - sg), max(rl, rl + sd - sg)
                output(moncompte, ico(sg, sd), ico(rg, rd), nxtlvl)
            else :
                print("ligne invalide")
    print("dead :", comptes_morts)
    print("position :", comptes_actifs)
    print("compte :", moncompte)
    [cl, cu, sl, su, rl, ru, nxtlvl] = input()
    recep(ico(min(cl, cu), max(cl, cu)), (ico(min(sl, su), max(sl, su)), ico(min(rl, ru), max(rl, ru)), nxtlvl))
    os.kill(child, signal.SIGTERM)
