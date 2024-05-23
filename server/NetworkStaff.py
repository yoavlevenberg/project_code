import os


def separate_line(line):
    """
    separate ip and mac from the text in line:
    """

    blank = line.index(' ')
    ip = line[:blank]
    line = line[blank+1:]
    line = line.strip()
    blank = line.index(' ')
    mac = line[:blank]
    return ip, mac


def get_all_exist_mac():
    """

    :return a dictionary of all the macs and ip in the network:
    """
    # operate the arp -a command into an output file arp.txt
    os.system("arp -a > arp.txt")

    # open the file and separate the lines
    with open("arp.txt") as file:
        data = file.read()

    data = data.split('\n')

    mac_and_ip = {}
    for line in data:
        # only the dynamic matters to us the static are special like the gateway
        if 'dynamic' in line:
            line = line.strip()
            ip, mac = separate_line(line)
            mac = mac.replace("-", ":")
            mac_and_ip[mac] = ip

    # build a dictionary mac:ip
    return mac_and_ip


def check_mac_in_network(mac):
    """

    :param mac:
    :return check if the mac in the network :
    """
    mac_dic = get_all_exist_mac()
    print(mac)
    print(mac_dic.keys())
    return mac.lower() in mac_dic.keys()


if __name__ == '__main__':
    print(get_all_exist_mac())
