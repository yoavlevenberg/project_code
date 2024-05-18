import pyodbc

class DB:
    def __init__(self):
       self.conn = None
       self.curr = None
       self.computersTbl = "computers1"
       self.adminsTbl = "admins"
       self.infoTbl = "info"

       self._create_db()

    def _create_db(self):
        '''

        :param self:
        :return:
        '''
    #192.117.49.135
        self.conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=192.117.49.135;'  #192.117.49.135 192.168.4.4
                              'port=1433;'
                              'Database=taskmanager;'
                              'UID=yoav;'
                              'PWD=zxcvb;')
        self.curr = self.conn.cursor()
        sql1 = f'CREATE TABLE {self.computersTbl} (mac varchar(17), description varchar(20), cpu int, memory int);'
        sql2 = f'CREATE TABLE {self.adminsTbl} (username varchar(10), password varchar(30));'
        try:
            self.curr.execute(sql1)
            self.curr.execute(sql2)
        except Exception as e:
            pass
            #print(str(e))

        self.conn.commit()



    def get_comp_limits(self, mac):
        """

        :param mac:
        :return:
        """

        if self.is_mac_exist(mac):
            sql = f"SELECT cpu,memory FROM {self.computersTbl} WHERE mac = ?"
            self.curr.execute(sql, (mac,))
            return self.curr.fetchone()
        return None

    def is_mac_exist(self, mac):
        '''

        :param self:
        :param mac:
        :return:
        '''
        sql = f"SELECT * FROM {self.computersTbl} WHERE mac = ?"
        self.curr.execute(sql, (mac,))
        return self.curr.fetchone()

    def _is_username_exist(self, username):
        '''

        :param self:
        :param username:
        :return:
        '''
        sql = f"SELECT * FROM {self.adminsTbl} WHERE username = ?"
        self.curr.execute(sql, (username,))
        return self.curr.fetchone()

    def _is_name_exist(self, name):
        '''

        :param self:
        :param name:
        :return:
        '''
        sql = f"SELECT * FROM {self.infoTbl} WHERE name = ?"
        self.curr.execute(sql, (name,))
        return self.curr.fetchone()

    def add_mac(self, mac, desc ,cpu , memory):
        '''

        :param self:
        :param mac:
        :return:
        '''
        status = False
        if not self.is_mac_exist(mac):
            sql = f"INSERT INTO {self.computersTbl}  VALUES (?,?,?,?);"
            self.curr.execute(sql, (mac, desc,cpu, memory,  ))
            self.conn.commit()
            print("mac")

            status = True

        return status

    def del_mac(self, mac):
        '''

        :param self:
        :param mac:
        :return:
        '''
        status = False
        if self.is_mac_exist(mac):
            sql = f"DELETE FROM {self.computersTbl}  WHERE mac = ?;"
            self.curr.execute(sql, (mac,))
            self.conn.commit()
            print("del mac",mac)

            status = True

        return status

    def add_username(self, username, password):
        '''

        :param self:
        :param mac:
        :return:
        '''
        status = False
        if not self._is_username_exist(username):
            sql = f"INSERT INTO {self.adminsTbl}  VALUES (?,?);"
            self.curr.execute(sql, (username, password, ))
            self.conn.commit()
            status = True
            print("username")

        return status


    def add_name(self, name, info):
        '''

        :param self:
        :param mac:
        :return:
        '''
        status = False
        if not self._is_name_exist(name):
            sql = f"INSERT INTO {self.infoTbl}  VALUES (?,?);"
            self.curr.execute(sql, (name, info, ))
            self.conn.commit()
            status = True
            print("name")

        return status

    def get_info(self, name ):
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

    def getMng_pass(self,username):
        '''

        :param self:
        :param username:
        :return:
        '''
        password = None
        if self._is_username_exist(username):
            print("hi")
            sql = f"SELECT password FROM {self.adminsTbl} WHERE username = ?"
            self.curr.execute(sql, (username,))
            password = self.curr.fetchone()[0]

        return password

    def edit_cpu_limits(self, mac, cpu):
        '''

        :param self:
        :param mac,limits :
        :return:
        '''
        if self.is_mac_exist(mac):
            print("hloo")
            sql = f"UPDATE {self.computersTbl} SET cpu = (?) WHERE mac = ?"
            self.curr.execute(sql, (cpu, mac, ))
            self.conn.commit()

    def edit_mem_limits(self, mac, mem):
        '''

        :param self:
        :param mac,limits :
        :return:
        '''
        if self.is_mac_exist(mac):
            print("hloo")
            sql = f"UPDATE {self.computersTbl} SET memory = (?) WHERE mac = ?"
            self.curr.execute(sql, (mem, mac, ))
            self.conn.commit()



    def get_computers_details(self):
        sql = f"SELECT * FROM {self.computersTbl} "
        self.curr.execute(sql)
        computers = self.curr.fetchall()

        return computers





if __name__ == '__main__':
    myDB = DB()




    # print(myDB.add_mac("78:24:AF:1A:10:31", "home2",5,5))
    # print(myDB.add_mac("64-00-6A-42-4C-46", "cyber 211 comp 20", 5, 5))
    # print(myDB.add_mac("64:00:6a:41:d9:23", "cyber 211 comp 5", 5, 5))
    # print(myDB.get_comp_limits("78:24:af:1a:10:31"))
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
    #
    #
    #
    #
    #
    # print(myDB.is_mac_exist("78:24:AF:1A:10:31"))
    # cpu, memory = myDB.get_comp_limits("78:24:AF:1A:10:31")
    # print(cpu, memory)
    # myDB.edit_cpu_limits("78:24:AF:1A:10:31",10)
    # myDB.edit_mem_limits("78:24:AF:1A:10:31", 8)

    print(myDB.get_computers_details())

    print(myDB.add_mac("78:24:af:1a:10:31","home",5,4))
    print(myDB.get_computers_details())

    # print(myDB.del_mac("1:1:1:1:1"))
    # print(myDB.get_comp_limits("1:1:1:1:1"))



