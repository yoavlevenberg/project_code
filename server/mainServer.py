import queue
from ServerCom import ServerCom
from server_protocol import server_protocol
import threading
from DB import DB
from all.process import Process
import wx
import login
from pubsub import pub


computers = {}  #computers[ip] = [mac,graphic]


def handle_get_mac(ip, comm, myDB, params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    mac = params
    print("mac=============",mac)
    if not myDB.is_mac_exist(mac):
        comm.disconnect_client(ip)
    else:
        # add to graphic
        computers[ip] = [mac, None]
        print(mac)

        wx.CallAfter(pub.sendMessage,"new computer", computer_name=mac ,computer_ip = ip)


def handle_delete_computer(ip):
    """

    :param ip:
    :return:
    """
    if ip in computers.keys():
        mac = computers[ip][0]
        wx.CallAfter(pub.sendMessage, "delete computer", computer_name=mac)


def handle_get_process_details(ip, comm, myDB, params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    good_process = []
    bad_process = []

    if ip in computers.keys():
        cpu_limit, memory_limit = myDB.get_comp_limits(computers[ip][0])

        data, total_cpu,total_mem = params.split("@")
        procs = data.split("#")

        for proc in procs:
            name, pid, user, cwd, cpu, mem, io, threads = proc.split(',')

            newProc = Process(name, pid, user, cwd, cpu, mem, io, threads)
            if float(cpu) > float(cpu_limit) or float(mem) > float(memory_limit):
                bad_process.append(newProc)
            else:
                good_process.append(newProc)

        # call to graphic

        wx.CallAfter(pub.sendMessage, f"update-{computers[ip][0]}", good_procs=good_process,
                     bad_procs=bad_process, total_cpu=total_cpu, total_mem=total_mem)

        status = len(bad_process) > 0
        wx.CallAfter(pub.sendMessage, "bad comp", computer_name=computers[ip][0], status=status)


recv_commands = { "01":handle_get_mac, "03": handle_get_process_details}


def handle_msgs(my_server, msg_q):
    """
    :param  my_server com object
    :param msg_q: the queue of messages to handle
    :return: takes the message out the message queue
    """
    myDB = DB()
    while True:
        ip, data = msg_q.get()
        print("in main server:", ip)
        if data.startswith("disconnect"):
            handle_delete_computer(ip)
        else:
            opcode, params = server_protocol.break_msg(data)

            if opcode in recv_commands.keys():
                recv_commands[opcode](ip, my_server, myDB, params)


def build_key(my_server, msg_q):
    pass


if __name__ == '__main__':
    msg_q = queue.Queue()
    my_server = ServerCom(msg_q)
    threading.Thread(target=handle_msgs, args=(my_server, msg_q,)).start()

    app = wx.App()
    frame = login.MyFrame(my_server)
    frame.Show()
    app.MainLoop()


