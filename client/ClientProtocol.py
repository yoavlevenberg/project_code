class ClientProtocol:

    def build_key(key):
        # Constructs a message for sending an encryption key
        return f"00{key}"

    def build_mac(mac):
        # Constructs a message for sending mac address
        return f"01{mac}"


    def build_close_pc():
        # Constructs a message for closing the client computer
        return "05"

    def break_msg(msg):
        # Breaks down a message according to the protocol
        # Returns a tuple containing the operation code and a list of parameters
        opcode = msg[:2]
        parameters = msg[2:]
        return (opcode, parameters)

    def build_process_details(sendMsg, total_mem, total_cpu):
        msg = "#".join(sendMsg)
        msg = f"03{msg}@{total_cpu}@{total_mem}"
        return msg

