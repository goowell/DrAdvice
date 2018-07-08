from db import paients_calculated,paients_merged,paients_info
from logger import logger
from datetime import datetime
from setting import names, nu_per_ml,protein_per_ml, weight_dict
from pygrowup import Calculator, helpers
import re
import csv
import os
 

_0=0

def main():
    'main entry'
    start = datetime.now()
    logger.info('hello..')
    # nu2csv() 
    # raw2csv()
    # summary2csv()
    summary2csv(True)
    print('Elapsed time: ', datetime.now() - start)

def nu2csv():
    paients = paients_calculated.find().sort('_id')
    group = _groupBySt(paients)

    for k in group:
        print(k)   
        _nu2csv(k+'.csv',group[k])

def _nu2csv(file_name, paients):
    f = open(file_name,mode='w',encoding='gbk')
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
            wight = _get_weight(p, date_nu)
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

def summary2csv(one_file=False):
    paients = paients_merged.find().sort('_id')
    group = _groupBySt(paients)
    if one_file and os.path.isfile('All_avg.csv'):
        os.remove('All_avg.csv')

    for k in group:
        if one_file:
            _summary2csv('All_avg.csv',group[k],one_file=one_file)
        else:
            _summary2csv(k+'_avg.csv',group[k])

def _summary2csv(file_name, paients, one_file=False):
    calculator = Calculator(adjust_height_data=False, adjust_weight_scores=False,
                    include_cdc=False, logger_name='pygrowup',
                    log_level='INFO')
    new_file = not os.path.isfile(file_name)

    open_mode = 'a' if one_file else 'w'
    ff=open(file_name,mode=open_mode, newline='',encoding='utf8')
    f = csv.writer(ff)
    header = '序号,姓名,性别,年龄,住院号,出生日期,胎龄,出生体重,Aparg评分,既往手术次数,既往手术名称,入科诊断,出科主要诊断,其他诊断,入科日期,出科日期,住科天数,本次手术日期,本次手术名称,转出,出院,死亡,EN-avg,PN-avg,氨基酸(EN+PN)-avg,出科Z值,入科Z值'
    # p_info = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'
    # daily_info = ',,,,,{0},{1},{2},,,,{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17}\n'
    daily_info = ',,,,,{},{},{},{},{},{},,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'
    counter = 1
    if new_file:
        f.writerow(header.split(','))
    for p in paients:
        src_info = paients_info.find_one({'住院号': re.compile(p['_id'], re.IGNORECASE)})
        # print(p['_id'])
        ignor_this, checkin_date, checkout_date = _is_ignor(src_info, p)
        if ignor_this:
            continue

        nu_counter = 0
        p['nu'].sort(key=lambda x: x['d'])
        len_nu = len(p['nu'])
        en_avg = 0
        pn_avg = 0
        protein_avg = 0
        weight = 0
        checkin_weight = 0
        checkout_weight = 0
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
            if date_nu < checkin_date:
                continue
            if date_nu > checkout_date:
                break
            weight,en,pn,protein = _write_one_record(p, date_nu, daily_info, v_en_dict, v_pn_dict, f, checkin_date,False)
            if weight==0:
                break
            if checkin_weight==0:
                checkin_weight = weight
            en_avg+=en/weight
            pn_avg+=pn/weight
            protein_avg+=protein/weight
        if weight==0:
            continue
        checkout_weight = weight
        total_days = _total_days(checkin_date,checkout_date)
        en_avg=en_avg/total_days
        pn_avg=pn_avg/total_days
        protein_avg=protein_avg/total_days

        born_date = src_info['出生日期'][:10]
        if born_date == '':
            checkin_z = '出生日期未知'
            checkout_z = '出生日期未知'

        else:
            months_in = _total_months(born_date,checkin_date)
            months_out = _total_months(born_date,checkout_date)
            gender = 'M' if src_info['女']!=1 else 'F'
            checkin_z = calculator.wfa(checkin_weight, months_in, gender)
            logger.info(','.join([str(checkin_weight), str(months_in), gender,str(checkin_z)]))
            checkout_z = calculator.wfa(checkout_weight, months_out, gender)
            logger.info(','.join([str(checkout_weight), str(months_out), gender,str(checkout_z)]))
        info= [counter,src_info['姓名'],'男' if src_info['女']!=1 else '女',src_info.get('年龄',src_info.get('入科年龄')),src_info['住院号'],born_date,src_info['胎龄'],src_info['出生体重'],'\''+str(src_info['Aparg评分']),src_info['既往手术次数'],src_info['既往手术名称'],src_info.get('入科诊断'),src_info['出科主要诊断'],src_info['其他诊断'],src_info['入科日期'][:10],src_info['出科日期'][:10],src_info.get('住科天数',src_info.get('住院天数')),src_info.get('本次手术日期','')[:10],src_info.get('本次手术名称', src_info.get('本次手术名称')),src_info.get('好转',src_info.get('转出')),src_info['出院'],src_info['死亡'],en_avg,pn_avg,protein_avg,checkin_z,checkout_z]
        f.writerow(info)
        if checkout_weight > 15:
            logger.info('weightxx:  '+weight)
        counter += 1

def _is_ignor(src_info, p):
    checkin_date = p['info'][7].split(' ')[0]
    checkout_date = p['info'][8].split(' ')[0]
    ignor_this = False
    try:
        if not src_info:
            logger.warn('cannot find info from source: ' + p['_id'])
            ignor_this = True
            return ignor_this, checkin_date, checkout_date
        else:
            checkin_date = src_info['入科日期'][:10]
            checkout_date = src_info['出科日期'][:10]

        if checkin_date=='' or checkout_date=='':
            logger.error('checkin_date or checkin_date is null: '+checkin_date+'&'+checkout_date)
            ignor_this = True
            return ignor_this, checkin_date, checkout_date

        if _total_days(checkin_date,checkout_date) <= 3:
            logger.info('total days less than 3: ' + p['_id'])
            ignor_this = True
    except Exception as identifier:
        logger.error(p['_id']+': '+str(identifier))
        ignor_this = True  

    return ignor_this, checkin_date, checkout_date

def _groupBySt(paients):
    group = {}
    for p in paients:
        src_info = paients_info.find_one({'住院号': re.compile(p['_id'], re.IGNORECASE)})
        if len(p['info'])==13:
            p['info'].append(p['info'][2])
            p['info'].remove(p['info'][2])
        d = src_info['入科日期'][0:7] if src_info else p['info'][7][0:7]
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
        src_info = paients_info.find_one({'住院号': re.compile(p['_id'], re.IGNORECASE)})
        ignor_this, checkin_date, checkout_date = _is_ignor(src_info, p)
        if ignor_this:
            continue
            

        info= p_info.format(counter,p['info'][2],p['_id'],p['info'][5],checkin_date,'#'.join(p['info']))
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
            if date_nu < checkin_date:
                continue
            if date_nu > checkout_date:
                break
            _write_one_record(p, date_nu, daily_info, v_en_dict, v_pn_dict, f, checkin_date)

        counter += 1
    f.close()

def _write_one_record(p, date_nu, daily_info, v_en_dict, v_pn_dict, f, checkin_date, write=True):
    wight = _get_weight(p, date_nu)
    en = v_en_dict.get(names.nkt,_0)*nu_per_ml[names.nkt]+ v_en_dict.get(names.ntt,_0)*nu_per_ml[names.ntt]+ v_en_dict.get(names.mrtn,_0)*nu_per_ml[names.mrtn]+ v_en_dict.get(names.aes,_0)*nu_per_ml[names.aes]+ v_en_dict.get(names.mr,_0)*nu_per_ml[names.mr]+ v_en_dict.get(names.yn,_0)*nu_per_ml[names.yn]+ v_en_dict.get(names.zn,_0)*nu_per_ml[names.zn]+ v_en_dict.get(names.pfn,_0)*nu_per_ml[names.pfn]+ v_en_dict.get(names.xbt,_0)*nu_per_ml[names.xbt]+ v_en_dict.get(names.ptt,_0)*nu_per_ml[names.ptt]+ v_en_dict.get(names.ajs,_0)*nu_per_ml[names.ajs]
    pn = v_pn_dict.get(names.zcl,_0)*nu_per_ml[names.zcl]+ v_pn_dict.get(names.yy,_0)*nu_per_ml[names.yy]+ v_pn_dict.get(names.ptt,_0)*nu_per_ml[names.ptt]+ v_pn_dict.get(names.ajs,_0)*nu_per_ml[names.ajs]
    protein = v_en_dict.get(names.nkt,_0)*protein_per_ml[names.nkt]+ v_en_dict.get(names.ntt,_0)*protein_per_ml[names.ntt]+ v_en_dict.get(names.mrtn,_0)*protein_per_ml[names.mrtn]+ v_en_dict.get(names.aes,_0)*protein_per_ml[names.aes]+ v_en_dict.get(names.mr,_0)*protein_per_ml[names.mr]+ v_en_dict.get(names.yn,_0)*protein_per_ml[names.yn]+ v_en_dict.get(names.zn,_0)*protein_per_ml[names.zn]+ v_en_dict.get(names.pfn,_0)*protein_per_ml[names.pfn]+ v_en_dict.get(names.xbt,_0)*protein_per_ml[names.xbt]+ v_en_dict.get(names.ptt,_0)*protein_per_ml[names.ptt]+ v_en_dict.get(names.ajs,_0)*protein_per_ml[names.ajs]+ v_pn_dict.get(names.ajs,_0)

    one_nu = daily_info.format(_total_days(checkin_date, date_nu), date_nu,wight,
    en,
    pn,

    protein,

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
    if write:
        f.write(one_nu)
    return wight,en,pn,protein

def _get_weight(p, date_nu):

    weight = 0
    for w in p['wt']:
        if date_nu > w['st']:
            weight = w['w']
        else:
            if weight==0:
                weight = w['w']
            break
    if weight==0:
        weight = weight_dict.get(p['_id'].upper(),0)
    return weight

def _total_days(start, end):
    return (datetime.strptime(end,'%Y-%m-%d')-datetime.strptime(start,'%Y-%m-%d')).days+1
def _total_months(start, end):
    return ((datetime.strptime(end,'%Y-%m-%d')-datetime.strptime(start,'%Y-%m-%d')).days+1)/30.4375
    

if __name__ == '__main__':
    main()