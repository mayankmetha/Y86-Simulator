#!/usr/bin/env python3

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
addrlen = 4
logfile = None