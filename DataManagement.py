class DataManagement :
    __groupList__ = list()

    def classificationByIdGroup(self,_list,_idGroup):
        '''리스트에서 해당 id값이 있는 값을 새로운 리스트로 분류
            args:
                _list : 전체 리스트(json)
                _idGroup : target idGroup
            return:
                new_list : _list에서 추출한 target id의 리스트
        '''
        new_list =list()
        for item in _list:
            if item['id'] in _idGroup:
                new_list.append(item)
        return new_list

    def setGroup(self,_list,_idGroup): 
        '''요건에 맞게 해당 번호(id)끼리 묶어서 그룹으로 묶어주는 함수 + 동적으로 리스트 생성
            args:
                _list =그룹으로 묶일 id(int)를 element로 가진 리스트들의 묶음(리스트) ex) ((1,2,3),(4,5))
        '''
        self.__groupList__ = list() # 전역변수 초기화
        for group in _idGroup:
            self.__groupList__.append(self.classificationByIdGroup(_list,group))

    def getGroup(self):
        '''
        현재 저장된 groupList 리턴
        '''
        tempList = self.__groupList__
        return tempList            
    
    def cutoutMax(self,_count,_list):
        '''
        count에 맞게 최신순으로 배열을 잘라서 리턴, count보다 작으면 그대로 리턴
        '''
        if len(_list) > _count:
            return _list[-_count:]
        else :
            return _list
    


if __name__ =='__main__':
    management = DataManagement()
    a_list = [[1,2,3],[4,5,6]]
    tempJson = {
                "id": 1,
                "value" : 10
            }
    allList = list()
    allList.append(tempJson)
    tempJson = {
            "id": 4,
            "value" : 15
        }
    allList.append(tempJson)
    management.setGroup(allList,a_list)
    print(management.getGroup())
    #print(management.cutoutMax(3,[0,2,3,4,5,6]))




