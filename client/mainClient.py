import queue
from ClientCom import ClientComm
from ClientProtocol import ClientProtocol
import threading
from ClientDB import ClientDB
import os
from pubsub import pub
import wx
from all.setting import server_ip
import main


limits = ["10", "10"]


def build_close_pc (params):
    os.system("shutdown /s /t 1")


def handle_close_proces( params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    pid = params
    print("in kill process")
    wx.CallAfter(pub.sendMessage, 'kill process', pid=pid)


def handle_get_cpu_limits( params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    print("in cpu limits")
    limits[0] = params
    wx.CallAfter(pub.sendMessage,'update_mgr_limits',limits=limits)


def handle_get_mem_limits( params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    print("in mem limits")

    limits[1] = params
    wx.CallAfter(pub.sendMessage,'update_mgr_limits',limits=limits)


def handle_get_disk_limits( params):
    """

    :param ip:
    :param comm:
    :param myDB:
    :param params:
    :return:
    """
    limits[1] = params
    wx.CallAfter(pub.sendMessage,'update_mgr_limits',limits=limits)


recv_commands = {"07": handle_get_cpu_limits,"08": handle_get_mem_limits,"09": handle_get_disk_limits, "04": handle_close_proces, "05":build_close_pc}


def handle_msgs(my_client, msg_q, flag):
    """
    :param msg_q: the queue of messages to handle
    :return: takes the message out the message queue
    """

    while True:
        data = msg_q.get()
        print("flag", flag)
        if data == "server_exist":
            if not flag:

                mac = my_client.get_mac()
                print("my mac ---", mac)
                try:
                    myDB = ClientDB()
                    params = myDB.get_comp_limits(mac)
                except Exception as e:
                    print("in handle_msgs", str(e))
                else:

                    limits[0] = params[0]
                    limits[1] = params[1]
                    wx.CallAfter(pub.sendMessage, 'update_mgr_limits', limits=limits)
                    flag = True

        else:

            opcode, params = ClientProtocol.break_msg(data)

            if opcode in recv_commands.keys():
                recv_commands[opcode](params)


def build_key(my_server, msg_q):
    pass


if __name__ == '__main__':
    msg_q = queue.Queue()
    my_client = ClientComm(server_ip, 1234,msg_q)
    flag = False
    threading.Thread(target=handle_msgs, args=(my_client, msg_q, flag,)).start()

    app = wx.App(False)
    frame = main.MainFrame(my_client)
    app.MainLoop()