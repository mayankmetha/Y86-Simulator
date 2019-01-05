#!/usr/bin/env python3

import sys
import os

# condition flags
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

# byte size per instruction
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

# convert from lEndian to int
def lEndianInt(s):
    a = '%c%c%c%c%c%c%c%c' % (s[6], s[7], s[4], s[5], s[2], s[3], s[0], s[1])
    b = '%c%c%c%c%c%c%c%c' % (s[14], s[15], s[12], s[13], s[10], s[11], s[8], s[9])
    x = int('%s%s'%(b,a),16)
    if x > 0x7FFFFFFFFFFFFFFF:
        x = -((~x + 1) & 0xFFFFFFFFFFFFFFFF)
    return x

# condition flags   
def conditions(s):
    zf = ccFlags['ZF']
    sf = ccFlags['SF']
    of = ccFlags['OF']
    if s == 0:
        return True
    elif s == 1 and (sf ^ of) | zf == 1:
        return True
    elif s == 2 and sf ^ of == 1:
        return True
    elif s == 3 and zf == 1:
        return True
    elif s == 4 and zf == 0:
        return True
    elif s == 5 and sf ^ of == 0:
        return True
    elif s == 6 and (sf ^ of) | zf == 0:
        return True
    else :
        return False

def validateInCount(count):
    if count == -1:
        return True
    elif count == 0:
        return False
    else:
        return True

# sequential pipeline
def simulateNoPipeline(inCount, showRegs,step,file):
    reg = ["%rax","%rcx","%rdx","%rbx","%rsp","%rbp","%rsi","%rdi","%r8","%r9","%r10","%r11","%r12","%r13","%r14"]
    regFile = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    memDump = []
    locDump = []
    memory = {}
    try:
        f = os.path.splitext(file)[0] + '.ybo'
        fin = open(f,'r')
    except IOError:
        print('Error: cannot open file')
        sys.exit(1)
    x = 0x1000
    for line in fin:
        if line != '':
            locDump.append(x)
            memDump.append(line.strip('\n'))
            x += instByte[line[0:2]]
    try:
        fin.close()
    except:
        pass
    index = 0
    cycle = 0
    regFile[reg.index("%rsp")] = 0x3000
    while index < len(memDump) and cycle < 64:
        if validateInCount(inCount) == False:
            return False
        else:
            inCount -= 1
        line = memDump[index]
        print("Instruction Count: %s"%cycle)
        cycle += 1
        inst = instOpCode[line[0:2]]
        print("\tPC: 0x%x\n\tInstruction: %s"%(locDump[index],inst))
        if line[0] in ('2','3','4','5','6','A','B'):
            rA = int(line[2],16)
            rB = int(line[3],16)
        if int(line[0],16) == 0:
            if showRegs == True:
                print("\tRegisters:")
                for i in range(len(reg)):
                    print("\t\t%s:0x%x"%(reg[i],regFile[i]))
                print("\tConditional Flags:")
                print("\t\tZF=%s"%ccFlags['ZF'])
                print("\t\tSF=%s"%ccFlags['SF'])
                print("\t\tOF=%s"%ccFlags['OF'])
            return
        elif int(line[0],16) == 2:
            if conditions(int(line[1],16)) == True:
                regFile[rB] = regFile[rA]
        elif int(line[0],16) == 3:
            regFile[rB] = lEndianInt(line[4:21])
        elif int(line[0],16) == 6:
            opp = int(line[1],16)
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
        elif int(line[0],16) == 0xA:
            memory[regFile[reg.index("%rsp")]] = regFile[rA]
            regFile[reg.index("%rsp")] -= 8
        elif int(line[0],16) == 0xB:
            if regFile[reg.index("%rsp")] + 8 > 0x3000:
                pass
            else:
                regFile[rA] = memory[regFile[reg.index("%rsp")]]
                memory.pop(regFile[reg.index("%rsp")])
                regFile[reg.index("%rsp")] += 8
        if int(line[0],16) == 9:
            if regFile[reg.index("%rsp")] + 8 > 0x3000:
                if showRegs == True:
                    print("\tRegisters:")
                    for i in range(len(reg)):
                        print("\t\t%s:0x%x"%(reg[i],regFile[i]))
                    print("\tConditional Flags:")
                    print("\t\tZF=%s"%ccFlags['ZF'])
                    print("\t\tSF=%s"%ccFlags['SF'])
                    print("\t\tOF=%s"%ccFlags['OF'])
                return
            else:
                index = memory[regFile[reg.index("%rsp")]]
                memory.pop(regFile[reg.index("%rsp")])
                regFile[reg.index("%rsp")] += 8
        elif int(line[0],16) == 8:
            memory[regFile[reg.index("%rsp")]] = locDump[index+1]
            regFile[reg.index("%rsp")] -= 8
            index = locDump.index(lEndianInt(line[2:]))
        elif int(line[0],16) == 7:
            if conditions(int(line[1],16)) == True:
                index = locDump.index(lEndianInt(line[2:]))
            else:
                index +=1
        else:
            index += 1
        
        if showRegs == True:
            print("\tRegisters:")
            for i in range(len(reg)):
                print("\t\t%s:0x%x"%(reg[i],regFile[i]))
            print("\tConditional Flags:")
            print("\t\tZF=%s"%ccFlags['ZF'])
            print("\t\tSF=%s"%ccFlags['SF'])
            print("\t\tOF=%s"%ccFlags['OF'])
        
        if step == True:
            key = input("Enter a r to restart else any other key to continue: ")
            if key in ('r','R'):
                print("Restarting execution")
                return True
            else: 
                pass
            
    return False
        
