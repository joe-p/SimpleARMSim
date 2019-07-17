#!/usr/bin/env python

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


    def alu(self):
        pass

    def instruction_fetch(self):
        pass

    def instruction_decode(self):
        pass
