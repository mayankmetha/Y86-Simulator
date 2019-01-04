#!/usr/bin/env python3

import os
import sys
import re

instByte = {
    "00": 1,
    "10": 1,
    "20": 2,
    "21": 2,
    "22": 2,
    "23": 2,
    "24": 2,
    "25": 2,
    "26": 2,
    "30": 10,
    "40": 10,
    "50": 10,
    "60": 2,
    "61": 2,
    "62": 2,
    "63": 2,
    "70": 9,
    "71": 9,
    "72": 9,
    "73": 9,
    "74": 9,
    "75": 9,
    "76": 9,
    "80": 9,
    "90": 1,
    "a0": 2,
    "b0": 2
}

regName = {
    0x0: "%rax",
    0x1: "%rcx",
    0x2: "%rdx",
    0x3: "%rbx",
    0x4: "%rsp",
    0x5: "%rbp",
    0x6: "%rsi",
    0x7: "%rdi",
    0x8: "%r8",
    0x9: "%r9",
    0xA: "%r10",
    0xB: "%r11",
    0xC: "%r12",
    0xD: "%r13",
    0xE: "%r14"
}

string = ''
binlen = 0
pc = 0
pcPad = 0x1000
icode = 0
ifun = 0
rA = 0xf
rB = 0xf
valC = ''
valP = 0
newPC = 0

def getOC(file):
    global string
    global binlen
    try:
        fin = open(os.path.splitext(file)[0] + '.ybo', 'rb')
    except:
        print('Error: cannot open binary: %s' % file)
        sys.exit(1)
    try:
        string = fin.read().hex()
    except:
        print('Error: cannot identify binary: %s' % (file))
        sys.exit(1)
    try:
        fin.close()
    except IOError:
        pass
    binlen = len(string) // 2

def lEndianReverseConv(s):
    x = int('%c%c%c%c%c%c%c%c' % (s[6], s[7], s[4], s[5], s[2], s[3], s[0], s[1]))
    if x > 0x7fffffff:
        x = -((~x + 1) & 0xffffffff)
    return x

def fetch():
    global pc
    global newPC
    global icode
    global ifun
    global valC
    global valP
    global rA
    global rB
    if pc != 0:
        pc = newPC
    icode = int(string[pc],16)
    ifun = int(string[pc+1],16)
    if icode in (0,1,7,8,9):
        rA = 0xf
        rB = 0xf
    else:
        rA = int(string[pc+2],16)
        rB = int(string[pc+3],16)
    if icode in (3,4,5):
        valC = str(string[pc+4:pc+21])
    elif icode in (7,8):
        valC = str(string[pc+2:pc+19])
    else:
        valC = ''
    valP = pc + instByte[string[pc:pc+2]]
    print(pc,icode,ifun,rA,rB,valC,valP)

getOC('demo.ybo')
fetch()
