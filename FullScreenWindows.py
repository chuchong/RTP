# 我被你qt坑惨了
# timer应该不是异步的
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
import threading
from fullScreen import Ui_Form
import time
from signal import *
from Timer import Timer


def qt_exception_wrapper(func):
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            QMessageBox.information(self, 'Error', 'Meet with Error: ' + str(e),
                QMessageBox.Yes, QMessageBox.Yes)
    return wrapper

class FullScreenWindow(QWidget, Ui_Form):
    ANIMATION_DURATION = 1000
    IDLE_TIME = 4000
    AWAKE_INTERVAL = 500
    DEFAULT_INTERVAL = 200

    # 状态
    BUSY = 0
    IDLE = 1
    ANIMATION = 3
    NOTIN = 2
    REANIME = 4

    def __init__(self, parent=None, fa=None):
        super(FullScreenWindow, self).__init__(parent, Qt.Window)
        self.setupUi(self)


        self.slider.setMaximum(255)
        self.onAnim = False
        self.movingMouse = False
        self.setMouseTracking(True)
        self.mouseLock = threading.Lock()
        self.state = self.IDLE
        self.stateLock = threading.Lock()
        self.loopLock = threading.Lock()
        self.timer = Timer()
        self.fa = fa
        self.slider.setSingleStep(0)
        self.slider.setPageStep(0)


    def anime(self):
        print("BEGIN ANIME-------------------")
        # self.play.setEnabled(False)
        # self.pause.setEnabled(False)
        # self.slider.setEnabled(False)
        # self.exit.setEnabled(False)
        # self.comboBox.setEnabled(False)
        # self.label.resize(self.width()-2, self.height() - 1)
        self.widget.hide()
        # self.label.move(0,0)
        # self.label.resize(self.width()-2, self.height()-2)  # 是这里的bug,遮盖关系会导致闪退

        print("End ANIME-------------------")

    def reAnime(self):
        print("BEGIN REANIME-----------------------")
        # self.widget.setMaximumHeight(80)
        # self.widget.resize(self.widget.width(), 80)
        # self.widget.move(0, self.height() - 81)
        # self.label.resize(self.width()-2, self.height() - 81)
        self.widget.show()
        # self.label.resize(self.width()-2, self.height() - 82)
        #
        # self.play.setEnabled(True)
        # self.pause.setEnabled(True)
        # self.slider.setEnabled(True)
        # self.exit.setEnabled(True)
        # self.comboBox.setEnabled(True)
        print("End REANIME-------------------")

    def getState(self):
        self.stateLock.acquire()
        state = self.state
        self.stateLock.release()
        return state

    def setState(self, state):
        self.stateLock.acquire()
        self.state = state
        self.stateLock.release()

    def getMouse(self):
        self.mouseLock.acquire()
        bl = self.movingMouse
        self.mouseLock.release()
        return bl

    def setMouse(self, bl):
        self.mouseLock.acquire()
        self.movingMouse = bl
        self.mouseLock.release()

    def resizeToFill(self):
        """重新调整大小"""
        self.setWindowFlags( Qt.FramelessWindowHint
                                or Qt.WindowStaysOnTopHint
                                      or Qt.CustomizeWindowHint)

        self.showFullScreen()
        self.label.setScaledContents(True)
        self.label.move(1,1)
        self.label.resize(self.width()-2, self.height() - 2)
        # self.slider.resize(self.width()-2, 20)
        self.widget.move(1, self.height() - 81)
        self.widget.resize(self.width()-2, 80)
        self.loopLock.acquire()
        self.setState(self.BUSY)
        self.loopLock.release()
        self.movingMouse = True
        print('--------------------------------------START LOOP')
        # self.timer.singleShot(self.loop, 0)
        self.show()

    def exitToPar(self):
        self.hide()
        self.movingMouse = False
        self.setState(self.NOTIN)
        print('--------------------------------------END LOOP')
        self.loopLock.acquire()
        self.loopLock.release()

    @qt_exception_wrapper
    def loop(self):
        self.loopLock.acquire()
        while True:
            self.stateLock.acquire()
            state = self.state
            mouseMoving = self.getMouse()
            print('LOOP')
            if state == self.NOTIN:
                print('NOTIN')
                self.stateLock.release()
                break
            elif state == self.BUSY:
                if mouseMoving:
                    print('BUSY1')
                    self.setMouse(False)
                    self.stateLock.release()
                    QThread.msleep(self.IDLE_TIME)
                    # time.sleep(self.IDLE_TIME)
                else:
                    #最终animate中释放lock
                    print('BUSY2-ANIMATE')
                    self.state = self.ANIMATION
                    self.stateLock.release()
                    QThread.msleep(self.DEFAULT_INTERVAL)
                    # time.sleep(self.DEFAULT_INTERVAL)
            elif state == self.IDLE:
                if mouseMoving:
                    print('IDLE-BUSY')
                    self.state = self.REANIME
                else:
                    print('IDLE-INTERVAL')
                print('IDLE1')
                self.stateLock.release()
                print('IDLE2')
                QThread.msleep(self.DEFAULT_INTERVAL)
                # time.sleep(self.DEFAULT_INTERVAL)
                print('IDLE3')
            elif state == self.ANIMATION:
                print('ANIMATE START')
                print('IN SWITCH ON ANIME')
                self.fa.onSendAnime()
                print('ANIMATE END')
                self.state = self.IDLE
                print('ANIMATE END1')
                self.stateLock.release()
                self.setMouse(False)
                print('ANIMATE END2')
                QThread.msleep(self.ANIMATION_DURATION)
                # time.sleep(self.ANIMATION_DURATION)
                print('ANIMATE END3')
            elif state == self.REANIME:
                self.fa.onSendReAnime()
                print('REANIMATE END')
                self.state = self.BUSY
                print('REANIMATE END1')
                self.stateLock.release()
                print('REANIMATE END2')
                QThread.msleep(self.ANIMATION_DURATION)
                # time.sleep(self.ANIMATION_DURATION)
                print('REANIMATE END3')
            else:
                print('WTF')
                self.stateLock.release()
                raise Exception('Error: what state')
            print('LOOP END')
        # 完全退出后再release
        self.loopLock.release()

    # def animate(self):
        # 此时进入,播放动画

        #
        # https://stackoverflow.com/questions/38284845/qpropertyanimation-not-running-immediately-when-qabstractanimationstart-is-c
        #
        # 由于这个坑问题导致思索
        # self.anim.start(
    def mouseMoveEvent(self, a0: QMouseEvent):
        self.setMouse(True)

    def mousePressEvent(self, a0: QMouseEvent):
        self.setMouse(True)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        self.setMouse(True)

