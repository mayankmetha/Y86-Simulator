#!/usr/bin/env python3
from assemble import Y86Assmbler
import simulate
import os
import sys

file = ""

def opt1():
    global file
    try:
        file = input("Input assembly file: ")
        Y86Assmbler().assemble(file)
    except:
        print("E: Wrong input or file doesnt exist!")
        return

def opt2():
    try:
        start = int(input("Enter start address: 0x"),16)
        if start < 0x1000:
            print("E: Invalid address!")
            return
    except:
        print("E: Invalid input!")
        return
    try:
        fin = open(os.path.splitext(file)[0] + '.yb', 'rb')
    except:
        print("E: File does not exist!")
        return
    yasBin = fin.read().hex()
    try:
        fin.close()
    except:
        print("E: IOError!")
        return
    binlen = len(yasBin) // 2
    length = int(input("Enter number of bytes: "))
    if length > binlen:
        print("E: Invalid length!")
        return
    cnt = (start-0x1000)*2
    ptr = 0
    while ptr != length:
        print(" 0x%x: %c%c" % ((start+ptr),yasBin[cnt],yasBin[cnt+1]))
        cnt += 2
        ptr += 1
     

def opt3():
    try:
        inF = os.path.splitext(file)[0] + '.yo'
        fin = open(inF)
        print(fin.read())
        fin.close()
    except:
        print("E: File error!")

def opt4():
    singleStep = input("Do you want single step?[y/n]: ")
    if singleStep in ('y','Y','yes','Yes','YES'):
        sStep = True
    elif singleStep in ('n','N','no','No','NO'):
        sStep = False
    else:
        print("E: Invalid input!")
    showRegs = input("Do you want to see registers and conditional flags?[y/n]: ")
    if showRegs in ('y','Y','yes','Yes','YES'):
        shRegs = True
    elif showRegs in ('n','N','no','No','NO'):
        shRegs = False
    else:
        print("E: Invalid input!")
    try:
        inCount = int(input("Enter number of execution required or enter -1 to ignore: "))
    except:
        print("E: Invalid input!")
    restart = True
    while restart == True:
        restart = simulate.simulateNoPipeline(inCount,shRegs,sStep,file)

while True:
    print("")
    print("0.Exit")
    print("1.Input a ysm file path")
    print("2.Show memory")
    print("3.Show program")
    print("4.Show execution")
    global x
    try:
        x = int(input("Select option: "))
    except:
        x = -1
    if x == 0:
        sys.exit(0)
    elif x == 1:
        opt1()
    elif x == 2:
        opt2()
    elif x == 3:
        opt3()
    elif x == 4:
        opt4()
    else:
        print("Invalid option")