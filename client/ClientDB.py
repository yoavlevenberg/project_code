import pyodbc


class ClientDB:
    def __init__(self):
        self.conn = None
        self.curr = None
        self.infoTbl = "info"
        self.computersTbl = "computers"

        self._create_db()

    def _create_db(self):
        '''

        :param self:
        :return:
        '''

        self.conn = pyodbc.connect('Driver={SQL Server};'
                                   'Server=192.168.4.4;'
                                   'port=1433;'
                                   'Database=taskmanager;'
                                   'UID=yoav;'
                                   'PWD=zxcvb;'
                                   , readonly=True
                                   , timeout=1)
        self.curr = self.conn.cursor()

    def _is_name_exist(self, name):
        '''

        :param self:
        :param name:
        :return:
        '''
        sql = f"SELECT * FROM {self.infoTbl} WHERE name = ?"
        self.curr.execute(sql, (name,))
        return self.curr.fetchone()

    def get_info(self, name):
        '''

        :param self:
        :param mac:
        :return:
        '''
        info = None
        if self._is_name_exist(name):
            sql = f"SELECT info FROM {self.infoTbl} WHERE name = ?"
            self.curr.execute(sql, (name,))
            info = self.curr.fetchone()[0]

        return info

    def is_mac_exist(self, mac):
        '''

        :param self:
        :param mac:
        :return:
        '''
        sql = f"SELECT * FROM {self.computersTbl} WHERE mac = ?"
        self.curr.execute(sql, (mac,))
        return self.curr.fetchone()

    def get_comp_limits(self, mac):
        """

        :param mac:
        :return:
        """
        if self.is_mac_exist(mac):
            sql = f"SELECT cpu,memory,disk FROM {self.computersTbl} WHERE mac = ?"
            self.curr.execute(sql, (mac,))
            return self.curr.fetchone()


if __name__ == '__main__':
    myDB = ClientDB()
    print(myDB.get_comp_limits("78:24:af:1a:10:31"))
    print(myDB.get_info('1242'))
    # print(myDB.add_mac("11:22:33:44:55:66", "cyber 211 comp 7",5,5,5))
    # print(myDB.add_username("yoav123", "54321"))
    # print(myDB.add_username("yoav123", "54321"))
    # print(myDB.add_username("teff", "tr4ew"))
    # print(myDB.add_username("lior", "sirno"))
    # print(myDB.add_username("hi", "irno"))
    # print(myDB.add_username("hi", "irno"))
    # print(myDB.add_name("1242", "hdifhdkjgfujiovzj fdgivjzkxvjhb"))
    # print(myDB.get_info("1242"))
    # print(myDB.getMng_pass("lior"))
    # print(myDB.edit_cpu_limits("11:22:33:44:55:66", 7))
