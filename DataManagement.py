class DataManagement :
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
        
