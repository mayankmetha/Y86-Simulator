#!/usr/bin/env python3
from assemble import Y86Assmbler
import processor

file = input("Input assembly file: ")
Y86Assmbler().assemble(file)
processor.main(file)