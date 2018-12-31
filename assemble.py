#!/usr/bin/env python3

import sys
import re

class Y86Assmbler:

    # initalization
    def __init__(self):

        # registers
        self.regs = {
            "%rax": "0",
            "%rcx": "1",
            "%rdx": "2",
            "%rbx": "3",
            "%rsp": "4",
            "%rbp": "5",
            "%rsi": "6",
            "%rdi": "7",
            "%r8": "8",
            "%r9": "9",
            "%r10": "A",
            "%r11": "B",
            "%r12": "C",
            "%r13": "D",
            "%r14": "E",
            "nor": "F"
        }

        # opcodes value
        self.instOpCode = {
            "halt": "00",
            "nop": "10",
            "rrmovq": "20",
            "cmovle": "21",
            "cmovl": "22",
            "cmove": "23",
            "cmovne": "24",
            "cmovge": "25",
            "cmovg": "26",
            "irmovq": "30",
            "rmmovq": "40",
            "mrmovq": "50",
            "addq": "60",
            "subq": "61",
            "andq": "62",
            "xorq": "63",
            "jmp": "70",
            "jle": "71",
            "jl": "72",
            "je": "73",
            "jne": "74",
            "jge": "75",
            "jg": "76",
            "call": "80",
            "ret": "90",
            "pushq": "A0",
            "popq": "B0"
        }

        # instruction size
        self.instByte = {
            "halt": 1,
            "nop": 1,
            "rrmovq": 2,
            "cmovle": 2,
            "cmovl": 2,
            "cmove": 2,
            "cmovne": 2,
            "cmovge": 2,
            "cmovg": 2,
            "irmovq": 10,
            "rmmovq": 10,
            "mrmovq": 10,
            "addq": 2,
            "subq": 2,
            "andq": 2,
            "xorq": 2,
            "jmp": 9,
            "jle": 9,
            "jl": 9,
            "je": 9,
            "jne": 9,
            "jge": 9,
            "jg": 9,
            "call": 9,
            "ret": 1,
            "pushq": 2,
            "popq": 2
        }

        # length of data word
        self.byteSize = {
            '.quad': 8,
            '.long': 4,
            '.word': 2,
            '.byte': 1 
        }
    
    # little endian conversion
    def lEndianStr(self, x, len):
        s = ''
        nlen = 0
        while x != 0 and nlen < len:
            s += "%.2x" % (x & 0xff)
            x = x>>8
            nlen += 1
        while nlen < len:
            s += '00'
            nlen +=1
        return s
    
    # error message display
    def printError(self, error):
        print("E: Assembly failed: ",error)
        sys.exit(1)

    # assembling Y86 code
    def assemble(self,inFile):
        try:
            fin = open(inFile)
        except IOError:
            print('E: Cannot open input file: ',inFile)
            sys.exit(1)

        lineCount = 0
        binCount = 0
        lineToken = []
        error = ''
        labels = {}
        yasLineNo = {}
        chompLine = {}
        alignment = 0

        # pass 1: label detection and error detection
        for lines in fin:
            lineCount += 1
            lineToken.append(lines)
            lines = re.sub(r'#.*$','',lines)
            lines = re.sub(r'/\*.*\*/','',lines)
            lines = re.sub(r'\s*,\s*',',',lines)
            if lines.find(':') != -1:
                lab = re.compile('([^\s]+):')
                labmatch = lab.search(lines)
                lines= lab.sub('',lines)
                if labmatch != None:
                    labelname = labmatch.group(1)
                else:
                    error += 'Line %d: %s\n' % (lineCount, 'Label error.')
                    continue
                if labelname in labels:
                    error += 'Line %d: %s\n' % (lineCount, 'Label repeated error.')
                    continue
                else:
                    labels[labelname] = binCount
                    yasLineNo[lineCount] = binCount
                lineList = []
                for ele in lines.split(' '):
                    e = ele.replace('\t','').replace('\n','').replace('\r','')
                    if e != '':
                        lineList.append(e)
                if lineList == []:
                    continue
                posIndex = str(lineCount)
                chompLine[posIndex] = lineList
                try:
                    if lineList[0] in self.instByte:
                        alignment = 0
                        yasLineNo[lineCount] = binCount
                        binCount += self.instByte[lineList[0]]
                    elif lineList[0] == '.pos':
                        binCount = int(lineCount[1],0)
                        yasLineNo[lineCount] = binCount
                    elif lineList[0] == '.align':
                        alignment = int(lineCount[1],0)
                        if binCount % alignment != 0:
                            binCount += alignment - binCount % alignment
                        yasLineNo[lineCount] = binCount
                    elif lineList[0] in self.byteSize:
                        yasLineNo[lineCount] = binCount
                        if alignment != 0:
                            binCount += alignment
                        else:
                            binCount += self.byteSize[lineList[0]]
                    else:
                        error += 'Line %d: Instruction "%s" not defined.\n' % (lineCount, lineList[0])
                        continue
                except:
                    error += 'Line %d: Instruction error.\n' % lineCount
                    continue
        try:
            fin.close()
        except IOError:
            pass
        if error != '':
            self.printError(error)

        # pass 2: generate object code
        