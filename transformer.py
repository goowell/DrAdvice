from datetime import datetime, timedelta
from judge import get
from logger import logger
from setting import nu_per_ml,names
from db import paients_source, paients_splited, paients_merged, paients_calculated,paients_pn,paients_splited_with_excel
_get = get()

def split_all_ad(one_child):
    one_p_nutrition = []
    one_p_weight = []
    for a in one_child.get('d').get('doctor_advice'):
        # print(a)
        da = _get.dict(a)
        if da and da.get('t'):
            one_p_nutrition.extend(_split_ad(da))
        elif da and da.get('w'):
            one_p_weight.append(da)
    return {'nu':one_p_nutrition, 'wt': one_p_weight}


def _split_ad(dict_ad):
    '''
    input: {'total': 60.0, 'et': '2014-11-07 12:45', 'st': '2014-11-05 14:06', 'en': False, 't': '葡萄糖'}
    output: [
        {'v': 60.0, 'en': False, 'd': '2014-11-05', 't': '葡萄糖'}, 
        {'v': 60.0, 'en': False, 'd': '2014-11-06', 't': '葡萄糖'}
        ]
    '''
    ads = []
    st = str2date(dict_ad['st'])
    temp_date = st
    firstDay=True
    if dict_ad['et']:
        et = str2date(dict_ad['et'])
        tbd = dict_ad['tbd']
        while temp_date.date() <= et.date():
            
            if firstDay:
                ratio = int((tbd*(24-temp_date.hour))/24)/tbd if tbd>1.01 else 1
            elif temp_date.date() == et.date() and tbd>=1:
                ratio = int(tbd*(et.hour)/24)/tbd
            else:
                temp_r = tbd*(temp_date-st).days
                ratio = 1 if (tbd>=0.99 or (temp_r-int(temp_r))<tbd) else 0
            if ratio==0:
                temp_date = temp_date + timedelta(days=1)
                firstDay=False
                continue
            ads.append({
                'd': date2str(temp_date),
                't': dict_ad['t'],
                'wt': dict_ad['wt'],
                'en': dict_ad['en'],
                'v': int(dict_ad['total']*ratio)
            })
            temp_date = temp_date + timedelta(days=1)
            firstDay=False

    else:
        ads.append({
            'd': date2str(temp_date),
            'en': dict_ad['en'],
            'wt': dict_ad['wt'],
            't': dict_ad['t'],
            'v': dict_ad['total']
        })
    return ads

def dict_collect(list_d):
    res = []
    for d in list_d:
        res.extend(d)
    return res


def str2date(str_d):
    return datetime.strptime(str_d, '%Y-%m-%d %H:%M')
def date2str(date_d):
    return date_d.strftime('%Y-%m-%d')

def split():
    '''
    parse single advice to dict
    '''
    paients_splited.remove
    for p in paients_source.find():

        splited = {
            '_id': p['_id'],
            'info': p['d']['info']
            }
        splited.update(split_all_ad(p))
        paients_splited.save(splited)

def merge():
    '''
    merge long and term advice by date
    '''
    paients_merged.remove()
    for p in paients_splited_with_excel.find():
        nu = p['nu']
        merged = []

        nu.sort(key=lambda x:x['d']+x['t']+str(x['en'])+str(x['wt']))
        for n in nu:
            if merged != [] and _is_same_nu(merged[-1], n):
                merged[-1]['v'] += n['v']
            else:
                merged.append(n)
        p['nu'] = merged
        paients_merged.insert_one(p)

def cal_en():
    for p in paients_merged.find():
        nu = p['nu']
        cal = []

        nu.sort(key=lambda x:x['d']+x['t']+str(x['en'])+str(x['wt']))
        for n in nu:
            if cal != [] and _is_same_day(cal[-1], n):
                cal[-1]['v'] += n['v'] * n['wt'] * nu_per_ml[n['t']]
            else:
                cal.append(n)
        for c in cal:
            c.pop('t')
            c.pop('wt')
        p['nu'] = cal
        paients_calculated.save(p)
def _is_same_day(d1, d2):
    return d1['d'] == d2['d'] and d1['en'] == d2['en']

def _is_same_nu(d1, d2):
    return d1['d']==d2['d'] and d1['t'] == d2['t'] and d1['wt']==d2['wt'] and d1['en'] == d2['en']
def _split_excel_pn(excel_pn):
    '''
    excel_pn=[
        {
            "10%GS" : 0,
            "脂肪乳" : 0,
            "date" : "2014-10-02",
            "25%GS" : 0,
            "6%AA" : 0
        }, 
    ]
    '''
    pn=[]
    for e_pn in excel_pn:
        if e_pn[r"10%GS"]>0:
            pn.append({
            "t" : names.ptt,
            "v" : e_pn[r"10%GS"],
            "d" : e_pn[r"date"],
            "en" : False,
            "wt" : 0.1
        })
        if e_pn[r"25%GS"]>0:
            pn.append({
            "t" : names.ptt,
            "v" : e_pn[r"25%GS"],
            "d" : e_pn[r"date"],
            "en" : False,
            "wt" : 0.25
        })
        if e_pn[r"6%AA"]>0:
            pn.append({
            "t" : names.ajs,
            "v" : e_pn[r"6%AA"],
            "d" : e_pn[r"date"],
            "en" : False,
            "wt" : 0.06
        })
        if e_pn[r"脂肪乳"]>0:
            pn.append({
            "t" : names.yy,
            "v" : e_pn[r"脂肪乳"]*0.1,
            "d" : e_pn[r"date"],
            "en" : False,
            "wt" : 1
        })
    return pn
def combine_splited_and_excel():
    paients_splited_with_excel.remove()
    for one_nu in paients_splited.find():
        items = paients_pn.find({'sn':one_nu.get('_id')})
        for item in items:
            one_nu['nu'].extend(_split_excel_pn(item['pn']))
        paients_splited_with_excel.insert_one(one_nu)

def main():
    logger.info('start')
    test_case = [
        {'total': 100.0, 'et': '2015-05-13 15:27', 'st': '2015-05-04 15:42', 'en': False, 't': '葡萄糖'},
        {'total': 250.0, 'et': '', 'st': '2015-05-07 08:52', 'en': False, 't': '葡萄糖'},
        {'total': 100.0, 'et': '', 'st': '2015-05-07 08:52', 'en': False, 't': '葡萄糖'},
        {'total': 100.0, 'et': '2015-05-13 15:27', 'st': '2015-05-11 08:59', 'en': False, 't': '葡萄糖'}
    ]
    # for t in test_case:
    #     print(split_ad(t))
    # print()
    # split()
    combine_splited_and_excel()
    merge()
    # cal_en()
    logger.info('done')


if __name__ == '__main__':
    main()
#     info = [ 
#     "1", 
#     "儿外科", 
#     "儿外二病区", 
#     "徐秋叶之子", 
#     "男", 
#     "D77770", 
#     "33", 
#     "", 
#     "2017-04-25 18:04", 
#     "2017-05-15 13:48", 
#     "先天性肛门缺如、闭锁和狭窄，伴瘘", 
#     "申请归档(自动)", 
#     "查看详情"
# ]
#     print(len(info))
#     # info[2]=None
#     info.append(info[2])
#     info.remove(info[2])
#     print(len(info))
#     print(info)