# Компьютерное зрение в робототехнике 

## Подготовка к работе 
_____
Перед началом работы нам нужно установить необходимые *библиотеки*

~~~ python 
    pip install opencv-python
    pip install cvzone 
    pip install mediapipe
    pip install python-math
    pip install pyserial
    pip install pyqtgraph
    pip install PyQt5
~~~
_____

## Создание пользовательского интерфейса 
____

Для создания интерфейса мы будем использовать программу [qt Designer](https://build-system.fman.io/qt-designer-download), но вы можете воспользоваться способами,которые будут удобны вам. 

В открывшейся программе создаём новое окно.Для этого во вкладке ***File*** жмём на кпопку ***New*** и в окне,которое вспыло , выбираем ***Widget***

Меняем длину и ширину создонного окна

![](https://sun9-12.userapi.com/impg/xD-A0yqxwjXQSVPlUwx1GSyrGFx3mkIsoQ10uA/rYJ4gHYoVDE.jpg?size=533x141&quality=96&sign=75f9af0c5254b19d82d260b1869d124c&type=album) 

Из меню элементов, которое находится слева переносим ***Group Box*** в него помещаем ***Combo Box*** и два ***Puch Button*** 
В итоге должно получиться что-то похожее на это 

![](https://sun9-38.userapi.com/impg/hfYHDy5Y8v4pGPRAQvD-wxVvvxWxoUAMNc_1Xw/wW-O82GaRY8.jpg?size=438x141&quality=96&sign=5ef14d28b26c4fbaf4ccc16fff46dfba&type=album) 

сохраняем проект и закрываем программу 
____

## Пишем код для python 

_____
Импортиуем устоновленные ранее библиотеки
~~~ python
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
~~~


Загружаем пользовательский интерфейс 

~~~ python

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("SerialGUI")

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
~~~


в функции ***onOpen*** происходит  инцилизация технического зрения при нажатии на кнопку

~~~python 

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
~~~

Функция ***serialSend*** , которыя вызвается в ***onOpen*** отвечает, за отправку данных на ***serial-port***

~~~python
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
~~~

_____

## Коментарии к коду для ардуино

Для того чтобы считать данные с **Serial Port** необходимо написать слюдующие строки 

~~~arduino 
 if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');} 
~~~
____



