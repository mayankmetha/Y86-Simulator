#!/usr/bin/env python3

import sys
import re
import os

ccFlags = {
    'ZF': 1,
    'SF': 0,
    'OF': 0
}

# opcodes value
instOpCode = {
    "00": "halt",
    "10": "nop",
    "20": "rrmovq",
    "21": "cmovle",
    "22": "cmovl",
    "23": "cmove",
    "24": "cmovne",
    "25": "cmovge",
    "26": "cmovg",
    "30": "irmovq",
    "40": "rmmovq",
    "50": "mrmovq",
    "60": "addq",
    "61": "subq",
    "62": "andq",
    "63": "xorq",
    "70": "jmp",
    "71": "jle",
    "72": "jl",
    "73": "je",
    "74": "jne",
    "75": "jge",
    "76": "jg",
    "80": "call",
    "90": "ret",
    "A0": "pushq",
    "B0": "popq"
}

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
    "A0": 2,
    "B0": 2
}

reg = ["%rax","%rcx","%rdx","%rbx","%rsp","%rbp","%rsi","%rdi","%r8","%r9","%r10","%r11","%r12","%r13","%r14"]
regFile = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
memDump = []
locDump = []

def lEndianInt(s):
    x = int('%c%c%c%c%c%c%c%c' % (s[6], s[7], s[4], s[5], s[2], s[3], s[0], s[1]))
    if x > 0x7fffffff:
        x = -((~x + 1) & 0xffffffff)
    return x

def simulateNoPipeline(step,file):
    pc = 0x1000
    try:
        f = os.path.splitext(file)[0] + '.ybo'
        fin = open(f,'r')
    except IOError:
        print('Error: cannot open file')
        sys.exit(1)
    cycle = 0
    for line in fin:
        print("Cycle: %s"%cycle)
        cycle += 1
        inst = instOpCode[line[0:2]]
        print("\tPC: 0x%x Instruction: %s"%(pc,inst))
        if line[0] in ('2','3','4','5','6','A','B'):
            rA = int(line[2],16)
            rB = int(line[3],16)
        if int(line[0]) == 2:
            regFile[rB] = regFile[rA]
        elif int(line[0]) == 3:
            regFile[rB] = lEndianInt(line[4:21])
        elif int(line[0]) == 6:
            opp = int(line[1])
            alures = regFile[rB]
            if opp == 0:
                alures = regFile[rB]+regFile[rA]
            elif opp == 1:
                alures = regFile[rB]-regFile[rA]
            elif opp == 2:
                alures = regFile[rB]&regFile[rA]
            elif opp == 3:
                alures = regFile[rB]^regFile[rA]
            ccFlags['ZF'] = 1 if alures == 0 else 0
            ccFlags['SF'] = 1 if alures < 0 else 0
            ccFlags['OF'] = 0
            if opp == 1 and ((regFile[rB] > 0 and regFile[rA] > 0 and alures < 0) and (regFile[rB] < 0 and regFile[rA] < 0 and alures > 0)):
                ccFlags['OF'] = 1
            if opp == 2 and ((regFile[rB] > 0 and regFile[rA] < 0 and alures < 0) and (regFile[rB] < 0 and regFile[rA] > 0 and alures > 0)):
                ccFlags['OF'] = 1
            regFile[rB] = alures
        if int(line[0]) == 8:
            pc = lEndianInt(line[4:])
        elif int(line[0]) == 7:
            pc = lEndianInt(line[4:])
        else:
            pc = pc + instByte[line[0:2]]
        
        for i in range(len(reg)):
            print("\t%s:%s"%(reg[i],regFile[i]))
        print("\tZF=%s"%ccFlags['ZF'])
        print("\tSF=%s"%ccFlags['SF'])
        print("\tOF=%s"%ccFlags['OF'])
        
        if step == True:
            input("Enter a key to continue: ")

    try:
        fin.close()
    except:
        pass