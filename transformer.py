from datetime import datetime, timedelta
from judge import get
from logger import logger
from setting import nu_per_ml
from db import paients_source, paients_splited, paients_merged, paients_calculated
_get = get()

def split_all_ad(one_child):
    one_p_nutrition = []
    one_p_weight = []
    for a in one_child.get('d').get('doctor_advice'):
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
    if dict_ad['et']:
        et = str2date(dict_ad['et'])
        while st <= et:
            ads.append({
                'd': date2str(st),
                't': dict_ad['t'],
                'wt': dict_ad['wt'],
                'en': dict_ad['en'],
                'v': dict_ad['total']
            })
            st = st + timedelta(days=1)

    else:
        ads.append({
            'd': date2str(st),
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
    for p in paients_source.find():
        splited = {
            '_id': p['_id'],
            'info': p['d']['info']
            }
        splited.update(split_all_ad(p))
        paients_splited.save(splited)

def merge():
    for p in paients_splited.find():
        nu = p['nu']
        merged = []

        nu.sort(key=lambda x:x['d']+x['t']+str(x['en'])+str(x['wt']))
        for n in nu:
            if merged != [] and _is_same_nu(merged[-1], n):
                merged[-1]['v'] += n['v']
            else:
                merged.append(n)
        p['nu'] = merged
        paients_merged.save(p)
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
    merge()
    cal_en()
    logger.info('done')


if __name__ == '__main__':
    main()
