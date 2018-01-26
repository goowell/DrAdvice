from db import paients_calculated
from logger import logger
from datetime import datetime
from setting import invalid

def main():
    'main entry'
    start = datetime.now()
    logger.info('hello..')
    paients = paients_calculated.find().sort('_id')
    group = {}
    for p in paients:
        if p['_id'] in invalid:
            continue
        if len(p['info'])==13:
            p['info'].append(p['info'][2])
            p['info'].remove(p['info'][2])
        # print(p)
        # print(p['info'])
        d = p['info'][7][0:7]
        if d=='':
            print(p['info'])
            continue
        if d in group.keys():
            group[d].append(p)
        else:
            group.update({d:[p]})

    for k in group:
        print(k)   
        toCsv(k+'.csv',group[k])
    print('Elapsed time: ', datetime.now() - start)

def toCsv(file_name, paients):
    f = open(file_name,mode='w')
    header = '序号,姓名,住院号,入科年龄,入科日期,入科天数,日期,体重,EN,PN,其他\n'
    p_info = '{0},{1},{2},{3},{4},,,,,,{5}\n'
    daily_info = ',,,,,{0},{1},{2},{3},{4},\n'
    counter = 1
    f.write(header)
    for p in paients:   
        info= p_info.format(counter,p['info'][2],p['_id'],p['info'][5],p['info'][7],'#'.join(p['info']))
        f.write(info)
        nu_counter = 0
        len_nu = len(p['nu'])
        while nu_counter < len_nu:
            nu = p['nu'][nu_counter]
            date_nu = nu['d']
            en_nu,pn_nu = 0,0

            if nu['en']:
                en_nu = nu['v']
            else:
                pn_nu = nu['v']
            if (nu_counter < len_nu - 1):
                next_nu = p['nu'][nu_counter+1]
                if next_nu['d'] == date_nu:
                    if next_nu['en']:
                        en_nu = next_nu['v']
                    else:
                        pn_nu = next_nu['v']
                    nu_counter += 1
            nu_counter += 1
            wight = _get_wight(p, date_nu)

            one_nu = daily_info.format(_total_days(p, date_nu), date_nu,wight,en_nu,pn_nu)
            f.write(one_nu)
        counter += 1
    f.close()
def _get_wight(p, date_nu):
    wight = 0
    for w in p['wt']:
        if date_nu > w['st']:
            wight = w['w']
        else:
            break
    return wight

def _total_days(p, date_nu):
    return (datetime.strptime(date_nu,'%Y-%m-%d')-datetime.strptime(p['info'][7].split(' ')[0],'%Y-%m-%d')).days
    

if __name__ == '__main__':
    main()