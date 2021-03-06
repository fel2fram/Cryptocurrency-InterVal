Nouvelle cryptomonnaie : [InterVal[
Unité : ITV

InterVal est une cryptomonnaie ayant la propriété d’être complètement insensible à l’ordre de reception des transactions. Pour l’instant, je n’ai codé que le coeur du coeur de l’algo, mais bon. Il n’y a pas encore de comptes a proprement parler, tout le monde peut envoyer des pièces depuis n’importe où.

I. COMMENT UTILISER :

Lancer dans le terminal "python interpreter.py" (ou bien python2, python3, jsp trop).
Deux lignes vont s’afficher :
- dead : emplacements déjà vidés.
- position : emplacement des pièces. Initialement en [0, 10[

Ensuite, écrire des messages de la forme :
[validateur[ [depart[ [arivee[ niveaux

Pour l’instant, on va laisser le premier intervalle à [0, 10[, et le dernier nombre à 0. On comprendra leur utilité plus tard. 
Exemple de transaction :

0 10 0 10 20 30 0

Envoie les 10 ITV qui se trouvaient en [0, 10[ en [20, 30[.

II. REGLES :

- On peut couper les intervalles autant qu’on veut. Attention cependant, le comportement n’est garanti qu’avec des demi-entiers, ou demi-demi-entiers, etc. (sommes de 1/2^n). Exemple : 0,625. Sinon, python délire parfois.
- Les nombres négatifs fonctionnent.
- Les bornes des intervalles peuvent être inversées.
- La taille du deuxième intervalle sera toujours ramenée à celle du premier, sauf si un des deux intervalles est vide (ce qui invalide la transaction)

Amusez-vous à envoyer des pièces à gauche à droite.

1. CREATION / DESTRUCTION MONETAIRE :

Si un intervalle envoie de l’argent à deux autres intervalles, l’argent est dédoublé :

0 10 0 10 10 20 0
0 10 0 10 20 30 0

(N’oubliez pas de relancer le programme à chaque fois pour réinitialiser)

Les intervalles [10, 20[ et [20, 30[ sont remplis à present.
Cette situation sera impossible à atteindre dans la pratique. Explications en section IV.

Si deux intervalles envoie de l’argent au même intervalle, l’argent est perdu :

0 10 0 5 20 25 0
0 10 5 10 20 25 0

Seul l’intervalle [20, 25[ est rempli.
Cette situation sera possible mais aucune personne saine d’esprit ne souhaite perdre de l’argent, donc cela n’arrivera pas.

2. TRANSACTION DIFFEREE :

Comme je l’ai promis, l’ordre de réception n’a pas d’importance. C’est à dire que
0 10 20 30 40 50 0
0 10 0 10 20 30 0

se comporte comme :
0 10 0 10 20 30 0
0 10 20 30 40 50 0

Pourquoi est-ce que ça marche ? Parce qu’un emplacement peut faire une transaction même sans avoir d’argent. Dès qu’il recevra de l’argent, il sera envoyé conformément à la transaction.

3. VALIDATION :

Bon, il est temps de comprendre comment fonctionne la validation d’une transaction.
Une transaction est confirmée une fois qu’elle validée par 7.5 ITV (soit 75% de l’argent initial).

Par exemple :

0 8 0 10 10 20 0
Va marcher

0 3 0 10 10 20 0
Ne va pas marcher tout de suite, mais si on ajoute le message suivant :
3 8 0 10 10 20 0
Là ça marche.

Les intervalles morts peuvent également valider une transaction.

Par exemple :

0 10 0 10 10 20 0 pour tuer [0, 10[. Puis,
0 10 10 20 20 30 0 fonctionne même si les pièces votantes sont mortes.

Donc vous pouvez laisser les deux premiers nombres à 0 10 et toutes les transactions fonctionneront.

Attends voir, ça veut dire que la quantité de validations peut dépasser la quantité d’argent initiale ?
Non, car si la même « pièce » est passée par ces deux intervalles, elle est comptée qu’une seule fois.
Et c’est LA tout l’interêt de cette cryptomonnaie : elle garde en memoire quel argent est passé par quel emplacement. 

Par exemple :

0 10 5 10 10 15 0 : [5, 10[ va dans [10, 15[ Ce sont les mêmes pièces qui sont passées de [5, 10[ à [10, 15[, donc [5, 15[ n’a que 5 ITV de pouvoir de validation, meme si tout l’intervalle est composé d’argent vivant ou mort.
5 15 0 5 50 55 0 : rien ne se passe, car la validation de [5, 15[ ne suffit pas.

4. VALIDATION DIFFEREE :

Rappelez-vous, l’ordre de réception n’a pas d’importance. Ce qui veut dire qu’un intervalle peut voter avant d’avoir reçu de l’argent. Ainsi :

10 20 10 20 20 30 0
0 10 0 10 10 20 0

équivaut à 

0 10 0 10 10 20 0
10 20 10 20 20 30 0

dans le premier cas, le vote de [10, 20[ reste en suspens. Puis il reçoit de l’argent. Donc les 10 ITV de validation sont débloqués, et valident la transaction de [10, 20[ vers [20, 30[.

5. NIVEAU :

On va enfin étudier le dernier nombre. Il désigne le level auquel l’argent va être envoyé. L’argent commence avec un level 0 et ne peut que monter de level. Ainsi :

0 10 0 10 20 30 0.1
est valide. Puis :
0 10 20 30 40 50 0
est une baisse de level, elle est donc invalide.

Un intervalle ne peut valider qu’une transaction de même level. Ainsi :

0 10 0 10 20 30 1
0 10 20 30 40 50 2
La deuxième transaction n’est validée que par de l’argent de level 1, qui n’a donc pas effet.

III. EN PRATIQUE :

Mon programme actuel ne fait qu’interpréter les messages de transactions reçus depuis le réseau InterVal. Aucun système d’identification n’a été implémenté pour l’instant. Quand tout sera implémenté, chaque compte n’aura accès qu’a un seul intervalle : [clépubliquecompte, clépubliquecompte + 1[, et ne pourra émettre de transaction et de vote que depuis cet intervalle (ce qui est vérifiable par l’ensemble du réseau car il chiffre ses messages avec la clé privée correspondante), ou une partie de cet intervalle.

1. VALIDATION AUTOMATIQUE :

Tous les clients se comportent ainsi en permanence :

A chaque réception de message, le client regarde si l’identification est correcte. 
- Si non, il supprime le message : tentative d’usurpation
- Si oui : 
	Il regarde s’il a déjà reçu un message correct dont l’argent sort du même intervalle.
	- Si oui, il stocke le message et ne fait rien : tentative de spam (si message identique) ou tentative de double-spend (si message différent).
	- Si non, il relaie le message + son propre message de validation à un max de gens (où le validateur est [clépubliqueclient, clépubliqueclient + 1[ tout entier).

Tous les jours à minuit, chaque compte doit faire une transaction vers un emplacement vide de son propre compte, de level égal à la date actuelle (en nombre de jours depuis le 1er janvier 1980).

2. ENVOI DE TRANSACTION :

Le récepteur doit déjà chercher un intervalle vide de taille suffisante [a,b[ sur ses comptes.
Il le montre à l’émetteur (cela peut se faire manuellement entre les deux utilisateurs, mais on peut implementer ça sur le réseau)

L’émetteur cherche un ensemble d’intervalles de ses comptes dont la somme est égale à la somme désirée.
Il émet sur le réseau, pour chaque intervalle [c,d[ :
clépubliqueémetteur clépubliqueémetteur+1 c d a b dateactuelle

IV. POURQUOI CA MARCHE :

Deux problèmes pourraient survenir :

- Une transaction met du temps à être validée / n’est jamais validée :
Ceci n’arrive que si l’ensemble des clients honnêtes connectés accumulent moins de 7.5 ITV sur le level actuel. C’est difficile à garantir, mais plus les gens se déconnectent, plus les transactions seront lentes, ce qui crée un incentive pour les comptes déjà existants pour laisser leur pc allumé 24/7 (ce qui n’est pas cher du tout en ressources).

- Un individu malhonnête parvient à faire passer deux transactions provenant du même intervalle au dessus des 7.5 ITV de validation, ce qui crée de la monnaie (cf section I. 1) :
Cet individu a deux manières de faire :
	- les deux transactions sont éloignées dans le temps. Mais alors personne ne va valider la deuxième à part le (ou les) individu malhonnête, dont on espère que le pouvoir de validation ne dépasse pas les 7.5 ITV sur le level actuel.
	- plus malin : les deux transactions sont envoyées en même temps de deux côtés du réseau. Dans le pire des cas, 50% des ITV présents à ce moment là vont valider l’une, 50% l’autre. Au final, dans le pire des cas, il faut que l’individu malhonnête ait plus de 5 ITV sur le level actuel pour valider les deux transaction (en validant avec 2.5 ITV d’un côté et 2.5 ITV de l’autre)

Pour avoir x ITV à un certain level, il faut que x « pièces » soit passées au moins une fois sur nos comptes pendant la même journée. On peut raisonnablement supposer qu’aucun individu ne verra passer 5 ITV sur ses comptes, faute de quoi le système entier est corrompu.

V. COMPORTEMENTS BIZARRES :

Ces règles étranges ne sont que des conséquences logiques des règles précédentes et du fait que le résultat ne dépend pas de l’ordre.

Dans le cas de plusieurs transferts validés vers le même intervalle :
- cet intervalle accumule le pouvoir de vote de tous ses parents. C’est le seul cas dans lequel un intervalle a un pouvoir de vote plus grand que sa taille.

0 10 0 5 20 25 0
0 10 5 10 20 25 0
20 25 20 25 30 35 0 Fonctionne meme si validé par un intervalle de taille 5

- les sous intervalles ont tous le même ratio (pouvoir de vote / taille).

0 10 0 5 20 25 0
0 10 5 10 20 25 0
20 25 20 25 30 35 0 Même chose que précédemment
30 34 30 35 40 45 0 Fonctionne meme si validé par un intervalle de taille 4 (8 ITV)
41 45 40 45 50 55 0 De même
50.5 54.5 50 55 60 65 0 De même
60 63 60 65 70 75 0 Ne fonctionne pas avec taille 3 (6 ITV)

- l’intervalle possède le level le plus petit de tous ses parents.

Have fun
