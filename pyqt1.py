import sys
#UI
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sip
#画像処理
import numpy as np
import cv2
#時間
import time
 
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.image = None
        self.playing = False#再生
        # 横のレイアウト
        #self.horizon = QHBoxLayout()
        # 縦のレイアウト
        #self.vertical = QVBoxLayout()
 
        # 再生ボタン
        '''
        self.button = QPushButton('PLAY', self)
        self.button.clicked.connect(self.play)
        self.button.move(150, 50)
        self.button.resize(100,50)
        '''
        self.layout = QHBoxLayout()
        self.checkBoxA = QCheckBox("PLAY")
        self.checkBoxA.toggled.connect(lambda:self.play())
        self.layout.addWidget(self.checkBoxA)
        
        #リスト
        self.movs = []
        self.sliders = []
        
        self.load_button = QPushButton('movie load', self)
        self.load_button.clicked.connect(self.prepare_data)
        self.load_button.move(150, 200)
        self.load_button.resize(100,50)
        self.layout.addWidget(self.load_button)

        '''
        self.label = QLabel(self)
        self.label.setText('0')
        self.label.setGeometry(160, 40, 80, 30)
        '''
 
        #self.horizon.addLayout(self.vertical)
        #self.setLayout(self.vertical)
 
        self.setLayout(self.layout)
        self.setGeometry(300, 50, 800, 500)#(x,y,横,縦)
        self.setWindowTitle('MEXICALI')
        
        #self.show()
 
    def output(self):
        outputs = []
        outputs.append("A")
        for output in outputs:
            print(output)
            
    def changeValue(self, value):
        self.label.setText(str(value))
        
    def load_mov(self):
        cap = cv2.VideoCapture('./mov/mugi.mp4')
        #fourcc = cv2.VideoWriter_fourcc('H','2','6','4')  #fourccを定義
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
        ret, frame = cap.read()
        self.image = self.openCV2Qimage(frame)
        #cv2.imshow('frame', frame)
        self.movs.append(cap)
        return cap
        #set_slider(max_frame)
        
    def change_frame(self, value, cap):
        cap.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = cap.read()
        #cv2.imshow('frame', frame)
        self.image = self.openCV2Qimage(frame)
        #self.show()
    
    def set_mov_slider(self, cap):
        #スライダ
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFocusPolicy(Qt.NoFocus)#?
        #slider.setGeometry(30, 40, 100, 30)
        self.slider.move(100,100)
        self.slider.resize(500,100)
        self.slider.setMinimum(0)
        self.slider.setMaximum(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1)
        self.slider.setValue(0)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(lambda: self.change_frame(int(self.slider.value()), cap))
        self.layout.addWidget(self.slider)
        #self.slider.show()
        
        #self.show()
        #print("debug")
        
    def prepare_data(self):
        cap = self.load_mov()
        self.set_mov_slider(cap)
        #debug
        #self.show()
        print("fps: " + str(self.movs[0].get(cv2.CAP_PROP_FPS)))
        self.makeWindow()
        '''
    def paintEvent(self, event):
        # デバッグ用
        print('paintEvent Start')
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor('#FFFFFF'))
        painter.setBrush(Qt.white)
        #painter.drawRect(event.rect())
        # デバッグ用
        print('painter tool set')
        if self.image == None:
            return
        #image = QtGui.QImage('./sample01.jpg')
        #x = (self.width() - self.image.width()) / 2
        #y = (self.height() - self.image.height()) / 2
        #painter.drawImage(0, 0, self.image)
        #imgWidth = main_window.movs[0].get(cv2.CAP_PROP_FRAME_WIDTH)
        #imgHeight = main_window.movs[0].get(cv2.CAP_PROP_FRAME_HEIGHT)
        #imgWidth = self.image.width()
        #imgHeight = self.image.height()
        #painter.drawPixmap(0, 0, imgWidth, imgHeight, QPixmap.fromImage(self.image))
        painter.drawPixmap(0, 0, QPixmap.fromImage(self.image))
        painter.end()
        '''

    def play(self):
        '''
        if(not self.playing):
            self.playing = True
        else:
            self.playing = False
        '''
        for i in range((int)(100)):
            self.slider.setValue(i)
            self.slider.show()
            main_window.movs[0].set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = main_window.movs[0].read()
            self.image = self.openCV2Qimage(frame)
            #cv2.imshow('frame', frame)

    #画像変換
    def openCV2Qimage(self, cvImage):
        height, width, channel = cvImage.shape
        bytesPerLine = channel * width
        cvImageRGB = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
        image = QImage(cvImageRGB, width, height, bytesPerLine, QImage.Format_RGB888)
        #image = QImage(cvImage, width, height, bytesPerLine, QImage.Format_RGB888)
        #image = image.rgbSwapped()
        return image
        
    def makeWindow(self):
        subWindow = SubWindow(self)
        subWindow.show()

'''
def play(main_window):
    if main_window.movs:
        fps = main_window.movs[0].get(cv2.CAP_PROP_FPS)
        start = time.time()
        print('debug2')
        while(main_window.playing):
            print('debug3')
            if(time.time() - start > fps):
                ret, frame = main_window.movs[0].read()
                cv2.imshow('frame', frame)
                start = time.time()
                print('debug4')
                '''
                
class SubWindow(QWidget):#動画ほ表示ウィンドウ
    def __init__(self, parent=None):

        # こいつがサブウィンドウの実体？的な。ダイアログ
        self.w = QDialog(parent)
        self.parent = parent #親ウィンドウ
        label = QLabel()
        label.setText('MOV Window')
        layout = QHBoxLayout()
        layout.addWidget(label)
        self.w.setLayout(layout)

    def show(self):
        self.w.exec_()
    
    def paintEvent(self, event):
        # デバッグ用
        print('paintEvent Start')
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor('#FFFFFF'))
        painter.setBrush(Qt.white)
        #painter.drawRect(event.rect())
        # デバッグ用
        print('painter tool set')
        if self.parent.image == None:
            return
        painter.drawPixmap(self.rect(), QPixmap.fromImage(self.parent.image))
        painter.end()

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    #play(main_window)
    '''
    print('debug1')
    while(1):
        if main_window.movs:
            fps = main_window.movs[0].get(cv2.CAP_PROP_FPS)
            start = time.time()
            print('debug2')
            while(main_window.playing):
                print('debug3')
                if(time.time() - start > fps):
                    ret, frame = main_window.movs[0].read()
                    cv2.imshow('frame', frame)
                    start = time.time()
                    print('debug4')
                    '''
    sys.exit(app.exec_())
