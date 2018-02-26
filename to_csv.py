from db import paients_calculated,paients_merged
from logger import logger
from datetime import datetime
from setting import names, nu_per_ml,protein_per_ml

_0=0

def main():
    'main entry'
    start = datetime.now()
    logger.info('hello..')
    # nu2csv()
    raw2csv()
    print('Elapsed time: ', datetime.now() - start)

def nu2csv():
    paients = paients_calculated.find().sort('_id')
    group = _groupBySt(paients)

    for k in group:
        print(k)   
        _nu2csv(k+'.csv',group[k])

def _nu2csv(file_name, paients):
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
def raw2csv():
    paients = paients_merged.find().sort('_id')
    group = _groupBySt(paients)

    for k in group:
        print(k)   
        _raw2csv(k+'_raw.csv',group[k])

def _groupBySt(paients):
    group = {}
    for p in paients:
        if len(p['info'])==13:
            p['info'].append(p['info'][2])
            p['info'].remove(p['info'][2])
        d = p['info'][7][0:7]
        if d=='':
            print(p['info'])
            continue
        if d in group.keys():
            group[d].append(p)
        else:
            group.update({d:[p]})
    return group

def _raw2csv(file_name, paients):
    f = open(file_name,mode='w')
    header = '序号,姓名,住院号,入科年龄,入科日期,入科天数,日期,体重,EN,PN,氨基酸(EN+PN),其他,纽康特,纽太特,免乳糖奶,蔼尔舒,母乳,婴奶,早奶,配方奶,小百肽,葡萄糖,氨基酸,中长链脂肪乳pn,鱼油脂肪乳pn(g),葡萄糖pn,氨基酸pn(g)\n'
    p_info = '{0},{1},{2},{3},{4},,,,,,,{5}\n'
    # daily_info = ',,,,,{0},{1},{2},,,,{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17}\n'
    daily_info = ',,,,,{},{},{},{},{},{},,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'
    counter = 1
    f.write(header)
    for p in paients:   
        info= p_info.format(counter,p['info'][2],p['_id'],p['info'][5],p['info'][7],'#'.join(p['info']))
        f.write(info)
        nu_counter = 0
        p['nu'].sort(key=lambda x: x['d'])
        len_nu = len(p['nu'])
        while nu_counter < len_nu: #write info day by day
            v_en_dict={}
            v_pn_dict={}
            nu = p['nu'][nu_counter]
            date_nu = nu['d']
            if nu['en']:    #first
                v_en_dict.update({nu['t']:nu['v']*nu['wt']})
            else:
                v_pn_dict.update({nu['t']:nu['v']*nu['wt']})

            while (nu_counter < len_nu - 1) and p['nu'][nu_counter+1]['d'] == date_nu:    #the next with same date
                next_nu = p['nu'][nu_counter+1]
                if next_nu['en']:
                    v_en_dict.update({next_nu['t']:next_nu['v']*next_nu['wt'] + v_en_dict.get(next_nu['t'],0)})
                else:
                    v_pn_dict.update({next_nu['t']:next_nu['v']*next_nu['wt']+v_pn_dict.get(next_nu['t'],0)})
                nu_counter += 1
            nu_counter += 1

            wight = _get_wight(p, date_nu)
            one_nu = daily_info.format(_total_days(p, date_nu), date_nu,wight,
            v_en_dict.get(names.nkt,_0)*nu_per_ml[names.nkt]+
            v_en_dict.get(names.ntt,_0)*nu_per_ml[names.ntt]+
            v_en_dict.get(names.mrtn,_0)*nu_per_ml[names.mrtn]+
            v_en_dict.get(names.aes,_0)*nu_per_ml[names.aes]+
            v_en_dict.get(names.mr,_0)*nu_per_ml[names.mr]+
            v_en_dict.get(names.yn,_0)*nu_per_ml[names.yn]+
            v_en_dict.get(names.zn,_0)*nu_per_ml[names.zn]+
            v_en_dict.get(names.pfn,_0)*nu_per_ml[names.pfn]+
            v_en_dict.get(names.xbt,_0)*nu_per_ml[names.xbt]+
            v_en_dict.get(names.ptt,_0)*nu_per_ml[names.ptt]+
            v_en_dict.get(names.ajs,_0)*nu_per_ml[names.ajs],
            v_pn_dict.get(names.zcl,_0)*nu_per_ml[names.zcl]+
            v_pn_dict.get(names.yy,_0)*nu_per_ml[names.yy]+
            v_pn_dict.get(names.ptt,_0)*nu_per_ml[names.ptt]+
            v_pn_dict.get(names.ajs,_0)*nu_per_ml[names.ajs],

            v_en_dict.get(names.nkt,_0)*protein_per_ml[names.nkt]+
            v_en_dict.get(names.ntt,_0)*protein_per_ml[names.ntt]+
            v_en_dict.get(names.mrtn,_0)*protein_per_ml[names.mrtn]+
            v_en_dict.get(names.aes,_0)*protein_per_ml[names.aes]+
            v_en_dict.get(names.mr,_0)*protein_per_ml[names.mr]+
            v_en_dict.get(names.yn,_0)*protein_per_ml[names.yn]+
            v_en_dict.get(names.zn,_0)*protein_per_ml[names.zn]+
            v_en_dict.get(names.pfn,_0)*protein_per_ml[names.pfn]+
            v_en_dict.get(names.xbt,_0)*protein_per_ml[names.xbt]+
            v_en_dict.get(names.ptt,_0)*protein_per_ml[names.ptt]+
            v_en_dict.get(names.ajs,_0)*protein_per_ml[names.ajs]+
            v_pn_dict.get(names.ajs,_0),
            
            v_en_dict.get(names.nkt,_0),
            v_en_dict.get(names.ntt,_0),
            v_en_dict.get(names.mrtn,_0),
            v_en_dict.get(names.aes,_0),
            v_en_dict.get(names.mr,_0),
            v_en_dict.get(names.yn,_0),
            v_en_dict.get(names.zn,_0),
            v_en_dict.get(names.pfn,_0),
            v_en_dict.get(names.xbt,_0),
            v_en_dict.get(names.ptt,_0),
            v_en_dict.get(names.ajs,_0),
            v_pn_dict.get(names.zcl,_0),
            v_pn_dict.get(names.yy,_0),
            v_pn_dict.get(names.ptt,_0),
            v_pn_dict.get(names.ajs,_0)
            )
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