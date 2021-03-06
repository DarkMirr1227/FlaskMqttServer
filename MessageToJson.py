import json
from datetime import datetime
# testString = "1 1.1 1.2 1.1 23.3 24.3 23.5 60" 
# "id[1] current[3] temperture[3] vibration[1]"
class MessageToJson:

    def emptyJson(self):
        ''' 값이 0으로 채워진 json(dict)을 2개를 가진 리스트를 리턴하는 함수

            args: 

            return:
                _emptyJson : 0으로 채워진 json
        '''
        _emptyJson = {
                "id": 1,
                "time": '0000-00-00T00h00m00_000',
                "current":[0,0,0],
            "temperature" :[0,0,0],
            "vibration" : 0
        }
        _list = list()
        _list.append(_emptyJson)
        _list.append(_emptyJson)
        return _list

    def timestamp(self,_message):
        '''메세지 받을 때 timestamp 찍어주는 함수.

            args:
                _message : mqtt에서 받은 메세지
            return:
                dict : [time, message]
        '''
        return dict(
            time = datetime.utcnow().strftime('%Y-%m-%dT%Hh%Mm%S_%f')[:-3], message = _message
        )

    def transMessageToJson(self,_dict):
        '''string인 message를 받아서 모터id 및 각종 센서값을 정리하고 이것을 json형태로 바꿔주는 함수

            args:
                _dict : 메세지가 저장된 딕셔너리
            return:
                json : 모터id 와 센서값이 저장된 json
        '''

        temptime = _dict['time'] 
        #_dict['message'] = {'message': '1 0.1 0.2 0.1 2.3 2.4 2.2 5'}
        #TODO: 다른형식의 데이터가 들어올 때 예외처리해줘야함.
        try:
            message = str(_dict['message'])[13:-2].split(' ')
            # message의 string 값을 다른 데이터로 바꾸는 코드 필요 (mqtt보낼 메세지 먼저 정의하고 구현해야함.) 
            JsonList = []
            for i in range(0,40,8):
                tempJson = {
                    "id": message[i+0],
                    "time": temptime,
                    "current":message[i+1:i+4],
                "temperature" :message[i+4:i+7],
                "vibration" :message[i+7]
                }
                JsonList.append(tempJson)
            return JsonList
        except IndexError as err:
            print('error:' , err)
            return None

    def saveJsonInList(self,_filename, _list):
        '''element가 json인 list를 파일로 저장하는 함수

            args:
                _filename : 저장할 파일의 이름,경로
                _list : json이 저장된 리스트
        '''
        with open(_filename, 'w') as f:
            json.dump(_list,f,indent=2)
        #_list.clear() #저장된 리스트 데이터 지우기

    def saveJsonInListAuto(self,_list):
        ''' 파일이름을 리스트에 시작time과 끝 time으로 저장해주는 함수
            저장경로는 data폴더

            args:
                _list : json이 저장된 리스트
        '''
        if len(_list) == 0:
            print("list is empty! / Can't make file.")
            return
        first_time = _list[0]['time'] #json으로 변환된 시간을 다시 원래 struct_time 형태로 변환
        last_time = _list[-1]['time']
        filename ='('+first_time+')_('+last_time+').json'
        filename = 'data/'+filename 
        print(filename)
        self.saveJsonInList(filename,_list)
        

    def loadJsonfile(self,_filename):
        '''저장된 json파일을 다시 읽어오는 함수 (읽어서 Json형태로 변환)

            args:
                _filename : 읽어올 파일 이름,경로 (확장자까지 써주기)
            return:
                json_object
        '''
        with open(_filename) as f:
            json_object = json.load(f)
        return json_object

#for test
''' 
fanJson = {
    "id": '001',
    "time": time.gmtime(),
    "current":[1,2,3],
    "temperature" :[4,5,6],
    "vibration" : 60
}
tempList = []
tempList.append(fanJson)
saveJsonInList('motor_data.json',tempList)
print(tempList)
json_object = loadJsonfile('motor_data.json')

assert json_object[0]['id'] == '001','error! It\'s not 001'
nowTime = time.struct_time(json_object[0]['time']) #json으로 변환된 시간을 다시 원래 struct_time 형태로 변환하는 법
print(time.strftime('%Y-%m-%dT%H:%M:%SZ', nowTime)) #struct_time을 보기편하게 출력하기
print(len(json_object))
'''