class Process(object):
    """
    Process class for storing information about a single process.
    """

    def __init__(self, name, pid, user, cwd, cpu, mem, io, threads):
        """
        Constructor: Initializes process information.

        :param name: The name of the process.
        :param pid: The process ID.
        :param user: The user who owns the process.
        :param cwd: The current working directory of the process.
        :param cpu: The CPU usage of the process.
        :param mem: The memory usage of the process.
        :param io: The I/O usage of the process.
        :param threads: The number of threads in the process.
        """
        self.name = name
        self.pid = pid
        self.user = user
        self.cwd = cwd
        self.cpu = cpu
        self.mem = mem
        self.io = io
        self.threads = threads