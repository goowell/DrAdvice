from pymongo import MongoClient

def main():
    from datetime import datetime

    start = datetime.now()
    print('hello..')

    client = MongoClient('192.168.2.110')
    collection = client.xinhuahos.paients

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
    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()