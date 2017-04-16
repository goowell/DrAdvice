from pymongo import MongoClient
from judge import *

test_case = [
    '5%葡萄糖针 50ml 口服',
    '10%葡萄糖针 50ml 静滴 st',
    '5%葡萄糖针 42 ml 鼻饲',
]

def verify_data(collection):
    'verify the data format is correct or not.'
    for d in collection.find():
        info = d.get('d').get('info')
        if len(info) != 12 and info[0] != '1':
            print('invalid patient info:' + d['_id'], len(info))
        if len(d.get('d').get('doctor_advice')) == 0:
            print('invalid doctor advice:' + d['_id'])
        else:
            for a in d.get('d').get('doctor_advice'):
                if len(a) != 18:
                    print("invalid doctor advice: " + a)
                
def get_info(collection):
    'count PE'
    count = 0
    count_gluclose = 0
    count_gluclose1 = 0
    is_nutritions = [is_alfare, is_breastFeeding, is_formula, is_gluclose, is_lactoseFree, is_neocate, is_peptide, is_pretermInfants, is_yingnai]
    _get = get()
    def is_nutrition(data):
        for j in is_nutritions:
            if j(data):
                return True
        return False
    for d in collection.find():
        if len(d.get('d').get('doctor_advice')) == 0:
            print('invalid doctor advice:' + d['_id'])
        else:
            for a in d.get('d').get('doctor_advice'):
                la5 = a[5].lower()
                if  '静滴' not in la5 and '''/h''' not in la5 and ('ml' in la5 or 'q' in la5):
                    count += 1
                    if  is_nutrition(a):
                        count_gluclose += 1 
                        if 'q' in la5:
                            print(la5)
                            print(_get.times(la5))
                    else:
                        # if '其他' == a[4]:
                            
                        # print(a[5])
                        pass
    print(count)
    print(count_gluclose)
    print(count_gluclose1)



def main():
    'main entry'
    from datetime import datetime

    start = datetime.now()
    print('hello..')

    client = MongoClient('172.22.25.48')
    collection = client.xinhuahos.paients
    # verify_data(collection)
    get_info(collection)

    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()