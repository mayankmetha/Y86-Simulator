from assemble import Y86Assmbler

file = input("Input assembly file: ")
obj = Y86Assmbler()
obj.assemble(file)
