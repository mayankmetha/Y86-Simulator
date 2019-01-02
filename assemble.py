#!/usr/bin/env python3

import sys
import re
import os
import binascii

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
        print("E: Assembly failed:\n%s" % error)
        sys.exit(1)

    # assembling Y86 code
    def assemble(self,inFile):
        try:
            fin = open(inFile)
        except IOError:
            print('E: Cannot open input file:%s' % inFile)
            sys.exit(1)

        lineCount = 0
        binCount = 0x1000
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
                lab = re.compile(r'([^\s]+):')
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
            chompLine[lineCount] = lineList
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

        yasObj= {}
        # pass 2: generate object code
        for l in chompLine:
            try:
                lineCount = int(l)
            except:
                print('E: unexpected internal error')
                sys.exit(1)
            lineList = chompLine[l]
            if lineList == []:
                continue
            resBin = ''
            if lineList[0] in self.instOpCode:
                alignment = 0
                try:
                    if lineList[0] in ('nop', 'halt', 'ret'):
                        resBin = self.instOpCode[lineList[0]]
                    elif lineList[0] in ('pushq', 'popq'):
                        resBin = self.instOpCode[lineList[0]] + self.regs[lineList[1]] + self.regs["nor"]
                    elif lineList[0] in ('addq', 'subq', 'andq', 'xorq', 'rrmovq') or lineList[0].startswith('cmov'):
                        regList = lineList[1].split(",")
                        resBin = self.instOpCode[lineList[0]] + self.regs[regList[0]] + self.regs[regList[1]]
                    elif lineList[0].startswith('j') or lineList[0] == 'call':
                        resBin = self.instOpCode[lineList[0]]
                        if lineList[1] in labels:
                            resBin += self.lEndianStr(labels[lineList[1]],8)
                        else:
                            res += self.lEndianStr(int(lineList[1],0),8)
                    elif lineList[0] == 'irmovq':
                        regList = lineList[1].split(",")
                        if regList[0] in labels:
                            addr = self.lEndianStr(labels[regList[0]],8)
                        else:
                            addr = self.lEndianStr(int(regList[0].replace('$',''),0),8)
                        resBin = self.instOpCode[lineList[0]] + self.regs['nor'] + self.regs[regList[1]] + addr
                    elif lineList[0] in ('rmmovq', 'mrmovq'):
                        regList = lineList[1].split(",")
                        if lineList[0] == 'rmmovq':
                            memStr = regList[1]
                            self.reg = regList[0]
                        elif lineList[0] == 'mrmovq':
                            memStr = regList[0]
                            self.reg = regList[1]
                        regex = re.compile(r'\((.+)\)')
                        regmatch = regex.search(memStr)
                        memInt = regex.sub('', memStr)
                        if memInt == '' or memInt == None:
                            memInt = '0'
                        resBin = self.instOpCode[lineList[0]] + self.regs[self.reg] + self.regs[regmatch.group(1)] +self.lEndianStr(int(memInt,0),8)
                    else:
                        error += 'Line %d: Instruction "%s" not defined.\n' % (lineCount, lineList[0])
                        continue
                except:
                    error += 'Line %d: Instruction error.\n' % lineCount
                    continue
            else:
                try:
                    if lineList[0] == '.pos':
                        pass
                    elif lineList[0] == '.align':
                        alignment = int(lineList[1],0)
                    elif lineList[0] in self.byteSize:
                        if alignment != 0:
                            length = alignment
                        else:
                            length = self.byteSize[lineList[0]]
                        if lineList[1] in labels:
                            resBin = self.lEndianStr(labels[lineList[1]], length)
                        else:
                            resBin = self.lEndianStr(int(lineList[1],0), length)
                    else:
                        error += 'Line %d: Alignment error.\n' % lineCount
                        continue
                except:
                    error += 'Line %d: Alignment error.\n' % lineCount
                    continue
            if resBin != '':
                yasObj[lineCount] = resBin
            
        # output to .yo file
        lineCount = 0
        binCount = 0
        maxaddrlen = 4
        if error != '':
            self.printError(error)
        else:
            outFile = os.path.splitext(inFile)[0] + '.yo'
            outBinFile = os.path.splitext(inFile)[0] + '.ybo'
            try:
                fout = open(outFile,'w')
                fbout = open(outBinFile,'wb')
            except IOError:
                print('Error: cannot create output file')
                sys.exit(1)
            for line in lineToken:
                lineCount += 1
                if(lineCount in yasObj) and (lineCount in yasLineNo):
                    ystr = yasObj[lineCount]
                    nowaddr = yasLineNo[lineCount]
                    if binCount != nowaddr:
                        tmp = '0'*(2*(nowaddr-binCount))
                        fbout.write(binascii.a2b_hex(tmp))
                        binCount = nowaddr
                    binCount += len(ystr)//2
                    fout.write('  0x%.*x: %-20s | %s' % (maxaddrlen, nowaddr, ystr, line))
                    fbout.write(binascii.a2b_hex(ystr))
                elif lineCount in yasLineNo:
                    nowaddr = yasLineNo[lineCount]
                    fout.write('  0x%.*x:                      | %s' % (maxaddrlen, nowaddr, line))
                else:
                    fout.write((' ' * (maxaddrlen + 27)) + '| %s' % line)
            try:
                fout.close()
                fbout.close()
            except IOError:
                pass
            print('Assembled file: %s' % os.path.basename(inFile))

# main
def main():
    obj = Y86Assmbler()
    obj.assemble(sys.argv[1])

if __name__ == '__main__':
    main()