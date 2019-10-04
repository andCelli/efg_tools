from abc import ABC, abstractmethod


class AbstractReader(ABC):
    SECTION_INFO = 0
    SECTION_GAME = 1
    SECTION_TREEPLEXES = 2
    SECTION_UTILITY = 3

    CARDINAL_TO_PID = {
        'N': 0,
        'E': 1,
        'S': 2,
        'W': 3
    }

    def __init__(self, file_path, auto_read=True):
        """
        constructor
        :param file_path: path str of the file to read
        :param auto_read: if true reads the file on instantiation
        """
        self._file_path = file_path

        self._info_section = []
        self._game_section = []
        self._tree_section = []
        self._util_section = []

        super().__init__()

        if auto_read:
            self.read()

    def read(self):
        """
        Read file
        """
        f = open(self._file_path, 'r')
        lines = f.readlines()
        f.close()

        # delete empty lines and remove all special chars, like \n and \r
        lines = [line.rstrip() for line in lines if line.rstrip() != ""]

        section_indexes = []
        for n, l in enumerate(lines):
            if l.find("###") != -1:
                section_indexes.append(n)

        self._info_section = lines[1:section_indexes[AbstractReader.SECTION_GAME]]
        self._game_section = lines[section_indexes[AbstractReader.SECTION_GAME] + 1:
                                   section_indexes[AbstractReader.SECTION_TREEPLEXES]]
        self._tree_section = lines[section_indexes[AbstractReader.SECTION_TREEPLEXES] + 1:
                                   section_indexes[AbstractReader.SECTION_UTILITY]]
        self._util_section = lines[section_indexes[AbstractReader.SECTION_UTILITY] + 1:]

    @abstractmethod
    def process_data(self):
        """
        Override this method to process sections and return a game object
        """
        pass
