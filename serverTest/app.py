# pip install Flask
from flask import Flask, render_template
# pip install Flask-MQTT
from flask_mqtt import Mqtt
# pip install apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import MessageToJson
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '127.0.0.1'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_UERSNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
SUBTOPIC =  's/us'
global data
global allData
allData = list()
trans = MessageToJson.MessageToJson()
mqtt =Mqtt(app)

def schedulerFunction():
    print("Scheduler is working\n")
    if len(allData) > 1:
        print("data move to file")
        trans.saveJsonInListAuto(allData)
        allData.clear #리스트에 데이터 파일로 욺기고 초기화

sched = BackgroundScheduler(daemon=True)
sched.add_job(schedulerFunction,'cron',second = '30') #시간(스캐줄)에 맞춰 함수부르기
if __name__ == '__main__':
    app.run(debug=True)
sched.start()


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
        allData.append(trans.transMessageToJson(trans.timestamp(data)))




@app.route('/index.html')
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/generic.html')
def generic():
    return render_template('generic.html')

#TODO: 한 변수에 한꺼번에 보내는 것보다는 여러개로 나눠서 보내는게 좋을 듯 함. 
@app.route('/elements.html')
def elements():
    print(allData)
    return render_template('elements.html',jsonData=allData)
    