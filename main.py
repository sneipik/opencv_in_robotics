
# coding: utf8
from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import cv2
import mediapipe as mp
import math
import serial
from serial import Serial
# https://stackoverflow.com/questions/35932660/qcombobox-click-event обновление по клику

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("SerialGUI")

#ser = serial.Serial('COM6', 9600, timeout=1)
serial1 = QSerialPort()
serial1.setBaudRate(115200)
portList = []
ports = QSerialPortInfo().availablePorts()
for port in ports:
    portList.append(port.portName())
ui.comL.addItems(portList)

posX = 200
posY = 100
listX = []
for x in range(100): listX.append(x)
listY = []
for x in range(100): listY.append(0)


def onRead():
    if not serial1.canReadLine(): return     # выходим если нечего читать
    rx = serial1.readLine()
    rxs = str(rx, 'utf-8').strip()
    data = rxs.split(',')
    if data[0] == '0':
        ui.lcdN.display(data[1])
        ui.tempB.setValue(int(float(data[3]) * 10))
        ui.tempL.setText(data[3])
        global listX
        global listY
        listY = listY[1:]
        listY.append(int(data[2]))
        ui.graph.clear()
        ui.graph.plot(listX, listY)

    if data[0] == '1':
        if data[1] == '0':
            ui.circle.setChecked(True)
        else:
            ui.circle.setChecked(False)

    if data[0] == '2':
        global posX
        global posY
        posX += int((int(data[1]) - 512) / 100)
        posY += int((int(data[2]) - 512) / 100)
        ui.circle.setGeometry(posX, posY, 20, 20)


def onOpen():
  global ser 
  ser = serial.Serial(str(ui.comL.currentText()), 9600, timeout=1)
  cap = cv2.VideoCapture(0)  # основаня камера
  detector = HandDetector(detectionCon=0.8, maxHands=2)
  while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
      hand1 = hands[0]
      lmList = hand1["lmList"]
      fingers1 = detector.fingersUp(hand1)
      serialSend(fingers1)
    cv2.imshow("Image", img)
    if cv2.waitKey(40) == 27:
      break

        # List of 21 Landmark points
        # bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        # centerPoint1 = hand1['center']  # center of the hand cx,cy
        # handType1 = hand1["type"]  # Handtype Left or Right


def serialSend(data):


    print(type(data))

    if data[0]==1:
      #ser.write(str(data[0]+"\n".encode('utf8')))
      ser.write(str("led1_on"+'\n').encode('utf8'))
      #ser.write(b"led1_on\n")
      ser.flush()
    else :
      ser.write(b"led1_off\n")
      ser.flush()

    if data[1] == 1:
        ser.write(b"led2_on\n")
        ser.flush()
    else:
        ser.write(b"led2_off\n")
        ser.flush()
    if data[2] == 1:
        ser.write(b"led3_on\n")
        ser.flush()
    else:
        ser.write(b"led3_off\n")
        ser.flush()
    if data[3] == 1:
        ser.write(b"led4_on\n")
        ser.flush()
    else:
        ser.write(b"led4_off\n")
        ser.flush()
    if data[4] == 1:
        ser.write(b"led5_on\n")
        ser.flush()
    else:
        ser.write(b"led5_off\n")
        ser.flush()

    ser.flush()
    line = ''


    #serial.write(txs.encode())


def onClose():
    serial1.close()


def ledControl(val):
    if val == 2: val = 1;
    serialSend([0, val])


def fanControl(val):
    if val == 2: val = 1;
    serialSend([3, val])


def bulbControl(val):
    if val == 2: val = 1;
    serialSend([4, val])


def RGBcontrol():
    serialSend([1, ui.RS.value(), ui.GS.value(), ui.BS.value()])


def servoControl(val):
    serialSend([2, val])


def sendText():
    txs = "5,"
    txs += ui.textF.displayText()
    txs += ';'
    serial1.write(txs.encode())






class HandDetector:
  """
  Finds Hands using the mediapipe library. Exports the landmarks
  in pixel format. Adds extra functionalities like finding how
  many fingers are up or the distance between two fingers. Also
  provides bounding box info of the hand found.
  """

  def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
    """
    :param mode: In static mode, detection is done on each image: slower
    :param maxHands: Maximum number of hands to detect
    :param detectionCon: Minimum Detection Confidence Threshold
    :param minTrackCon: Minimum Tracking Confidence Threshold
    """
    self.mode = mode
    self.maxHands = maxHands
    self.detectionCon = detectionCon
    self.minTrackCon = minTrackCon

    self.mpHands = mp.solutions.hands
    self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                    self.detectionCon, self.minTrackCon)
    self.mpDraw = mp.solutions.drawing_utils
    self.tipIds = [4, 8, 12, 16, 20]
    self.fingers = []
    self.lmList = []

  def findHands(self, img, draw=True, flipType=True):
    """
    Finds hands in a BGR image.
    :param img: Image to find the hands in.
    :param draw: Flag to draw the output on the image.
    :return: Image with or without drawings
    """
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    self.results = self.hands.process(imgRGB)
    allHands = []
    h, w, c = img.shape
    if self.results.multi_hand_landmarks:
      for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
        myHand = {}
        ## lmList
        mylmList = []
        xList = []
        yList = []
        for id, lm in enumerate(handLms.landmark):
          px, py = int(lm.x * w), int(lm.y * h)
          mylmList.append([px, py])
          xList.append(px)
          yList.append(py)

        ## bbox
        xmin, xmax = min(xList), max(xList)
        ymin, ymax = min(yList), max(yList)
        boxW, boxH = xmax - xmin, ymax - ymin
        bbox = xmin, ymin, boxW, boxH
        cx, cy = bbox[0] + (bbox[2] // 2), \
                 bbox[1] + (bbox[3] // 2)

        myHand["lmList"] = mylmList
        myHand["bbox"] = bbox
        myHand["center"] = (cx, cy)

        if flipType:
          if handType.classification[0].label == "Right":
            myHand["type"] = "Left"
          else:
            myHand["type"] = "Right"
        else:
          myHand["type"] = handType.classification[0].label
        allHands.append(myHand)

        ## draw
        if draw:
          self.mpDraw.draw_landmarks(img, handLms,
                                     self.mpHands.HAND_CONNECTIONS)
          cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                        (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                        (255, 0, 255), 2)
          cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                      2, (255, 0, 255), 2)
    if draw:
      return allHands, img
    else:
      return allHands

  def fingersUp(self, myHand):
    """
    Finds how many fingers are open and returns in a list.
    Considers left and right hands separately
    :return: List of which fingers are up
    """
    myHandType = myHand["type"]
    myLmList = myHand["lmList"]
    if self.results.multi_hand_landmarks:
      fingers = []
      # Thumb
      if myHandType == "Right":
        if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
          fingers.append(1)
        else:
          fingers.append(0)
      else:
        if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
          fingers.append(1)
        else:
          fingers.append(0)

      # 4 Fingers
      for id in range(1, 5):
        if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
          fingers.append(1)
        else:
          fingers.append(0)
    return fingers

  def findDistance(self, p1, p2, img=None):
    """
    Find the distance between two landmarks based on their
    index numbers.
    :param p1: Point1
    :param p2: Point2
    :param img: Image to draw on.
    :param draw: Flag to draw the output on the image.
    :return: Distance between the points
             Image with output drawn
             Line information
    """

    x1, y1 = p1
    x2, y2 = p2
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    length = math.hypot(x2 - x1, y2 - y1)
    info = (x1, y1, x2, y2, cx, cy)
    if img is not None:
      cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
      cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
      cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
      cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
      return length, info, img
    else:
      return length, info







#    if lmList:
#       fingers = detector.fingersUp()
#      print(fingers)
# mySerial.sendData(fingers)
# cv2.imshow("Image",img)
# if cv2.waitKey(40) == 27:
#   break


serial1.readyRead.connect(onRead)
ui.openB.clicked.connect(onOpen)
ui.closeB.clicked.connect(onClose)

ui.ledC.stateChanged.connect(ledControl)
ui.fanC.stateChanged.connect(fanControl)
ui.bulbC.stateChanged.connect(bulbControl)
ui.RS.valueChanged.connect(RGBcontrol)
ui.GS.valueChanged.connect(RGBcontrol)
ui.BS.valueChanged.connect(RGBcontrol)
ui.servoK.valueChanged.connect(servoControl)
ui.sendB.clicked.connect(sendText)

ui.show()
app.exec()
