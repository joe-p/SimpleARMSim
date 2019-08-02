#!/usr/bin/env python
import threading
import time
# Binary is a class used to to easily manipulate binary numbers
class Binary:
    def __init__(self, n, bits):

        # We need to convert the negative number using two's complement
        if n < 0:
            self.neg = n
            n = n*-1

            l_bin = list('{:0{}b}'.format(n, bits)) # Convert to binary
            
            for i in range(len(l_bin)):
                # Flip each bit
                if int(l_bin[i]):
                    l_bin[i] = "0"
                else:
                    l_bin[i] = "1"

            twos_comp = "".join(l_bin)
            twos_comp = Binary(int(twos_comp, 2) + 1, bits)

            self.bin = twos_comp.bin

        else:
            self.bin = '{:0{}b}'.format(n, bits) # Convert to binary
    
    # undone_twos() will undo a number that is in twos complement to get the original negative integer
    def undone_twos(self):

        l_bin = list(self.bin)

        for i in range(len(l_bin)):
            if int(l_bin[i]):
                l_bin[i] = "0"
            else:
                l_bin[i] = "1"

        undone = "".join(l_bin)
        undone = -1 *(int(undone, 2) + 1)
        return undone

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


# Each of the xFormat classes contain information about a register (format, name, and values)
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
        self.rt = inst.digits(4,0)

class BFormat:
    def __init__(self, name, inst):
        self.format = "B"
        self.name = name

        self.opcode = inst.digits(31,26)
        self.address = inst.digits(25,0)

# The mux class is used to simulate a MUX
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
# The Alu class is used to simulate an ALU
class ALU:

    def __init__(self):
        self.in1 = 0
        self.in2 = 0
        self.control = 0

    def out(self):
        if self.control == 0:

            return self.in1 + self.in2

# Our entire CPU is simulated within the ARM class
class ARM:

    pc = 0

    pc_alu = ALU() 

    alu = ALU()

    data_memory= [0] * 256 

    instruction_memory = {}

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
        self.pipeline = {"IF_ID": {}, "ID_EX": {}, "EX_MEM": {}, "MEM_WB": {} }
        self.stall_for_branch = threading.Thread(target=None)
    
    def instruction_fetch(self):
        try:
            self.instruction_bits = self.instruction_memory[self.pc] # Get the instruction at PC
        except KeyError:
            print("ERROR", flush=True)

        self.pc_alu.in1 = self.pc

        i = int(self.instruction_bits.digits(31,21))
        ib = self.instruction_bits

        # Check the first 11 bits (opcode) of the instruction to determine which instruction we are going to execute
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
        elif 1440 <= i <= 1447:
            self.instruction = CBFormat("CBZ", ib)
        elif 160 <= i <= 191:
            self.instruction = BFormat("B", ib)
        else:
            raise ValueError("Unrecognized opcode: {} 0b{}".format(i, ib))
        
        self.npc = self.pc_alu.out() 
 
        self.pipeline["IF_ID"]["PC"] = self.pc
        self.pipeline["IF_ID"]["IR"] = self.instruction

    def instruction_decode(self):
        
        i = self.pipeline["IF_ID"]["IR"]

        # Set up the dataA and dataB (the read data output of the register file) based on the values within the instruction object
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
            self.dataB = int(i.address.undone_twos())
        elif i.format == "I":
            self.imm = int(i.immediate)
            self.dataA = self.register[int(i.rn)]
 
        self.pipeline["ID_EX"]["DATAA"] = self.dataA
        self.pipeline["ID_EX"]["DATAB"] = self.dataB
        self.pipeline["ID_EX"]["PC"] = self.pipeline["IF_ID"]["PC"]
        self.pipeline["ID_EX"]["IMM"] = self.imm
    
    def execution(self):

        i = self.instruction

        dataA = self.pipeline["ID_EX"]["DATAA"]
        dataB = self.pipeline["ID_EX"]["DATAB"]
        pc = self.pipeline["ID_EX"]["PC"]
        imm = self.pipeline["ID_EX"]["IMM"]

        mux0 = MUX(self.pc, self.dataA)
        mux1 = MUX(self.dataB, self.imm)
        
        if i.format == "R":
            # select Data A and Data B
            mux0.select = 1
            mux1.select = 0
        elif i.format == "I":
            # select Data A and Immediate
            mux0.select = 1
            mux1.select = 1
        elif i.format == "D":
            # select Data A and Immediate
            mux0.select = 1
            mux1.select = 1
        elif i.format == "CB":
            # select NPC and Immediate
            mux0.select = 0
            mux1.select = 1
            self.cond = self.dataA
        elif i.format == "B":
            # select NPC and Immediate
            mux0.select = 0
            mux1.select = 1

        # set ALU
        self.alu.in1 = mux0.out()
        self.alu.in2 = mux1.out()
        if i.format == "D":
            # format for data memory
            self.alu.in1 *= 8
        elif i.format == "B":
            self.alu.in1 = self.pc
            self.alu.in2 = self.dataB * 4
        elif i.format == "CB":
            self.alu.in2 *= 4
        self.alu_out = self.alu.out()
        if i.name == "SUB" or i.name == "SUBI":
            self.alu_out = self.alu.in1 - self.alu.in2

 
        self.pipeline["EX_MEM"]["COND"] = self.cond
        self.pipeline["EX_MEM"]["ALU_OUT"] = self.alu_out
        self.pipeline["EX_MEM"]["DATAB"] = self.dataB

    def memory_access(self):
        i = self.instruction

        cond = self.pipeline["EX_MEM"]["COND"]
        alu_out = self.pipeline["EX_MEM"]["ALU_OUT"]
        dataB = self.pipeline["EX_MEM"]["DATAB"]

        mux = MUX(self.npc, alu_out)
        mux.select = 0

        if i.name == "LDUR":
            # store read data from data memory in lmd
            self.lmd = self.data_memory[alu_out]
        elif i.name == "STUR":
            # write data into data memory
            self.data_memory[alu_out] = self.register[dataB]
        elif i.name == "CBZ":
            if cond == 0:
                # if 0, branch
                mux.select = 1
            else:
                # if not 0, go to next instruction
                mux.select = 0
        elif i.name == "B":
            mux.select = 1
        
        self.pc = mux.out()

        self.pipeline["MEM_WB"]["LMD"] = self.lmd
        self.pipeline["MEM_WB"]["ALU_OUT"] = self.alu_out 

    def write_back(self):

        i = self.instruction

        lmd = self.pipeline["MEM_WB"]["LMD"]
        alu_out = self.pipeline["MEM_WB"]["ALU_OUT"]

        mux = MUX(lmd, alu_out)

        if i.format == "R":
            # write ALU output into the destination register
            mux.select = 1
            self.register[int(i.rd)] = mux.out()
        elif i.format == "I":
            # write ALU output into the destination register
            mux.select = 1
            self.register[int(i.rt)] = mux.out()
        elif i.name == "LDUR":
            # write lmd into the destination register
            mux.select = 0
            self.register[int(i.rt)] = mux.out()

    def cycle(self):
        self.instruction_fetch()
        self.instruction_decode()
        self.execution()
        self.memory_access()
        self.write_back()


    # run_all() will go through each instruction in the instruction memory and execute it until the PC
    # is over the last instruction
    def run_all(self):
        self.pc = 0
        self.register = [0] * 32
        print("Instruction Memory: ")
        for i in self.instruction_memory:
            print(i, self.instruction_memory[i])
        print("Registers (Before): ", self.register)
        print("Data Memory (Before):", self.data_memory)
        while self.pc < len(self.instruction_memory)*4:
            print("PC", self.pc)
            self.cycle()
        print("Registers (After): ", self.register)
        print("Data Memory (After):", self.data_memory)
        print("***********")


    # strip_code() is used when reading the assembly code to get integer values
    # For example, X9 => 9, XZR =>, #1 => 1, etc.
    def strip_code(self, code):
        split_c = code.split("//")[0].split(" ")

        for i in range(len(split_c)):
            c = split_c[i]
            c = c.replace(",","").replace("X" ,"").replace("#", "").replace("ZR", "0").replace("[","").replace("]","").strip()
            split_c[i] = c

        split_c[:] = (value for value in split_c if value != '')
        return split_c

    # assemble() reads a single line of code and converts it into machine language
    def assemble(self, code):
        bin_str = ""
        
        c = self.strip_code(code)
        name = c[0]
        if name == "ADDI" or name == "SUBI":
            
            rd = Binary(int(c[1]), 5)
            rn = Binary(int(c[2]), 5)
            imm = Binary(int(c[3]), 12)

            if name == "ADDI":
                op = Binary(580, 10)
            else:
                op = Binary(836, 10)
        
            for part in [op, imm, rn, rd]:
                bin_str += str(part)

        elif name == "ADD" or name == "SUB":
            rd = Binary(int(c[1]), 5)
            rn = Binary(int(c[2]), 5)
            shamt = Binary(0, 6)
            rm = Binary(int(c[3]), 5)

            if name == "ADD":
                op = Binary(1112, 11)
            else:
                op = Binary(1624, 11)
            
            for part in [op, rm, shamt, rn, rd]:
                bin_str += str(part)

        elif name == "LDUR" or name == "STUR":
            rt = Binary(int(c[1]), 5)
            rn = Binary(int(c[2]), 5)
            op2 = "00"
            address = Binary(int(c[3]), 9)

            if name == "LDUR":
                op = Binary(1986, 11)
            else:
                op = Binary(1984, 11)
        
            for part in [op, address, op2, rn, rt]:
                bin_str += str(part)

        elif name == "CBZ":
            op = "10110100"
            rt = Binary(int(c[1]), 5)
            address = Binary(int(c[2]), 19)
            bin_str = op + str(address) + str(rt)
        elif name == "B":
            op = "000101"
            
            address = Binary(int(c[1]), 26)
            bin_str = op + str(address)

        return Binary(int(bin_str,2), 32)

    def load_instructions(self, inst_list):
        location = 0

        self.instruction_memory = {}
        
        for inst in inst_list.split("\n"):
            self.instruction_memory[location] = self.assemble(inst)
            location += 4


    def run_pipelined(self):
        print("***************************************")
        self.pc = 0
        self.register = [0] * 32
        self.clock_cycles = 0
    
        while self.pc < len(self.instruction_memory)*4:
            print("PC", self.pc, flush=True)
            t = threading.Thread(target=self.pipeline_cycles)
            t.start()


    def pipeline_cycles(self):
        print(threading.active_count())
        new_fetch = threading.Thread(target=self.instruction_fetch)
        
        # Stall for a cycle if...
        #   i. A previous fetch is still ocurring
        #   ii. A branch instruciton is executing and we need to wait for it to finish

        #while self.branching:
        #    print("==============STALL===========", flush=True)
        #    self.clock_cycles += 1

        self.instruction_fetch()

        f = self.pipeline["IF_ID"]["IR"].format


        if  f == "B" or f == "CB":
            self.stall_for_branch = threading.current_thread()

        self.instruction_decode()

        self.execution()

        self.memory_access()

        self.write_back()

cpu = ARM()

ex_1 = """ADDI X21, XZR, #19
ADDI X22, XZR, #54
ADDI X23, XZR, #80
ADDI X24, XZR, #13
ADD  X9,  X23, X24
SUB  X10, X22, X21
ADD  X11, X9,  X10"""

cpu.load_instructions(ex_1)
print("Example 1")
cpu.run_pipelined()


ex_2 = """ADD  X21, XZR, XZR	//X21 = 0 or the beginning of data memory
LDUR X9,  [X21, #0]	//X9 = 10
LDUR X10, [X21, #1]	//X10 = 13
ADD  X11, X9,  X10
STUR X11, [X21, #2]"""

cpu.load_instructions(ex_2)

cpu.data_memory[168] = 10
cpu.data_memory[169] = 13

print("Example 2")
cpu.run_pipelined()

ex_3 = """ADDI X21, XZR, #0	//X21 = 0 (i = 0 for loop)
ADDI X22, XZR, #100	//X22 = 100
ADDI X23, XZR, #10	//X23 = 10
SUBI X9,  X21, #4	//compare i with 4
CBZ  X9, 4		//if i is 4 exit for loop
SUB  X22, X22, X23	
ADDI X21, X21, #1	//i++
B    -4			//loop back up to compare again"""

cpu.load_instructions(ex_3)

print("Example 3")
cpu.run_pipelined()
