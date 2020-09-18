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
#音声
import moviepy.editor as mp
#import pygame
import pyaudio
import wave
 
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.image = None
        self.playing = False#再生中
        self.stream = None#pyaudio
        
        #音
        #pygame.mixer.init(frequency = 44100)
        
        
        #リスト
        self.movs = []
        self.sliders = []
        # 横のレイアウト
        #self.horizon = QHBoxLayout()
        # 縦のレイアウト
        #self.vertical = QVBoxLayout()
        
        #timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._run)
        
        self.layout = QHBoxLayout()

        # 再生ボタン
        self.play_button = QPushButton('PLAY/STOP', self)
        self.play_button.clicked.connect(self.play)
        self.play_button.move(100, 450)
        self.play_button.resize(100,50)
        #self.layout.addWidget(self.play_button)

        self.load_button = QPushButton('movie load', self)
        self.load_button.clicked.connect(self.prepare_data)
        self.load_button.move(300, 450)
        self.load_button.resize(100,50)
        #self.layout.addWidget(self.load_button)

        #self.horizon.addLayout(self.vertical)
        #self.setLayout(self.vertical)
 
        self.setLayout(self.layout)
        self.setGeometry(300, 50, 800, 600)#(x,y,横,縦)
        self.setWindowTitle('MEXICALI')
        
        #self.show()
        
    def load_mov(self):
        filename = '../mov/nichijo.mp4'
        cap = cv2.VideoCapture(filename)
        #fourcc = cv2.VideoWriter_fourcc('H','2','6','4')  #fourccを定義
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
        ret, frame = cap.read()
        self.image = self.openCV2Qimage(frame)
        #cv2.imshow('frame', frame)
        #clip_input = mp.AudioFileClip(filename)#fps:44100
        wf = self.load_audio_from_movie(filename)
        #clip_input.preview()
        mov = {'cap':cap, 'fps':fps, 'width':w, 'height':h, 'maxFrame':max_frame, 'audio':wf}
        self.movs.append(mov)
        return cap

    def load_audio_from_movie(self, filename):
        clip_input = mp.AudioFileClip(filename)#fps:44100
        clip_input.write_audiofile('../wav/audio.wav')
        wf = wave.open("../wav/audio.wav", "rb")
        p = pyaudio.PyAudio()
        #self.chunk = 1024
        self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
        #data = wf.readframes(chunk)
        return wf
        #pygame.mixer.music.load("sample.wav")
        
        
    def change_frame(self, value, cap):
        cap.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = cap.read()
        #cv2.imshow('frame', frame)
        self.image = self.openCV2Qimage(frame)
        self.update()
        
    def run_audio(self, wf):
        chunk = 1024
        data = wf.readframes(chunk)
        self.stream.write(data)
    
    def set_mov_slider(self, cap):
        #スライダ
        self.slider = QSlider(Qt.Horizontal, self)
        #self.slider.setFocusPolicy(Qt.NoFocus)#?
        #slider.setGeometry(30, 40, 100, 30)
        self.slider.move(100,400)
        self.slider.resize(500,30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1)
        self.slider.setValue(0)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(lambda:self.change_frame(int(self.slider.value()), cap))
        #self.layout.addWidget(self.slider)
        self.slider.show()
        #self.show()
        
    def prepare_data(self):
        cap = self.load_mov()
        self.set_mov_slider(cap)
        #debug
        #self.show()
        print("Load fps: " + str(self.movs[0].get(cv2.CAP_PROP_FPS)))
        self.update()
        
    def play(self):
        if self.playing:
            self.playing = False
            if self.movs:
                self._timer.stop()
                print("stop")
        else:
            self.playing = True
            if self.movs:
                self._timer.start(1000/self.movs[0]['fps'])
                print("start")
        
    def _run(self):
        #動画の更新
        nowFrame = self.slider.value()
        nowFrame = nowFrame + 1
        self.change_frame(nowFrame, self.movs[0]['cap'])
        self.slider.setValue(nowFrame)
        self._timer.start(1000/self.movs[0]['fps'])
        #音の更新
        self.run_audio(self.movs[0]['audio'])
        
    def paintEvent(self, event):
        # デバッグ用
        #print('paintEvent Start')
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor('#FFFFFF'))
        painter.setBrush(Qt.white)
        #painter.drawRect(event.rect())
        # デバッグ用
        #print('painter tool set')
        if self.image == None:
            return
        #image = QtGui.QImage('./sample01.jpg')
        #x = (self.width() - self.image.width()) / 2
        #y = (self.height() - self.image.height()) / 2
        #painter.drawImage(0, 0, self.image)
        #imgWidth = main_window.movs[0].get(cv2.CAP_PROP_FRAME_WIDTH)
        #imgHeight = main_window.movs[0].get(cv2.CAP_PROP_FRAME_HEIGHT)
        imgWidth = self.image.width()
        imgHeight = self.image.height()
        painter.drawPixmap(0, 0, imgWidth/2, imgHeight/2, QPixmap.fromImage(self.image.scaled(imgWidth/2, imgHeight/2)))
        #painter.drawPixmap(self.rect(), QPixmap.fromImage(self.image))
        painter.end()

    #画像変換
    def openCV2Qimage(self, cvImage):
        height, width, channel = cvImage.shape
        bytesPerLine = channel * width
        cvImageRGB = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
        image = QImage(cvImageRGB, width, height, bytesPerLine, QImage.Format_RGB888)
        #image = QImage(cvImage, width, height, bytesPerLine, QImage.Format_RGB888)
        #image = image.rgbSwapped()
        return image

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
