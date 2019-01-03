#!/usr/bin/env python3
from assemble import Y86Assmbler
import processor
import os
import sys

file = ""

def opt0():
    sys.exit(0)

def opt1():
    global file
    try:
        file = input("Input assembly file: ")
        Y86Assmbler().assemble(file)
    except:
        print("E: Wrong input or file doesnt exist!")

def opt2():
    try:
        start = int(input("Enter start address: 0x"),16)
        if start < 0x1000:
            print("E: Invalid address!")
    except:
        print("E: Invalid input!")
    try:
        fin = open(os.path.splitext(file)[0] + '.ybo', 'rb')
    except:
        print("E: File does not exist!")
    yasBin = fin.read().hex()
    try:
        fin.close()
    except:
        print("E: IOError!")
    binlen = len(yasBin) // 2
    end = 0x1000 + binlen
    length = int(input("Enter number of bytes: "))
    askEnd = start + length
    print(hex(askEnd))
    if askEnd > end:
        print("Invalid length")
    cnt = (start-0x1000)*2
    while start != askEnd:
        print(" 0x%x: %c%c" % (start,yasBin[cnt],yasBin[cnt+1]))
        cnt += 2
        start += 1
     

def opt3():
    try:
        inF = os.path.splitext(file)[0] + '.yo'
        fin = open(inF)
        print(fin.read())
        fin.close()
    except:
        print("E: File error!")

while True:
    print("")
    print("0.Exit")
    print("1.Input a ysm file path")
    print("2.Show memory")
    print("3.Show program")
    x = int(input("Select option: "))
    if x == 0:
        opt0()
    elif x == 1:
        opt1()
    elif x == 2:
        opt2()
    elif x == 3:
        opt3()
    else:
        print("Invalid option")

