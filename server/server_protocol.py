class server_protocol:

    def build_set_cpu(cpu_limits):
        return f"07{cpu_limits}"

    def build_set_memory(memory_limits):
        return f"08{memory_limits}"


    def build_close_proc(pid):
        # Constructs a message to close a process by its PID
        return f"04{pid}"

    def build_close_pc():
        # Constructs a message to shut down the client computer
        return "05"

    def build_key(key):
        # Constructs a message for sending an encryption key
        return f"00{key}"

    def break_msg(msg):
        # Breaks down a message according to the protocol and returns a tuple (opcode, [parameters])
        opcode = msg[:2]
        parameters = msg[2:]
        return opcode, parameters


