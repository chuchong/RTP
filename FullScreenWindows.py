from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
import threading
from fullScreen import Ui_Form


def qt_exception_wrapper(func):
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)
    return wrapper

class FullScreenWindow(QWidget, Ui_Form):
    ANIMATION_DURATION = 3000
    IDLE_TIME = 5349
    AWAKE_INTERVAL = 500

    # 状态
    BUSY = 0
    IDLE = 1
    ANIMATION = 3
    NOTIN = 2
    def __init__(self,parent = None):
        super(FullScreenWindow, self).__init__(parent, Qt.Window)
        self.setupUi(self)

        self.slider.setMaximum(255)
        self.onAnim = False
        self.animLock = threading.Lock()
        self.movingMouse = False
        self.setMouseTracking(True)
        self.state = self.NOTIN

    def resizeToFill(self):
        """重新调整大小"""
        self.setWindowFlags( Qt.FramelessWindowHint
                                      or Qt.WindowStaysOnTopHint
                                      or Qt.CustomizeWindowHint)
        self.showFullScreen()
        self.label.setScaledContents(True)
        self.label.resize(self.width(), self.height() - 80)
        self.slider.resize(self.width(), self.height() // 2)
        self.widget.move(0, self.height() - 80)
        self.state = self.BUSY
        self.movingMouse = True
        self.loop()

    def exitToPar(self):
        self.hide()
        self.movingMouse = False
        self.state = self.NOTIN
        self.loop()

    @qt_exception_wrapper
    def widgetShow(self):
        self.label.resize(self.width(), self.height() - 80)
        self.widget.move(0, self.height() - 80)
        self.play.setEnabled(True)
        self.pause.setEnabled(True)
        self.slider.setEnabled(True)
        self.exit.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.widget.setMaximumHeight(80)
        self.widget.resize(self.widget.width(), 80)

    @qt_exception_wrapper
    def loop(self):
        if self.state == self.NOTIN:
            # 还未进来
            # pass
            # QTimer.singleShot(self.AWAKE_INTERVAL, self.loop)
            return
        elif self.state == self.BUSY:
            if self.movingMouse:
                self.movingMouse = False
                QTimer.singleShot(self.IDLE_TIME, self.loop)
            else:
                self.state = self.ANIMATION
                self.loop()
        elif self.state == self.IDLE:
            if self.movingMouse:
                self.state = self.BUSY
                self.widgetShow()
                self.loop()
            else:
                QTimer.singleShot(self.AWAKE_INTERVAL, self.loop)

        elif self.state == self.ANIMATION:
            #此时进入,播放动画
            self.animLock.acquire()
            self.play.setEnabled(False)
            self.pause.setEnabled(False)
            self.slider.setEnabled(False)
            self.exit.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.anim = None
            self.anim = QPropertyAnimation(self.widget, b"maximumHeight", self)
            self.anim.setDuration(self.ANIMATION_DURATION)
            self.anim.setStartValue(80)
            self.anim.setEndValue(0)
            self.anim.finished.connect(self.switchOnAnim)
            self.anim.start()
        else:
            raise Exception('Error: what state')
    @qt_exception_wrapper
    def switchOnAnim(self):
        self.label.resize(self.width(), self.height())
        self.widget.move(0, self.height())
        self.state = self.IDLE
        self.loop()
        self.movingMouse = False
        self.animLock.release()


    def mouseMoveEvent(self, a0: QMouseEvent):
        self.movingMouse = True

    def mousePressEvent(self, a0: QMouseEvent):
        self.movingMouse = True

    def mouseReleaseEvent(self, a0: QMouseEvent):
        self.movingMouse = True

