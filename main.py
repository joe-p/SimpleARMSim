#!/usr/bin/env python

class Binary:
    def __init__(self, n, bits):
        self.bin = '{:0{}b}'.format(n, bits)

    def __str__(self):
        return self.bin

    def __int__(self):
        return int(self.bin)

    def digit(self, n):
        # Reverses so 0 is LSB, instead of MSB
        return self.bin[::-1][n]

    # digits() retuns the specified bit range
    # Example (Binary(0x0F).digits(0,3)) will return 1111
    def digits(self, start, end):
        s=""
        end += 1
        size = end - start

        for n in range(start, end):
            s = (self.digit(n)) + s

        return Binary(int(s,2), size)


class RFormat():
    def __init__(self, name, instruction_bits):
        self.format = "R"
        self.name = name

        self.opcode = instruction_bits.digits(31,21)
        self.rm = instruction_bits.digits(20,16)
        self.shamt = insutrction_bits.digits(15,10)
        self.rn = instruction_bits.digits(9,5)
        self.rd = instruction_buts.digits(4,0)


class MUX:
    def __init__(self):
        self.in0 = 0
        self.in1 = 0
        self.select = 0

    def out(self):
        if self.select == 1:
            return in1
        else:
            return in0

class ALU:

    def __init__(self):
        self.in1 = 0
        self.in2 = 0
        self.control = 0

    def out(self):
        if self.control == 0:
            return self.in1 + self.in2

class ARM:

    pc = 0

    pc_alu = ALU() 

    instruction_memory = {
            0: Binary(0, 32),
            4: Binary(0xAFFFFFFF, 32)
            }

    instruction = Binary(0, 32)

    register = [0] * 32

    def __init__(self):
        self.pc_alu.in2 = 4 # Input to the PC ALU is always 4 
        
        # Initial values are zero
        self.dataA = 0
        self.dataB = 0
        self.imm = 0
        self.npc = 4

    def instruction_fetch(self):
         
        self.instruction_bits = self.instruction_memory[self.pc] # Get the instruction at PC
        
        self.pc_alu.in1 = self.pc

        i = int(self.instruction_bits)
        ib = self.instruction_bits

        if i == 1112:
            self.instruction = RFormat("ADD", ib)
        elif i == 1624:
            self.instruction = RFormat("SUB", ib)
        elif i == 1160 or i == 1161:
            self.instruction = IFormat("ADDI", ib)
        elif i == 1672 or i == 1673:
             self.instruction = IFormat("SUBI", ib)
        elif i == 1104:
            self.instruction = RFormat("AND", ib)
        elif i == 1360:
            self.instruction = RFormat("ORR", ib)
        elif i == 1986:
            self.instruction =  DFormat("LDUR", ib)
        elif i == 1984:
            self.instruction =  DFormat("STUR", ib)
        elif 1440 < i < 1447:
            self.instruction = CBFormat("CBZ", ib)
        elif 160 < i < 191:
            self.instruction = BFormat("B", ib)
        
        self.npc = self.pc_alu.out() 
        
        # IF pipeline here

    def instruction_decode(self):
        
        i = self.instruction

        if i.format = "R":
            self.dataA = i.rn
            self.dataB = i.rm
        elif i.format = "D":
            self.imm = i.address
            self.dataA = i.rt # goes to write data
            self.dataB = i.rn # goes into ALU with imm
        elif i.format = "CB":
            self.dataA = i.rn
            self.dataB = i.address
        elif i.format = "B":
            self.dataB = i.address
        elif i.format = "I":
            self.imm = i.immediate

        # ID pipeline reg here

    def cycle(self):
        self.instruction_fetch()
        self.instruction_decode()

cpu = ARM()

cpu.cycle()
cpu.cycle()
