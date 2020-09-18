import numpy as np
import cv2
import sys

#動画カット編集ソフトとりあえずCUIで頑張るバージョン
def cv_use():
    #args = sys.argv #コマンドライン引数でファイル名をもらう
    cap = cv2.VideoCapture('')

    #fourcc = cv2.VideoWriter_fourcc('H','2','6','4')  #fourccを定義

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    max = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    flameWidth = 100 #-の数
    px = max/flameWidth #どれくらいの分量が一つの-ぶに値するか。
    fourcc = cv2.VideoWriter_fourcc('a','v','c','1')

    ret, frame = cap.read()
    nowFlame = 0 #現在のフレーム位置
    startFlame = 0 #書き出す際のスタート位置
    endFlame = 0 #書き出す際のエンド位置
    outID = 1 #書き出すファイルにIDをつけるため

    print("fps:",fps,",maxFlame:",max,"の動画です。")

    cap.release()
    cv2.destroyAllWindows()
