#!/usr/bin/env python


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

class Binary:
    def __init__(self, n, bits):
        self.bin = '{:0{}b}'.format(n, bits)

    def __str__(self):
        return self.bin

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

class ALU:

    def __init__(self):
        self.in1 = 0
        self.in2 = 0
        self.control = 0

    def out(self):
        if self.control == 0:
            return self.in1 + self.in2

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

    reg_mux = MUX()

    instruction_memory = {
            0: Binary(0, 32),
            4: Binary(0xAFFFFFFF, 32)
            }

    instruction = Binary(0, 32)

    register_file = {
            "Read Register 1": 0,
            "Read Register 2": 0,
            "Write Register": 0,
            "Write Data": 0,
            "Read Data 1": 0,
            "Read Data 2": 0
            }

    registers = [0] * 32

    def __init__(self):
        self.pc_alu.in2 = 4 # Input to the PC ALU is always 4

    def instruction_fetch(self):
        self.instruction = self.instruction_memory[self.pc] # Get the instruction at PC
        
        self.pc_alu.in1 = self.pc

        self.pc = self.pc_alu.out() 


    def update_register_file(self):
        self.register_file["Read Register 1"] = self.instruction.digits(21,31)

        self.reg_mux.in1 = self.instruction.digits(0,4)
        self.reg_mux.in0 = self.instruction.digits(16,20)
        self.reg_mux.select = self.control["Reg2Loc"]

        self.register_file["Read Register 2"] = self.reg_mux.out
        self.register_file["Write Register"] = self.instruction.digits(0,4)
        # Need to do self.register_file["Write Data"]

  
    def instruction_decode(self):
        self.update_register_file()
        print(self.instruction.digits(0,31))

        
    def cycle(self):
        self.instruction_fetch()
        self.instruction_decode()


cpu = ARM()

cpu.cycle()
cpu.cycle()
