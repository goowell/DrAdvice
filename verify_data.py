from transformer import *


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

    for d in collection.find():
        if len(d.get('d').get('doctor_advice')) == 0:
            print('invalid doctor advice:' + d['_id'])
        else:
            one_p = split_all_ad(d)
            print(one_p)
        break


def main():
    'main entry'
    from datetime import datetime

    start = datetime.now()
    print('hello..')

    client = MongoClient('192.168.4.12')
    collection = client.xinhuahos.paients
    verify_data(collection)
    # get_info(collection)

    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()