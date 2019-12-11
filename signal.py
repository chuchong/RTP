from PyQt5.QtGui import *
from PyQt5.QtCore import *
class RtpSignals(QThread):
    AnimeSignal = pyqtSignal()
    ReAnimeSignal = pyqtSignal()
    LoadSignal = pyqtSignal()
    LoadDoneSignal = pyqtSignal()

    def __init__(self, fullScrennWindow):
        super(RtpSignals, self).__init__()
        self.full = fullScrennWindow
    def run(self):
        self.full.loop()
