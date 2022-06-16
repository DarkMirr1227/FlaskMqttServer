class DataManagement :
    __groupList__ = list()

    def classificationById(self,_list,_id):
        '''리스트에서 해당 id값만 있는 값을 새로운 리스트로 분류
            args:
                _list : 전체 리스트(json)
                _id : target id
            return:
                new_list : _list에서 추출한 target id의 리스트
        '''
        new_list =list()
        for item in _list:
            if item['id']==_id:
                new_list.append(item)
        return new_list

    def setGroup(self,_list): 
        '''요건에 맞게 해당 번호(id)끼리 묶어서 그룹으로 묶어주는 함수 + 동적으로 리스트 생성
            args:
                _list =그룹으로 묶일 id(int)를 element로 가진 리스트들의 묶음(리스트) ex) ((1,2,3),(4,5))
        '''
        __groupList__ = list() # 전역변수 초기화
        for group in _list:
            tempGroup = list()
            for item in group:
                tempGroup.append(self.classficationById(item))
            __groupList__.append(tempGroup)
                






