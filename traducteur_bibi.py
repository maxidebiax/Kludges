#!/usr/bin/python
# -*- coding: utf-8  -*-
import math, binascii
"""
    Traducteur/Encodeur Bi-bi-binaire
"""
# TODO :
# * conversion en image

theme = {'0000' : 'ho',   '0001' : 'ha',    '0010' : 'he',    '0011' : 'hi',
         '0100' : 'bo',   '0101' : 'ba',    '0110' : 'be',    '0111' : 'bi',
         '1000' : 'ko',   '1001' : 'ka',    '1010' : 'ke',    '1011' : 'ki',
         '1100' : 'do',   '1101' : 'da',    '1110' : 'de',    '1111' : 'di' }
version = {v:k for k, v in theme.items()}

def asciiToBin(lettre):
    lettre = ord(lettre)
    retour = []
    for i in range(8,-1,-1):
        if lettre -2**i >= 0:
            lettre -= 2**i
            retour.append('1')
        else:
            retour.append('0')
    return "".join(retour)

def binaire(chaine):
    """
    on aurait pu passer par
    return bin(int(binascii.hexlify(chaine.encode('ascii', 'strict')), 16))[2:]
    mais il tronque des zéros :/
    """
    retour =[asciiToBin(lettre) for lettre in chaine]
    return "".join(retour) 

def bibi(b):
    """ Theme
    """
    rep = ""
    deb = 1
    fin = 5
    bout = len(b)
    while fin <= bout:
        rep += theme[b[deb:fin]]
        deb += 4
        fin += 4
    return rep

def debibi(phrase):
    """ Version
    """
    duet = int(math.floor(len(phrase)/2))
    rep = ""
    for i in range(0, duet):
        j = i*2
        mot = phrase[j:j+2]
        rep = rep + version[mot]
    return rep

def menu():
    # Menu principal
    print("==  Traducteur Bibi  ==")
    print("1. ASCII vers Bibi")
    print("2. Bibi  vers ASCII")
    #print("3. Bibi  vers PNG")

menu()
mode = input('Mode ? ')
if mode == "1":
    phrase = input('Phrase : ')
    traduction = bibi(binaire(phrase))
    print(traduction)
elif mode == "2":
    bibi = input('Bibi : ')
    traduction = binascii.unhexlify("%x" % int('0b'+debibi(bibi), 2))
    print(traduction)
else:
    print("Mode inconnue")
