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
#threadingやってみますか
import threading
 
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        #初期化（一度しか通らないよね・・・？）
        #self.image = None
        self.playing = False#再生中
        self.stream = None#pyaudio
        #self.frame_offset = 0#スタートの時のフレーム位置
        #self.prepare_imgs_num = 1024#プレイ時に何枚のフレームを準備しておくか。
        
        #音
        #pygame.mixer.init(frequency = 44100)

        #リスト
        self.movs = []
        self.wavs = []#んー複数の音声処理はあとになるかもな。
        self.master_wav = None#実際に再生する時の音
        self.master_images = None#実際に再生する時の画像
        self.frame_rate = 30.0
        self.sample_rate = 44100.0
        
        
        self.sliders = []
        self.pre_frame = -2#スライダで再生時に使用
        #self.imgs = []#再生のときにコンバート済みを準備したい。
        # 横のレイアウト
        #self.horizon = QHBoxLayout()
        # 縦のレイアウト
        #self.vertical = QVBoxLayout()
        
        #timer
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._run)
        
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
        filename = '../mov/hff1.mp4'
        cap = cv2.VideoCapture(filename)
        #fourcc = cv2.VideoWriter_fourcc('H','2','6','4')  #fourccを定義
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        max_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
        ret, frame = cap.read()
        #self.image = self.openCV2Qimage(frame)
        cv2.imshow('frame', frame)
        #clip_input = mp.AudioFileClip(filename)#fps:44100
        #clip_input.preview()
        mov = {'cap':cap, 'fps':fps, 'width':w, 'height':h, 'maxFrame':max_frame}
        self.movs.append(mov)
        
        wf = self.load_audio_from_movie(filename)
        if wf is not None:#音声がある場合、
            chunk = (int)(wf.getframerate()/fps)
            wav = {'audio':wf, 'samplerate':wf.getframerate(), 'chunksize':chunk}#チャンクサイズは動画のフレームレートに依存する。編集時のfpsなんて勝手に決めちゃっていいんじゃね。
            self.wavs.append(wav)
        return cap

    def load_audio_from_movie(self, filename):
        clip_input = mp.AudioFileClip(filename)#fps:44100固定？
        try:
            clip_input.write_audiofile('../wav/audio.wav')
        except:
            print("音声の含まれない動画ファイルなので、音声を読み込みませんでした")
            #sys.exit()
            return None
        else:
            wf = wave.open("../wav/audio.wav", "rb")
            print("samplerate: ", wf.getframerate())
            p = pyaudio.PyAudio()
            #self.chunk = 1024
            self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
            #data = wf.readframes(chunk)
            return wf
            #pygame.mixer.music.load("sample.wav")
        
    def change_slider_value(self, value, cap):
        #1つ違いの移動->自動移動ということで、手動移動を判断
        if value - self.pre_frame is not 1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, value)
            ret, frame = cap.read()
            cv2.imshow('frame', frame)
            self.prepare_audio()
            #print(str(value), str(self.pre_frame))
            #self.image = self.openCV2Qimage(frame)
            #self.update()
        self.pre_frame = self.slider.value()
    
    def set_mov_slider(self, cap):
        #スライダ
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFocusPolicy(Qt.NoFocus)
        #slider.setGeometry(30, 40, 100, 30)
        self.slider.move(100,400)
        self.slider.resize(500,30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1)
        self.slider.setValue(0)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(lambda:self.change_slider_value(int(self.slider.value()), cap))
        #self.layout.addWidget(self.slider)
        self.slider.show()
        #self.show()
        
    def prepare_data(self):
        cap = self.load_mov()
        self.set_mov_slider(cap)
        #debug
        #self.show()
        print("Load fps: " + str(self.movs[0]['fps']))
        self.update()

        """
    def prepare_imgs(self):#再生のとき使う画像準備。全部はやっぱだめだわ。
        imgs = []#初期化
        index = 0
        self.frame_offset = self.slider.value()
        self.movs[0]['cap'].set(cv2.CAP_PROP_POS_FRAMES, self.slider.value())
        #self.movs[0]['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.movs[0]['cap'].read()
        while ret and index < self.prepare_imgs_num:
            cvt_image = self.openCV2Qimage(frame)
            scaled_image = cvt_image.scaled(cvt_image.width()/2, cvt_image.height()/2)
            imgs.append(scaled_image)
            ret, frame = self.movs[0]['cap'].read()
            index = index + 1
        self.imgs = imgs
        """
    def prepare_audio(self):#再生の直前のオーディオ準備
        #鳴らす時にread_framesするので、ポインタを動かしておくだけで良い。
        self.wavs[0]['audio'].rewind()
        if self.slider.value() is not 0:
            start_frame = (int)((self.slider.value()/self.frame_rate) * self.sample_rate)
            eliminate_audio = self.wavs[0]['audio'].readframes(start_frame)
        
    def play(self):
        if self.playing:
            self.playing = False
            if self.movs:
                self.frame_timer.stop()
                print("stop")
        else:
            self.playing = True
            if self.movs:
                self.frame_timer.start(1000/self.movs[0]['fps'])
                #self.prepare_imgs()
                self.prepare_audio()
                #ここにスタート時の準備書くけど関数化しするかも
                print("start")
                
    def run_audio(self):
        chunk = self.wavs[0]['chunksize'] + 1
        data = self.wavs[0]['audio'].readframes(chunk)
        self.stream.write(data)
        
    def run_image(self):
        nowFrame = self.slider.value() + 1
        #nowFrame = nowFrame + 1
        #self.change_frame(nowFrame, self.movs[0]['cap'])
        ret, frame = self.movs[0]['cap'].read()
        cv2.imshow('frame', frame)
        print('now:', str(nowFrame),' pre:', str(self.pre_frame))
        self.slider.setValue(nowFrame)
        
    def _run(self):
        self.frame_timer.start((1000/self.movs[0]['fps']) - 1) #
        thread1 = threading.Thread(target=self.run_audio)
        thread2 = threading.Thread(target=self.run_image)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        #self.run_audio()
        #self.run_image()
        #更新
        #nowFrame = self.slider.value()
        #nowFrame = nowFrame + 1
        #self.change_frame(nowFrame, self.movs[0]['cap'])
        #self.slider.setValue(nowFrame)
        '''
        imgID = nowFrame - self.frame_offset
        if imgID >= self.prepare_imgs_num - 1:
            self.prepare_imgs()
        self.image = self.imgs[imgID]
        self.update()
        '''
        #ret, frame = self.movs[0]['cap'].read()
        #cv2.imshow(frame)
        #音の更新
        #if nowFrame%10 == 1:
        #self.run_audio()

        """
    def paintEvent(self, event):
        # デバッグ用
        #print('paintEvent Start')
        painter = QPainter()
        painter.begin(self)
        #painter.setPen(QColor('#FFFFFF'))
        #painter.setBrush(Qt.white)
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
        #imgWidth = self.image.width()
        #imgHeight = self.image.height()
        painter.drawPixmap(0, 0, self.image.width(), self.image.height(), QPixmap.fromImage(self.image))
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
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
