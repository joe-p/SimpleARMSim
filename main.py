#!/usr/bin/env python


class ALU:

    def __init__(self):
        self.in1 = 0
        self.in2 = 0
        self.out = 0

    def add(self):
        out = in1+in2

class ARM:

    control = {
            "Reg2Loc": 0,
            "Branch": 0,
            "MemRead": 0,
            "MemtoReg": 0,
            "ALUOp": 0,
            "MemWrite": 0,
            "ALUSrc": 0,
            "RegWrite": 0
            }

    pc = 0

    pc_alu = ALU() 
    mem_alu = ALU()

    instruction_memory = {
            0: 0x0000,
            4: 0x0000
            }

    instruction = 0x0000

    def __init__(self):
        pc_alu.in2 = 4 # Input to the PC ALU is always 4

    def instruction_fetch(self):
        pc_alu.in1 = pc
        pc_alu.add() # pc + 4

        instruction = instruction_memory[pc]

    def instruction_decode(self):
        pass
