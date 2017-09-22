from db import paients_calculated
from logger import logger

def main():
    'main entry'
    from datetime import datetime
    start = datetime.now()
    logger.info('hello..')
    toCsv()

    print('Elapsed time: ', datetime.now() - start)

def toCsv():
    header = '序号,姓名,住院号,入科年龄,入科日期,入科天数,日期,体重,EN,PN,其他\n'
    p_info = '{0},{1},{2},{3},{4},,,,,,{5}\n'
    daily_info = ',,,,,{0},{1},{2},{3},{4},\n'
    counter = 1
    for p in paients_calculated.find():
        print(p)
        a= p_info.format(counter,p['info'][2],p['_id'],p['info'][5],p['info'][7],'#'.join(p['info']))
        
        print(a)
        counter += 1
        break

if __name__ == '__main__':
    main()