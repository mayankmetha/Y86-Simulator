#!/usr/bin/env python3

import sys
import os

# register names
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

# opCode names
intrName = {
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

# register codes
R_RAX = 0x0
R_RCX = 0x1
R_RDX = 0x2
R_RBX = 0x3
R_RSP = 0x4
R_RBP = 0x5
R_RSI = 0x6
R_RDI = 0x7
R_R8 = 0x8
R_R9 = 0x9
R_R10 = 0xA
R_R11 = 0xB
R_R12 = 0xC
R_R13 = 0xD
R_R14 = 0xE
R_NONE = 0xF

# instruction codes
I_HALT = 0x0
I_NOP = 0x1
I_CMOV = 0x2
I_IRMOV = 0x3
I_RMMOV = 0x4
I_MRMOV = 0x5
I_OP = 0x6
I_J = 0x7
I_CALL = 0x8
I_RET = 0x9
I_PUSH = 0xA
I_POP = 0xB

# fetch none
F_NONE = 0x0

# alu op
A_ADD = 0x0
A_SUB = 0x1
A_AND = 0x2
A_XOR = 0x3

# jump op
J_JMP = 0x0
J_LE = 0x1
J_L = 0x2
J_E = 0x3
J_NE = 0x4
J_GE = 0x5
J_G = 0x6

# Pipeline F reg
F_predPC = 0
F_stat = 'BUB'

# Fetch intermediate values
f_icode = I_NOP
f_ifun = F_NONE
f_valC = 0x0
f_valP = 0x0
f_rA = R_NONE
f_rB = R_NONE
f_predPC = 0
f_stat = 'BUB'

# Pipeline D reg
D_stat = 'BUB'
D_icode = I_NOP
D_ifun = F_NONE
D_rA = R_NONE
D_rB = R_NONE
D_valP = 0x0
D_valC = 0x0
D_next_bub = False

# Decode intermediate values
d_srcA = R_NONE
d_srcB = R_NONE
d_dstE = R_NONE
d_dstM = R_NONE
d_valA = 0x0
d_valB = 0x0

# Pipeline E reg
E_stat = 'BUB'
E_icode = I_NOP
E_ifun = F_NONE
E_valC = 0x0
E_srcA = R_NONE
E_valA = 0x0
E_srcB = R_NONE
E_valB = 0x0
E_dstE = R_NONE
E_dstM = R_NONE

# Execute intermediate values
e_valE = 0x0
e_dstE = R_NONE
e_Cnd = False
e_setcc = False

# Pipeline M reg
M_stat = 'BUB'
M_icode = I_NOP
M_ifun = F_NONE
M_valA = 0x0
M_dstE = R_NONE
M_valE = 0x0
M_dstM = R_NONE
M_Cnd = False

# Memory intermediate values
m_valM = 0x0
m_stat = 'BUB'
mem_addr = 0x0
m_read = False
dmem_error = False

# Pipeline W reg
W_stat = 'BUB'
W_icode = I_NOP
W_ifun = F_NONE
W_dstE = R_NONE
W_valE = 0x0
W_dstM = R_NONE
W_valM = 0x0

# registers value
register = {
    0x0: 0,
    0x1: 0,
    0x2: 0,
    0x3: 0,
    0x4: 0,
    0x5: 0,
    0x6: 0,
    0x7: 0,
    0x8: 0,
    0x9: 0,
    0xA: 0,
    0xB: 0,
    0xC: 0,
    0xD: 0,
    0xE: 0,
    0xF: 0
}

# condition code flags
ccFlags = {
    'ZF': 1,
    'SF': 0,
    'OF': 0
}

# memory
mem = {}
memRo = []

# variables
cycle = 0
cpustat = 'AOK'
yasBin = ''
binlen = 0

def myHex(x, m = 0):
    if x < 0:
        x = (~(-x) + 1) & 0xffffffff
    if m == 0:
        return "%x" % (x)
    else:
        return "%.*x" % (m, x)

def getInstrName(icode, ifun):
    s = myHex(icode) + myHex(ifun)
    if s in intrName:
        return intrName[s]
    return 'INS'

def getRegName(x):
    if x == R_NONE:
        return '----'
    else:
        return register[x]
    
def getCCStr():
    return 'Z=%d S=%d O=%d' % \
            (ccFlags['ZF'], ccFlags['SF'], ccFlags['OF'])

# display messages
def logger(str):
    print(str)

# convert little endiam characters to int
def lEndianInt(s):
    a = '%c%c%c%c%c%c%c%c' % (s[6], s[7], s[4], s[5], s[2], s[3], s[0], s[1])
    b = '%c%c%c%c%c%c%c%c' % (s[14], s[15], s[12], s[13], s[10], s[11], s[8], s[9])
    x = int('%s%s' % (b, a), 16)
    if x > 0x7fffffffffffffff:
        x = -((~x + 1) & 0xffffffffffffffff)
    return x

# write to pipeline F reg
def writeF():
    global F_predPC
    global F_stat
    if I_RET in (D_icode,E_icode,M_icode) or (E_icode in (I_MRMOV, I_POP) and E_dstM in (d_srcA, d_srcB)):
        return
    F_predPC = f_predPC
    F_stat = f_stat

# next cycle pipeline F reg content
def nextF():
    global f_icode
    global f_ifun
    global f_valC
    global f_valP
    global f_rA
    global f_rB
    global f_predPC
    global f_stat
    pc = F_predPC
    if M_icode == I_J and not M_Cnd:
        pc = M_valA
    elif W_icode == I_RET:
        pc = W_valM
    oldPc = pc
    imem_Error = False
    if pc == binlen:
        f_icode = I_HALT
        f_ifun = F_NONE
        f_rA = R_NONE
        f_rB = R_NONE
        f_valC = 0x0
        f_valP = 0x0
        f_stat = 'HLT'
        return
    elif pc > binlen or pc < 0:
        imem_Error = True
    else:
        imem_icode = int(yasBin[pc])
        imem_ifun = int(yasBin[pc+1])
    f_icode = I_NOP if imem_Error else imem_icode
    f_ifun = F_NONE if imem_Error else imem_ifun
    instr_valid = f_icode in (I_NOP, I_HALT, I_CMOV, I_IRMOV, I_RMMOV, I_MRMOV, I_OP, I_J, I_CALL, I_RET, I_PUSH, I_POP)
    if instr_valid:
        try:
            if f_icode in (I_CMOV, I_OP, I_PUSH, I_POP, I_IRMOV, I_RMMOV, I_MRMOV):
                f_rA = R_NONE if f_rA == 0xf else int(yasBin[pc])
                f_rB = R_NONE if f_rB == 0xf else int(yasBin[pc+1])
            else:
                f_rA = R_NONE
                f_rB = R_NONE
            if f_icode in (I_HALT, I_NOP, I_RET):
                pc += 2
            elif f_icode in (I_IRMOV, I_MRMOV, I_RMMOV):
                pc += 20
            elif f_icode in (I_J, I_CALL):
                pc += 18
            else:
                pc += 4
            if (f_rA not in regName.keys() and f_rB != R_NONE) or (f_rB not in regName.keys() and f_rB != R_NONE):
                imem_Error = True
        except:
            imem_Error = True
        if not imem_Error:
            logger('\tFetch: f_pc = 0x%x, imem_instr = %s, f_instr = %s' % \
                   (oldPc, getInstrName(imem_icode, imem_ifun), getInstrName(f_icode, f_ifun)))
    if not instr_valid:
        logger('\tFetch: Instruction code 0x%s%s invalid' % (imem_icode, imem_ifun))
    f_valP = pc
    f_predPC = f_valC if f_icode in (I_J, I_CALL) else f_valP
    f_stat = 'AOK'
    if imem_Error:
        f_stat = 'ADR'
    if not instr_valid:
        f_stat = 'INS'
    if f_icode == I_HALT:
        f_stat = 'HLT'

# write to pipeline D reg
def writeD():
    global D_stat
    global D_icode
    global D_ifun
    global D_rA
    global D_rB
    global D_valP
    global D_valC
    global D_next_bub
    if E_icode in (I_MRMOV, I_POP) and E_dstM in (d_srcA, d_srcB):
        return
    if I_RET in (E_icode, M_icode, W_icode) or D_next_bub:
        D_icode = I_NOP
        D_ifun = F_NONE
        D_rA = R_NONE
        D_rB = R_NONE
        D_valC = 0x0
        D_valP = 0x0
        D_stat = 'BUB'
        if D_next_bub:
            D_next_bub = False
        return
    if E_icode == I_J and not e_Cnd:
        D_next_bub = True
    D_stat = f_stat
    D_icode = f_icode
    D_ifun = f_ifun
    D_rA = f_rA
    D_rB = f_rB
    D_valC = f_valC
    D_valP = f_valP

# next cycle pipeline D reg content
def nextD():
    global d_srcA
    global d_srcB
    global d_dstE
    global d_dstM
    global d_valA
    global d_valB
    d_srcA = R_NONE
    if D_icode in (I_CMOV, I_RMMOV, I_OP, I_PUSH):
        d_srcA = D_rA
    elif D_icode in (I_POP, I_RET):
        d_srcA = R_RSP
    d_srcB = R_NONE
    if D_icode in (I_OP, I_RMMOV, I_MRMOV):
        d_srcB = D_rB
    elif D_icode in (I_POP, I_PUSH, I_CALL, I_RET):
        d_srcB = R_RSP
    d_dstE = R_NONE
    if D_icode in (I_CMOV, I_IRMOV, I_OP):
        d_dstE = D_rB
    elif D_icode in (I_POP, I_PUSH, I_CALL, I_RET):
        d_dstE = R_RSP
    d_dstM = D_rA if D_icode in (I_MRMOV, I_POP) else R_NONE
    d_valA = register[d_srcA]
    if D_icode in (I_CALL, I_J):
        d_valA = D_valP
    elif d_srcA == e_dstE:
        d_valA = e_valE
    elif d_srcA == M_dstM:
        d_valA = m_valM
    elif d_srcA == M_dstE:
        d_valA = M_valE
    elif d_srcA == W_dstM:
        d_valA = W_valM
    elif d_srcA == W_dstE:
        d_valA = W_valE
    d_valB = register[d_srcB]
    if d_srcB == e_dstE:
        d_valB = e_valE
    elif d_srcB == M_dstM:
        d_valB = m_valM
    elif d_srcB == M_dstE:
        d_valB = M_valE
    elif d_srcB == W_dstM:
        d_valB = W_valM
    elif d_srcB == W_dstE:
        d_valB = W_valE

# write to pipeline E reg
def writeE():
    global E_stat
    global E_icode
    global E_ifun
    global E_valC
    global E_srcA
    global E_valA
    global E_srcB
    global E_valB
    global E_dstE
    global E_dstM
    if (E_icode == I_J and not e_Cnd) or E_icode in (I_MRMOV, I_POP) and E_dstM in (d_srcA, d_srcB):
        E_icode = I_NOP
        E_ifun = F_NONE
        E_valC = 0x0
        E_valA = 0x0
        E_valB = 0x0
        E_dstE = R_NONE
        E_dstM = R_NONE
        E_srcA = R_NONE
        E_srcB = R_NONE
        E_stat = 'BUB'
        return
    E_stat = D_stat
    E_icode = D_icode
    E_ifun = D_ifun
    E_valC = D_valC
    E_valA = d_valA
    E_valB = d_valB
    E_dstE = d_dstE
    E_dstM = d_dstM
    E_srcA = d_srcA
    E_srcB = d_srcB

# next cycle pipeline E reg content
def nextE():
    global ccFlags
    global e_Cnd
    global e_valE
    global e_dstE
    global e_setcc
    aluA = 0
    if E_icode in (I_CMOV, I_OP):
        aluA = E_valA
    elif E_icode in (I_IRMOV, I_RMMOV, I_MRMOV):
        aluA = E_valC
    elif E_icode in (I_CALL, I_PUSH):
        aluA = -8
    elif E_icode in (I_RET, I_POP):
        aluA = 8
    aluB = E_valB if E_icode in (I_RMMOV, I_MRMOV, I_OP, I_CALL, I_PUSH, I_RET, I_POP) else 0
    alufun = E_ifun if E_icode == I_OP else A_ADD
    alures = 0
    aluchar = '+'
    if alufun == A_ADD:
        alures = aluB + aluA
        aluchar = '+'
    elif alufun == A_SUB:
        alures = aluB - aluA
        aluchar = '-'
    elif alufun == A_AND:
        alures = aluB & aluA
        aluchar = '&'
    elif alufun == A_XOR:
        alures = aluB ^ aluA
        aluchar = '^'
    logger('\tExecute: ALU: 0x%s %c 0x%s = 0x%s' % (myHex(aluB), aluchar, myHex(aluA), myHex(alures)))
    e_setcc =  E_icode == I_OP and m_stat not in ('ADR', 'INS', 'HLT') and W_stat not in ('ADR', 'INS', 'HLT')
    if e_setcc:    
        ccFlags['ZF'] = 1 if alures == 0 else 0
        ccFlags['SF'] = 1 if alures < 0 else 0
        ccFlags['OF'] = 0
        if (E_ifun == A_ADD) and \
            ((aluB > 0 and aluA > 0 and alures < 0) or \
              aluB < 0 and aluB < 0 and alures > 0):
            ccFlags['OF'] = 1
        if (E_ifun == A_SUB) and \
            ((aluB > 0 and aluA < 0 and alures < 0) or \
              aluB < 0 and aluB > 0 and alures > 0):
            ccFlags['OF'] = 1
        logger('\tExecute: New cc = %s' % (getCCStr()))
    e_Cnd = False
    if E_icode == I_J or E_icode == I_CMOV:
        zf = ccFlags['ZF']
        sf = ccFlags['SF']
        of = ccFlags['OF']
        if E_ifun == J_JMP:
            e_Cnd = True
        elif E_ifun == J_LE and (sf ^ of) | zf == 1:
            e_Cnd = True
        elif E_ifun == J_L and sf ^ of == 1:
            e_Cnd = True
        elif E_ifun == J_E and zf == 1:
            e_Cnd = True
        elif E_ifun == J_NE and zf == 0:
            e_Cnd = True
        elif E_ifun == J_GE and sf ^ of == 0:
            e_Cnd = True
        elif E_ifun == J_G and (sf ^ of) | zf == 0:
            e_Cnd = True
        logger('\tExecute: instr = %s, cc = %s, branch %staken' % (getInstrName(E_icode, E_ifun), 'Z=%d S=%d O=%d' % (zf, sf, of), '' if e_Cnd else 'not '))
    e_valE = alures
    e_dstE = E_dstE
    if E_icode == I_CMOV and not e_Cnd:
        e_dstE = R_NONE

# write to pipeline M reg
def writeM():
    global M_stat
    global M_icode
    global M_ifun
    global M_Cnd
    global M_valE
    global M_valA
    global M_dstE
    global M_dstM
    if m_stat in ('ADR', 'INS', 'HLT') or W_stat in ('ADR', 'INS', 'HLT'):
        M_stat = 'BUB'
        M_icode = I_NOP
        M_ifun = F_NONE
        M_Cnd = False
        M_valE = 0x0
        M_valA = 0x0
        M_dstE = R_NONE
        M_dstM = R_NONE
        return
    M_stat = E_stat
    M_icode = E_icode
    M_ifun = E_ifun
    M_Cnd = e_Cnd
    M_valE = e_valE
    M_valA = E_valA
    M_dstE = e_dstE
    M_dstM = E_dstM

# next cycle pipeline M reg content
def nextM():
    global mem
    global dmem_error
    global m_stat
    global m_valM
    global m_read
    global mem_addr
    global memRo
    m_valM = 0
    mem_addr = 0
    dmem_error = False
    if M_icode in (I_RMMOV, I_PUSH, I_CALL, I_MRMOV):
        mem_addr = M_valE
    elif M_icode in (I_POP, I_RET):
        mem_addr = M_valA
    if M_icode in (I_MRMOV, I_POP, I_RET):
        try:
            if mem_addr not in mem:
                # TODO: check yasbin index
                mem[mem_addr] = lEndianInt(yasBin[mem_addr * 2:mem_addr * 2 + 16])
                memRo.append(mem_addr)
            m_valM = mem[mem_addr]
            m_read = True
            logger('\tMemory: Read 0x%s from 0x%x' % (myHex(m_valM), mem_addr))
        except:
            dmem_error = True
            logger('\tMemory: Invalid address 0x%s' % (myHex(mem_addr)))
    if M_icode in (I_RMMOV, I_PUSH, I_CALL):
        try:
            if mem_addr in memRo or mem_addr < 0:
                raise Exception
            mem[mem_addr] = M_valA
            logger('\tWrote 0x%s to address 0x%x' % (myHex(M_valA), mem_addr))
        except:
            dmem_error = True
            logger('\tCouldn\'t write to address 0x%s' % (myHex(mem_addr)))
    m_stat = 'ADR' if dmem_error else M_stat

# write to pipeline W reg
def writeW():
    global W_stat
    global W_icode
    global W_ifun
    global W_dstE
    global W_valE
    global W_dstM
    global W_valM
    if W_stat in ('ADR', 'INS', 'HLT'):
        return
    W_stat = m_stat
    W_icode = M_icode
    W_ifun = M_ifun
    W_valE = M_valE
    W_valM = m_valM
    W_dstE = M_dstE
    W_dstM = M_dstM

# next cycle pipeline W reg content
def nextW():
    global register
    global cpustat
    global cycle
    if W_dstE != R_NONE:
        register[W_dstE] = W_valE
        logger('\tWriteback: Wrote 0x%s to register %s' % (myHex(W_valE), register[W_dstE]))
    if W_dstM != R_NONE:
        register[W_dstM] = W_valM
        logger('\tWriteback: Wrote 0x%s to register %s' % (myHex(W_valM), register[W_dstM]))
    cpustat = 'AOK' if W_stat == 'BUB' else W_stat

def main(file):
    maxCycles = 65535
    try:
        fin = open(os.path.splitext(file)[0] + '.ybo', 'rb')
    except:
        print('Error: cannot open binary: %s' % file)
        sys.exit(1)
    global yasBin
    global binlen
    try:
        yasBin = fin.read().hex()
    except:
        print('Error: cannot identify binary: %s' % (file))
        sys.exit(1)
    try:
        fin.close()
    except IOError:
        pass
    binlen = len(yasBin) // 2
    logger('%d bytes of code read' % (binlen))
    global cycle
    global cpustat
    try:
        while True:
            print("Cycle:%x" % cycle)
            writeW()
            nextW()
            writeM()
            nextM()
            writeE()
            nextE()
            writeD()
            nextD()
            writeF()
            nextF()
            if maxCycles != 0 and cycle > maxCycles:
                cpustat = 'HLT'
            if cpustat != 'AOK' and cpustat != 'BUB':
                break
            cycle += 1
    except:
        print('Error: bad input binary file')
        sys.exit(1)
    print("Done")