from pymongo import MongoClient
from judge import *

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

    for d in collection.find():
        if len(d.get('d').get('doctor_advice')) == 0:
            print('invalid doctor advice:' + d['_id'])
        else:
            for a in d.get('d').get('doctor_advice'):
                if  'q' in a[5]:
                    count += 1
                    if  is_alfare(a) or is_breastFeeding(a) or is_gluclose(a) or is_lactoseFree(a) or is_neocate(a) or is_pretermInfants(a) or is_yingnai(a):
                        count_gluclose += 1 
                        # print(a[5])
                    else:
                        if expression:
                            pass
                            print(a[5])
                        pass
    print(count)
    print(count_gluclose)
    print(count_gluclose1)



def main():
    'main entry'
    from datetime import datetime

    start = datetime.now()
    print('hello..')

    client = MongoClient('192.168.4.12')
    collection = client.xinhuahos.paients
    # verify_data(collection)
    get_info(collection)

    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()