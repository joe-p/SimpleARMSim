#!/usr/bin/env python

class Binary:
    def __init__(self, n, bits):
        self.bin = '{:0{}b}'.format(n, bits)

    def __str__(self):
        return self.bin

    def __int__(self):
        return int(self.bin, 2)

    def digit(self, n):
        # Reverses so 0 is LSB, instead of MSB
        return self.bin[::-1][n]

    # digits() retuns the specified bit range
    # Example (Binary(0x0F).digits(0,3)) will return 1111
    def digits(self, end, start):
        s=""
        end += 1
        size = end - start

        for n in range(start, end):
            s = (self.digit(n)) + s

        return Binary(int(s,2), size)

class RFormat:
    def __init__(self, name, inst):
        self.format = "R"
        self.name = name

        self.opcode = inst.digits(31,21)
        self.rm = inst.digits(20,16)
        self.shamt = inst.digits(15,10)
        self.rn = inst.digits(9,5)
        self.rd = inst.digits(4,0)

class IFormat:

    def __init__(self, name, inst):
        self.format = "I"
        self.name = name

        self.opcode = inst.digits(31,22)
        self.immediate = inst.digits(21,10)
        self.rn = inst.digits(9,5)
        self.rt = inst.digits(4,0)

class DFormat:
    def __init__(self, name, inst):
        self.format = "D"
        self.name = name

        self.opcode = inst.digits(31,21)
        self.address = inst.digits(20,12)
        self.op2 = inst.digits(11,10)
        self.rn = inst.digits(9,5)
        self.rt = inst.digits(4,0)

class CBFormat:
    def __init__(self, name, inst):
        self.format = "CB"
        self.name = name

        self.opcode = inst.digits(31,24)
        self.address = inst.digits(23,5)
        self.rt = (4,0)

class BFormat:
    def __init__(self, name, inst):
        self.format = "B"
        self.name = name

        self.opcode = inst.digits(31,26)
        self.address = inst.digits(25,0)

class MUX:
    def __init__(self, in0, in1):
        self.in0 = in0
        self.in1 = in1
        self.select = 0

    def out(self):
        if self.select == 1:
            return self.in1
        else:
            return self.in0

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

    alu = ALU()

    data_memory= [0] * 256

    instruction_memory = {
            0: Binary(0b10010001000000000000000000010101, 32), # ADDI, X21, X0, 0
            4: Binary(0b100100010000000110010000000010111, 32), # ADDI, X22, X0, 100
            8: Binary(0b100100010000000000101000000011000, 32), # ADDI, X23, X0, 10
            12: Binary(0b11010001000000000001001010101001, 32), # SUBI X9, X21, 4
            16: Binary(0b10110100000000000000000010001001, 32), # CBZ X9, 4
            20: Binary(0b110010110001100000000010111010111, 32), # SUB X22, X22, X23
            24: Binary(0b10010001000000000000011010110101, 32), # ADDI x21, x21, 1
            #28: Binary(0b00010111111111111111111111111100, 32) # B -4
            28: Binary(0b00010100000000000000000000000100, 32)
            }

    instruction = None

    register = [0] * 32

    def __init__(self):
        self.pc_alu.in2 = 4 # Input to the PC ALU is always 4 
        
        # Initial values are zero
        self.dataA = 0
        self.dataB = 0
        self.imm = 0
        self.npc = 4
        self.lmd = 0
        self.alu_out = 0
        self.cond = 0

    def instruction_fetch(self):
         
        self.instruction_bits = self.instruction_memory[self.pc] # Get the instruction at PC
        
        self.pc_alu.in1 = self.pc

        i = int(self.instruction_bits.digits(31,21))
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

        if i.format == "R":
            self.dataA = self.register[int(i.rn)]
            self.dataB = self.register[int(i.rm)]
        elif i.format == "D":
            self.imm = int(i.address)
            self.dataA = int(i.rn) # goes to write data
            self.dataB = int(i.rt) # goes into ALU with imm
        elif i.format == "CB":
            self.dataA = self.register[int(i.rt)]
            self.dataB = int(i.address)
        elif i.format == "B":
            self.dataB = int(i.address)
        elif i.format == "I":
            self.imm = int(i.immediate)

        # ID pipeline reg here

    def execution(self):

        i = self.instruction

        mux0 = MUX(self.npc, self.dataA)
        mux1 = MUX(self.dataB, self.imm)
        
        if i.format == "R":
            mux0.select = 1
            mux1.select = 0
        elif i.format == "I":
            mux0.select = 1
            mux1.select = 1
        elif i.format == "D":
            mux0.select = 1
            mux1.select = 1
        elif i.format == "CB":
            mux0.select = 0
            mux1.select = 1
            if self.dataA == 0:
                self.cond = self.dataA
        elif i.format == "B":
            mux0.select = 0
            mux1.select = 1
        self.alu.in1 = mux0.out()
        self.alu.in2 = mux1.out()
        if i.format == "CB" or i.format == "B":
            self.alu.in1 -= 4
            self.alu.in2 <<= 2
            self.alu_out = self.alu.out()
        else:
            self.alu_out = self.alu.out()
            
    
    def memory_access(self):

        i = self.instruction

        mux = MUX(self.npc, self.alu_out)

        if i.name == "LDUR":
            self.lmd = self.data_memory[self.alu_out*8]
        elif i.name == "STUR":
            self.data_memory[self.alu_out*8] = self.dataB
        elif i.name == "CBZ":
            if self.cond == 0:
                mux.select = 1
            else:
                mux.select = 0
            self.pc = mux.out()
        elif i.name == "B":
            mux.select = 1
            self.pc = mux.out()
            


    def write_back(self):

        i = self.instruction

        mux = MUX(self.lmd, self.alu_out)

        if i.format == "R":
            mux.select = 1
            self.register[int(i.rd)] = mux.out()
        elif i.format == "I":
            mux.select = 1
            self.register[int(i.rt)] = mux.out()
        elif i.name == "LDUR":
            mux.select = 0
            self.register[int(i.rt)] = mux.out()
        elif i.name == "STUR":
            self.register[self.alu_out] = self.data_memory[self.alu_out*8]

        for i in range(0,31):
                addr = i * 8
                self.data_memory[addr] = self.register[i]
        

    def cycle(self):
        self.instruction_fetch()
        self.instruction_decode()
        print(self.instruction.name)
        self.execution()
        self.memory_access()
        self.write_back()
        print(self.register)
        print(self.npc)
        self.pc = self.npc # placeholder for testing

cpu = ARM()

#import file
#read to instruction memory
print(cpu.instruction_memory)
print(cpu.register)
print(cpu.data_memory)
for i in range(len(cpu.instruction_memory)):
    cpu.cycle()
print(cpu.register)
print(cpu.data_memory)