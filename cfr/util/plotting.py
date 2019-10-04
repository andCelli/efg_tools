import matplotlib.pyplot as plt


class Plotter:
    _instance = None

    def __init__(self):
        self.data_x = []
        self.data_y = []

        self.label_x = "x"
        self.label_y = "y"
        self.title = "title"
        self.file_name = "plot.png"

    @staticmethod
    def get_instance():
        if Plotter._instance is None:
            Plotter._instance = Plotter()

        return Plotter._instance

    def plot(self, save=False):
        figure, axis = plt.subplots()
        axis.plot(self.data_x, self.data_y)

        axis.set(xlabel=self.label_x, ylabel=self.label_y, title=self.title)
        axis.grid()

        if save:
            figure.savefig(self.file_name)
        plt.show()


class EpsDifferencesPlotter(Plotter):
    def __init__(self):
        super().__init__()

        self.title = "Eps nash differences"
        self.label_x = "iteration"
        self.label_y = "difference"
        self.file_name = "eps_diff.png"

    @staticmethod
    def get_instance():
        if EpsDifferencesPlotter._instance is None:
            EpsDifferencesPlotter._instance = EpsDifferencesPlotter()

        return EpsDifferencesPlotter._instance


class AverageRegretPlotter(Plotter):
    def __init__(self):
        super().__init__()

        self.title = "Average regret of declarer"
        self.label_x = "iteration"
        self.label_y = "regret"
        self.file_name = "regret.png"

    @staticmethod
    def get_instance():
        if AverageRegretPlotter._instance is None:
            AverageRegretPlotter._instance = AverageRegretPlotter()

        return AverageRegretPlotter._instance
