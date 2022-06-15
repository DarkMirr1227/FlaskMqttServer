#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time, threading, ssl, random
import json
import minimalmodbus
from time import _TimeTuple, sleep
#import htu21df

# client, user and device details
filepath ='C:/Users/lsy96/Desktop/serverTest/epico/deviceConfiguration.json' 
with open(filepath, encoding='utf-8') as data_file:
    json_data = json.loads(data_file.read())

serverUrl   =   json_data['serverUrl']  # tcp://mqtt.cumulocity.com 안됨 / mqtt.cumulocity.com  또는 IP 주소 사용할 것
port        =   json_data['port']
tenant      =   json_data['tenant']
username    =   json_data['username']
password    =   json_data['password']
sleepTime   =   json_data['sleepTime']

fRegistered = 0
global clientId
global deviceName
sensorNo = 1   
pumpNo = 1 
global client
instrument=minimalmodbus.Instrument('/dev/ttyS2', 1)  # port name, slave address (in decimal)
receivedMessages = []


def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
      
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial


def initComm():
    #instrument = minimalmodbus.Instrument('/dev/ttyS2', 1)  # port name, slave address (in decimal)
    #instrument.serial.port                     # this is the serial port name
    instrument.serial.baudrate = 9600         # Baud
    #instrument.serial.bytesize = 8
    #instrument.serial.parity   = serial.PARITY_NONE
    #instrument.serial.stopbits = 1
    instrument.serial.timeout  = 0.2          # seconds

    #instrument.address                         # this is the slave address number
    #instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
    #instrument.clear_buffers_before_each_transaction = True


def readNetworkEnable():
    #network 상태 읽기
    addr = 0xF400
    try :
        tWord = instrument.read_register(addr, 0, 3)
        if tWord == 0: 
            return False 
        else: 
            return True

    except IOError as e:
        print(repr(e))
        return False


# publish a message
def publish(topic, message, qos, waitForAck = False):
    ''' client가 message를 publish하는 함수

    args:
        topic:해당 topic으로 message를 upload
        message: 올릴 내용
        qos: 0=1번만 보냄,1=최소한번보냄,2=확인될때까지보냄..? 
        waitForAck: 받았다는 신호를 기다릴지 안기다릴지
    
    return:
        없음
    '''
    #print("send value")
    mid = client.publish(topic, message, qos)[1]
#    print("publish : "+ str(receivedMessages))
    if (waitForAck):
        while mid not in receivedMessages:
            print("sleep in while")
            time.sleep(0.25)


def on_publish(client, userdata, mid):
    #print(receivedMessages)
    receivedMessages.append(mid)


# display all incoming messages
def on_message(client, userdata, message):
    print("Received operation " + str(message.payload))
    if (message.payload.startswith("510")):   # 문자열이 510으로 시작하는지 true,false 판별
        print("Simulating device restart...")
        publish("s/us", "501,c8y_Restart", 2);
        print("...restarting...")
        time.sleep(3)
        publish("s/us", "503,c8y_Restart", 2);
        print("...done...")


def on_connect(client, userdata, flags, rc):
    #print(userdata)
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)
#        print('')

def on_disconnect(client, userdata, rc):
    print("disconnecting reason  "  +str(rc))
    client.connected_flag=False
    client.disconnect_flag=True


def unRegister():
    global fRegistered
    fRegistered = 0


def registerDevice():
    global pumpNo
    global sensorNo
    global clientId
    try:
        addr=0xF500
        values=[]
        values = instrument.read_registers(addr,4,3)
        tLong = (values[0]*256*256*256) + (values[1]*256*256) + (values[2]*256) + values[3]
        deviceName = str(tLong)
        print("deviceName = " + deviceName)

        addr=0xF600
        tWord = instrument.read_register(addr, 0, 3)
        print("tWord = " + str(tWord))
        pumpNo = int(tWord / 256)
        #pumpNo = 3
        sensorNo = tWord % 256
        print("punpNo = " + str(pumpNo))
        print("sensorNo = " + str(sensorNo))

        publish("s/us", " 200,Pump Total Number,Number,"+str(pumpNo)+",",0)

        publish("s/us", "100," + deviceName + ",c8y_MQTTDevice", 2, True)   # 템플릿 생성 Topic(100), Device Name, Device Type
        sleep(0.1)
        publish("s/uc/jylee", "100," + clientId + "," + deviceName, 2, True)   # 사용자 지정 템플릿(PUT) : 100, ClientId, DeviceName
        publish("s/us", "110," + clientId + ",EPICO Pump,Rev1.0", 2)   # 하드웨어 설정(110),  SerialNumber, Model, revision
        publish("s/us", "114,c8y_Restart", 2)
        print("Device registered successfully!")

        client.subscribe("s/ds")

        global fRegistered
        fRegistered = 1

    except IOError as e:
        print(repr(e))


def updateValues():
    global fRegistered
    global pumpNo

    if fRegistered == 0:
        registerDevice()
    
    #timestamp를 넣고 싶으면 여기다 넣으면 될듯함.
    timestamp = time.gmtime()
    #모든 펌프 정지/운행 상태
    addr = 0x100
    try :
        tWord = instrument.read_register(addr, 0, 4)
#            print(tWord)
        for i in range(0,pumpNo) : 
            x = int((tWord & (0x0001 << i)) != 0) 
            publish("s/us", "200,Pump"+ str(i+1) +" Status,Status,"+str(x)+",", 0)

    except IOError as e:
        print(repr(e))
    
    
    #펌프별 주파수/구동률
    try :
        for i in range(0,pumpNo) : 
            addr = 0x101 + i
            tWord = instrument.read_register(addr, 0, 4)
#               print(tWord)
            freq = int(tWord / 256)
            oper = tWord % 256

            
            publish("s/us", "200,Pump"+ str(i+1) +" Frequency,Frequency,"+str(freq)+",Hz", 0)
            publish("s/us", "200,Pump"+ str(i+1) +" Operating Ratio,Percent,"+str(oper)+",%", 0)

    except IOError as e:
        print(repr(e))
    
    
    #모든 펌프  트립/정상 상태
    addr = 0x200
    try :
        tLong = instrument.read_long(addr, 4)
#            print(tLong)
        for i in range(0,pumpNo) :
            x = int((tLong & (0x00000001 << i)) != 0)
            publish("s/us", "200,Pump"+ str(i+1) +" Trip Status,TripStatus,"+str(x)+",", 0)

    except IOError as e:
        print(repr(e))

    
    #펌프별 비트트립정보
    bitTripInfo = ["","Lack Of Water(1)","Communication","EOCR","General Inverter","Lack Of Water(5)","","Over Pressure","Over Current(8)","Under Voltage","","","Over Current(12)","Over Heating","Over Voltage(14)","Over Voltage(15)","","Under Pressure","Output Pressure(18)","Operation Limit(19)","Sensor Deviation(20)","Input Pressure(21)","","","","Pump No Power(25)"]
    try :
        for i in range(0, pumpNo) :
            addr = 0x201 + i
            tLong = instrument.read_long(addr, 4)
            
            for j in range(0,len(bitTripInfo)) :
                sleep(0.05)
                if len(bitTripInfo[j])==0 : 
                    continue
                x = int((tLong & (0x00000001 << j)) != 0)
                #print("200,Pump" + str(i+1) + " " + bitTripInfo[j] + " Trip, TripStatus," + str(x))
                publish("s/us", "200,Pump"+ str(i+1) + " " + bitTripInfo[j] + " Trip,TripStatus,"+str(x)+",", 0)
                
    except IOError as e:
        print(repr(e))
    
#publish("s/us", "200,Humid Mesurement,Humid,"+str(humid)+",%", 0)
    
    #대표 토출압력
    try : 
        addr = 0x300
        tWord = instrument.read_register(addr, 1, 4)
#            print(tWord)
        publish("s/us", "200,Output Pressure,Pressure,"+str(tWord)+",bar", 0)

    except IOError as e:
        print(repr(e))


    #소비전류(Amphere)
    try :
        for i in range(0,pumpNo) :
            addr = 0x401 + i
            tWord = instrument.read_register(addr, 1, 4)
            #print("tWord = " + str(tWord))
            publish("s/us", "200,Pump"+ str(i+1) + " Current Consumption,Current,"+str(tWord)+",A", 0)

    except IOError as e:
        print(repr(e))
    
    
    #소비전력(kW)
    try :
        for i in range(0,pumpNo) :
            addr = 0x501 + i
            tWord = instrument.read_register(addr, 1, 4)
#            print(tWord)
            publish("s/us", "200,Pump"+ str(i+1) + " Power Consumption,Power,"+str(tWord)+",kW", 0)

    except IOError as e:
        print(repr(e))


    #유량
    try :
        for i in range(0,pumpNo) :
            addr = 0x601 + i
            tWord = instrument.read_register(addr, 0, 4)
#            print(tWord)
            publish("s/us", "200,Pump"+ str(i+1) + " Flow Volume,Flow,"+str(tWord)+",m3/h", 0)

    except IOError as e:
        print(repr(e))


    #흡입압력
    try :
        addr = 0x700
        tWord = instrument.read_register(addr, 1, 4)
#            print(tWord)
        publish("s/us", "200,Input Pressure,Pressure,"+str(tWord)+",bar", 0)

    except IOError as e:
        print(repr(e))


    #Mode Sw
    try :
        addr = 0xF200
        tWord = instrument.read_register(addr, 0, 3)
#            print(tWord)

        publish("s/us", "200,User Run Stop,RunStop,"+str(tWord)+",", 0)

        for i in range(0,pumpNo) :
            publish("s/us", "200,Pump"+ str(i+1) +" Mode Switch,OffAutoManual,"+str(x)+",", 0)


    except IOError as e:
        print(repr(e))


    #Product Model
    try :
        addr = 0xF000
        tWord = instrument.read_register(addr, 0, 3)
#            print(tWord)
        publish("s/us", "200,Product Model,Product,"+str(tWord)+",", 0)

    except IOError as e:
        print(repr(e))


    #설정 압력
    try : 
        addr = 0xF700
        tWord = instrument.read_register(addr, 1, 3)
        publish("s/us", "200,Setting Pressure,Pressure,"+str(tWord)+",bar", 0)

    except IOError as e:
        print(repr(e))
    

# send temperature measurement
def sendMeasurements():  # 서브 스레드
    try:
        onOff = readNetworkEnable()
        if onOff == True:
            print("onOff = true")
            updateValues()
        else:
            print("onOff = false")
            unRegister()

        thread = threading.Timer(sleepTime, sendMeasurements)   # 새로운 서브 스레드 생성(요청) / Thread를 이용하여 얼마 간격으로 데이터를 전송할지 기입
        thread.daemon=True
        thread.start()

        # 현재 서브 스레드 작업 완료
        # 기존 코드는 스레드가 계속해서 생성되는데 이 스레드들이 죽지 않고 무한 반복을 하고 있었기 때문에 스레드 개수가 초과(247개) 되는 현상이었음

    except (KeyboardInterrupt, SystemExit):
        print("Received keyboard interrupt, quitting ...")


#do Work
def doWork():  # 메인 스레드
    try:
        thread = threading.Timer(1, sendMeasurements)   # 1초 뒤에 sendMeasurements 실행
        thread.daemon=True
        thread.start()

        while True: time.sleep(100) # 무한 반복
    except (KeyboardInterrupt, SystemExit):
        print("Received keyboard interrupt, quitting ...")

        

clientId = getserial()
client = mqtt.Client(clientId)
client.username_pw_set(tenant + "/" + username, password)
client.on_message = on_message
client.on_publish = on_publish
client.on_connect=on_connect
client.on_disconnect = on_disconnect
client.connect(serverUrl, port)
client.loop_start()

initComm()
doWork()

