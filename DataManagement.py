class DataManagement :

    def classifyByIdGroup(self,_list,_idGroup):
        '''리스트에서 해당 id값이 있는 값을 새로운 리스트로 분류

            args:
                _list : 전체 리스트(json)
                _idGroup : 그룹으로 묶일 id(int)를 element로 가진 리스트들의 묶음(리스트) ex) ((1,2,3),(4,5))
            return:
                new_list : _list에서 추출한 target id의 리스트
        '''
        new_list =list()
        for item in _list:
            if int(item['id']) in _idGroup:
                new_list.append(item)
        return new_list

    def classifyGroup(self,_list,_idGroup): 
        '''요건에 맞게 해당 번호(id)끼리 묶어서 그룹으로 묶어주는 함수 + 동적으로 리스트 생성

            args:
                _list : 전체 리스트(json)
                _idGroup : 그룹으로 묶일 id(int)를 element로 가진 리스트들의 묶음(리스트) ex) ((1,2,3),(4,5))       
            return:
                groupList : _list에서 _idGroup끼리 따로 묶인 리스트
        '''
        groupList = list() # 전역변수 초기화
        for group in _idGroup:
            groupList.append(self.classifyByIdGroup(_list,group))
        return groupList

    def extractRecentData(self,_list,_count:int):
        '''데이터 추출
        
            args:
                _list : 전체리스트(json)
                _count : id별로 뽑아낼 데이터의 수(int)
            return:
                returnList : 각 id별로 _count별로 추출된 리스트
        '''
        returnList = list()
        idGroup = list()
        for dictItem in _list:
            idGroup.append(dictItem['id'])      
        set(idGroup)
        idCount = dict()
        for id in idGroup:
            idCount[id] = _count
        for dictItem in reversed(_list): #최신순으로 보기위해서 역순으로 뒤집는다. (원본데이터 손실은 방지)
            if idCount[dictItem['id']] != 0 :
                returnList.insert(0,dictItem) # 시간순을 위해 append가 아닌 insert로 함.
                idCount[dictItem['id']] -= 1
                if idCount[dictItem['id']] == 0: # 특정 id의 count가 0이 되는 순간 다른 id의 카운트도 확인하여 모두 0이면 for문을 멈추도록 함.
                    for value in idCount:
                        breakFlag = True
                        if value != 0 :
                            breakFlag = False
                    if breakFlag == True:
                        break
        
        return returnList
        

            


if __name__ =='__main__':
    management = DataManagement()
    a_list = [[1,2,3],[4,5,6]]
    tempJson = {
                "id": 1,
                "value" : 10
            }
    allList = list()
    allList.append(tempJson)
    allList.append(tempJson)
    allList.append(tempJson)
    tempJson = {
            "id": 4,
            "value" : 15
        }
    allList.append(tempJson)
    allList.append(tempJson)
    print(management.classifyGroup(allList,a_list))
    print('test')
    print(management.extractRecentData(allList,2))
    #print(management.cutoutMax(3,[0,2,3,4,5,6]))




