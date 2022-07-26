# pip install Flask
from flask import Flask, render_template, request
from flask import jsonify
# pip install Flask-MQTT
from flask_mqtt import Mqtt
# pip install apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import DataManagement
import MessageToJson
import os
global data
global allData
global classifyIdGroup
def schedulerFunction():
    global allData
    print("Scheduler is working\n")
    print("list lenth :",len(allData))
    if len(allData) > 1:
        print("data move to file")
        trans.saveJsonInListAuto(allData)
        allData.clear() #리스트에 데이터 파일로 욺기고 초기화

# 처음 한번 동작하는 코드 시작 #
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true': #flask에서 디버그모드에서 2번 반복되는 것을 방지하기 위함 초기화할 함수는 여기서만
    classifyIdGroup = [[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15],[16,17,18,19,20]] #그룹별로 묶일 id 셋팅
    app = Flask(__name__)
    app.config['MQTT_BROKER_URL'] = '127.0.0.1'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_UERSNAME'] = ''
    app.config['MQTT_PASSWORD'] = ''
    SUBTOPIC =  's/us'
    allData = list()
    trans = MessageToJson.MessageToJson()
    dataManage = DataManagement.DataManagement()
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0')
    mqtt =Mqtt(app)
    sched = BackgroundScheduler(daemon=True,timezone='Asia/Seoul')
    sched.add_job(schedulerFunction,'cron', minute = '0',misfire_grace_time=15) #시간(스캐줄)에 맞춰 함수부르기 / misfire_grace_time =>정해진 시간에 스케줄러가 못 돌아갔을 때, (15)초동안 스케줄러가 돌수 있는 환경이 되면 돌아갈 수 있게 해줌.
    sched.start()
# 처음 한번 동작하는 코드 끝 #


def create_app():
    app = Flask(__name__)
    mqtt.init_app(app)

@mqtt.on_connect()
def handle_connect(clinet,userdata,flags,rc):
    mqtt.subscribe(SUBTOPIC)
    print("connect!")

@mqtt.on_message() #메세지 받을 때 호출되는 함수
def handle_mqtt_message(client,userdata,message):
    global data  
    global allData
    # payload = message
    print('get message!')
    if message.topic == SUBTOPIC:
        data = dict(
            message = message.payload.decode()
        )
        # 타임스탬프 찍어서 json형태로 allData 리스트에 저장.
        allData = allData + trans.transMessageToJson(trans.timestamp(data))

@app.route('/index.html')
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/generic.html')
def generic():
    return render_template('generic.html',jsonData=allData,listCount =len(allData)) 

@app.route('/elements.html',methods=["GET","POST"])
def elements():
    global allData
    global classifyIdGroup
    if request.method == "POST":
        jsonData=dataManage.classifyGroup(dataManage.extractRecentData(allData,20),classifyIdGroup) #데이터 그룹별로 분리하고 정리
        return jsonify(jsonData)
    else:
        if len(allData) < 2 :
            _jsonData=dataManage.classifyGroup(dataManage.extractRecentData(trans.emptyJson(),3),classifyIdGroup) #데이터 그룹별로 분리하고 정리
            return render_template('elements.html',jsonData=_jsonData)
        else:
            _jsonData=dataManage.classifyGroup(dataManage.extractRecentData(allData,20),classifyIdGroup) #데이터 그룹별로 분리하고 정리
            return render_template('elements.html',jsonData=_jsonData)

@app.route('/database.json',methods=["POST"])
def database():
    global allData
    global classifyIdGroup
    jsonData = dataManage.extractRecentData(allData,20) #데이터 그룹별로 분리하고 정리
    trans.saveJsonInList("templates/database.json",jsonData)
    return jsonify(trans.loadJsonfile("templates/database.json"))

@app.route('/graph.html')
def graph_html():
    _jsonData=dataManage.classifyGroup(dataManage.extractRecentData(allData,20),classifyIdGroup) #데이터 그룹별로 분리하고 정리
    return render_template('graph.html',jsonData=_jsonData)