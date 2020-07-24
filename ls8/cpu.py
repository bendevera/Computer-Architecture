import sys


class CPU:

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.flags = [0] * 8
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.instructions = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000001: self.hlt,
            0b10100000: self.add,
            0b10100001: self.sub,
            0b10100010: self.mul,
            0b10100011: self.div,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b10100111: self.compare,
            0b01010101: self.jeq,
            0b01010110: self.jne,
            0b01010100: self.jmp,
            0b10101000: self.and_op,
            0b10101010: self.or_op,
            0b01101001: self.not_op,
            0b10101011: self.xor,
            0b10101100: self.shl,
            0b10101101: self.shr,
            0b10100100: self.mod
        }

    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, pc, value):
        self.ram[pc] = value

    def load(self):
        """Load a program into memory."""
        # check input
        if len(sys.argv) < 2:
            raise NameError("No input program specified, exiting...")

        program_name = sys.argv[1]
        address = 0

        with open(program_name) as p:
            for line in p:
                line = line.split("#")[0]

                try:
                    instruction = int(line, 2)
                except ValueError:
                    continue

                self.ram[address] = instruction
                address += 1

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "AND":
            result = self.reg[reg_a] & self.reg[reg_b]
            self.reg[reg_a] = result
        elif op == "OR":
            result = self.reg[reg_a] | self.reg[reg_b]
            self.reg[reg_a] = result
        elif op == "XOR":
            result = self.reg[reg_a] ^ self.reg[reg_b]
            self.reg[reg_a] = result
        elif op == "SHL":
            result = self.reg[reg_a] << self.reg[reg_b]
            self.reg[reg_a] = result
        elif op == "SHR":
            result = self.reg[reg_a] >> self.reg[reg_b]
            self.reg[reg_a] = result
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags[-1] = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags[-3] = 1
            else:
                self.flags[-2] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running == True:
            ir = self.ram[self.pc]
            instruction = self.instructions.get(ir)
            sets_pc = (ir >> 4) & 0b1

            if instruction and not sets_pc:
                inc = (ir >> 6) + 1
                self.instructions[ir]()
                self.pc += inc
            elif instruction:
                self.instructions[ir]()

    def ldi(self):
        address = self.ram[self.pc+1]
        value = self.ram[self.pc+2]
        self.reg[address] = value

    def prn(self):
        address = self.ram[self.pc+1]
        value = self.reg[address]
        print(value)

    def hlt(self):
        sys.exit(0)

    def add(self):
        addresses = self.get_operands()
        self.alu("ADD", *addresses)

    def sub(self):
        addresses = self.get_operands()
        self.alu("SUB", *addresses)

    def mul(self):
        addresses = self.get_operands()
        self.alu("MUL", *addresses)

    def div(self):
        addresses = self.get_operands()
        self.alu("DIV", *addresses)

    def compare(self):
        addresses = self.get_operands()
        self.alu("CMP", *addresses)

    def get_operands(self):
        address_1 = self.ram[self.pc+1]
        address_2 = self.ram[self.pc+2]

        return [address_1, address_2]

    def push(self):
        self.sp -= 1

        address = self.ram[self.pc+1]
        value = self.reg[address]
        self.ram[self.sp] = value

    def pop(self):
        address = self.ram[self.pc+1]
        value = self.ram[self.sp]
        self.reg[address] = value

        self.sp += 1

    def call(self):
        # memory address we want to return to after subroutine
        return_addr = self.pc + 2

        # push onto stack
        self.sp -= 1
        self.ram[self.reg[self.sp]] = return_addr

        # get the address to be called
        reg_num = self.ram[self.pc+1]
        subroutine_addr = self.reg[reg_num]

        # call the subroutine
        self.pc = subroutine_addr

    def ret(self):
        self.pc = self.ram[self.reg[self.sp]]
        self.sp += 1

    def jeq(self):
        if self.flags[-1] == 1:
            address = self.ram[self.pc+1]
            jump_to = self.reg[address]
            self.pc = jump_to
        else:
            self.pc += 2

    def jne(self):
        if self.flags[-1] == 0:
            address = self.ram[self.pc+1]
            jump_to = self.reg[address]
            self.pc = jump_to
        else:
            self.pc += 2

    def jmp(self):
        address = self.ram[self.pc+1]
        jump_to = self.reg[address]
        self.pc = jump_to

    def and_op(self):
        addresses = self.get_operands()
        self.alu("AND", *addresses)

    def or_op(self):
        addresses = self.get_operands()
        self.alu("OR", *addresses)

    def not_op(self):
        operand_addr = self.ram[self.pc+1]
        self.alu("NOT", operand_addr)

    def xor(self):
        addresses = self.get_operands()
        self.alu("XOR", *addresses)

    def shl(self):
        addresses = self.get_operands()
        self.alu("SHL", *addresses)

    def shr(self):
        addresses = self.get_operands()
        self.alu("SHR", *addresses)

    def mod(self):
        addresses = self.get_operands()
        self.alu("MOD", *addresses)