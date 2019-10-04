class Logger:
    """
    Logging functions
    """
    def __init__(self, filename: str):
        self.file = open(filename+".txt", "w")

    def log_line(self, obj):
        self.file.write(str(obj)+"\n")

    def log_str(self, obj):
        self.file.write(str(obj))

    def close_logger(self):
        self.file.close()
