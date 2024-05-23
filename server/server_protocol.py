class server_protocol:

    def build_set_cpu(cpu_limits):
        # Constructs a message to set the memory_limits according to the protocol
        return f"07{cpu_limits}"

    def build_set_memory(memory_limits):
        # Constructs a message to set the memory_limits according to the protocol
        return f"08{memory_limits}"


    def build_close_proc(pid):
        # Constructs a message to close a process by its PID according to the protocol
        return f"04{pid}"

    def build_close_pc():
        # Constructs a message to shut down the client computer according to the protocol
        return "05"

    def build_key(key):
        # Constructs a message for sending an encryption key according to the protocol
        return f"00{key}"

    def break_msg(msg):
        # Breaks down a message according to the protocol and returns a tuple (opcode, [parameters])
        opcode = msg[:2]
        parameters = msg[2:]
        return opcode, parameters


