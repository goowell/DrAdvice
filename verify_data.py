from transformer import *
from logger import logger

def find_missing():
    from db import paients_source, paients_info
    import re
    for pi in paients_info.find():
        if paients_source.find({'_id': re.compile(pi['住院号'], re.IGNORECASE)}).count()>0:
            pass
        else:
            print(pi['住院号'])

def verify_data(collection):
    'verify the data format is correct or not.'
    for d in collection.find():
        info = d.get('d').get('info')
        if len(info) <12 and info[0] != '1':
            logger.error('invalid patient info:' + d['_id']+str(info))
        if len(d.get('d').get('doctor_advice')) == 0:
            logger.error('invalid doctor advice:' + d['_id'])
        else:
            has_long = False
            has_short = False
            for a in d.get('d').get('doctor_advice'):
                if len(a) != 18:
                    logger.error('invalid doctor advice:' + d['_id'])
                    logger.error("invalid doctor advice: " + a)
                if a[3] == '长':
                    has_long = True
                else:
                    has_short = True
            if not (has_long and has_short):
                logger.error('invalid doctor advice: ' + d['_id'] + ', long/short: {}/{}'.format(has_long, has_short) )
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
    from db import paients_source


    start = datetime.now()
    print('hello..')

    # verify_data(paients_source)
    # get_info(collection)
    find_missing()


    print(datetime.now() - start)


if __name__ == '__main__':
    main()