from logger import logger
from setting import names

def is_neocate(data):
    '纽康特'
    return names.nkt if '纽康特' in data[5] else None

def is_neotate(data):
    '纽太特'
    return names.ntt if ('纽太特' in data[5] or '纽肽特' in data[5]) else None

def is_lactoseFree(data):
    '免乳糖奶'
    return names.mrtn if '免乳' in data[5] else None

def is_alfare(data):
    '蔼尔舒'
    return names.aes if ('舒'in data[5] and ('蔼' in data[5] or '霭' in data[5])) else None

def is_breastFeeding(data):
    '母乳'
    return names.mr if '母乳' in data[5] else None

def is_yingnai(data):
    '婴奶'
    return names.yn if '婴' in data[5] else None

def is_pretermInfants(data):
    '早奶'
    return names.zn if '早' in data[5] and 'ml' in data[5] else None

def is_formula(data):
    '配方奶'
    return names.pfn if '配方' in data[5] else None

def is_peptide(data):
    '小百肽'
    return names.xbt if '小百肽' in data[5] else None

def is_midLong(data):
    '中长链脂肪乳'
    return names.zcl if '链脂肪乳' in data[5] and '静脉营养' in data[5] else None

def is_fishOil(data):
    '鱼油脂肪乳'
    return names.yy if '鱼油' in data[5] and '静脉营养' in data[5] else None

# def is_babysuger(data):
#     '糖水'
#     d = data[5].lower()
#     return names.ts if ('葡萄' in d or 'gs' in d.lower()) and ('抽胃液' not in d) and ('%' in d or '％' in d ) and ('tpn' not in d) and ('长期' not in d) and ('酸钙' not in d) and '静脉营养' in data[5] else None

def is_gluclose(data):
    '葡萄糖'
    d = data[5].lower()
    return names.ptt if ('葡萄' in d or 'gs' in d.lower()) and ('抽胃液' not in d) and ('%' in d or '％' in d ) and ('tpn' not in d) and ('长期' not in d) and ('酸钙' not in d) else None

def is_aminoAcid(data):
    '小儿复方氨基酸针'
    return names.ajs if '小儿复方氨基酸针' in data[5] else None

def is_weight(data):
    '体重'
    return '体重' in data[5] and ('测' not in data[5] and '称' not in data[5])

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

def is_en(data):
    la5 = data[5].lower()
    return '口服' in la5 or '鼻饲' in la5 or 'po' in la5 or '空肠' in la5 or '胃造瘘' in la5 or '胃管' in la5


is_nutritions = [is_alfare, is_breastFeeding, is_formula, is_gluclose, is_lactoseFree,
                 is_neocate, is_peptide, is_pretermInfants, is_yingnai, is_aminoAcid, 
                 is_neotate, is_midLong, is_fishOil]

def is_nutrition(data):
    for j in is_nutritions:
        if j(data):
            return j(data)
    return False


import re

class get(object):
    quantity_p = re.compile(r'(?P<q>\d+)\s*((ml)|(毫升)).*', flags=re.I)
    quantity_p2 = re.compile(r'(?P<q>\d+)(\s|m|g).*', flags=re.I)
    percent_p = re.compile(r'(?P<q>\d+)\s*(%|％).*', flags=re.I)
    times_p = re.compile(r'(q|(维持))(?P<q>\d+)(h|\s)', flags=re.I)
    times_p2 = re.compile(r'(\*|×|x)(?P<q>\d+)', flags=re.I)
    weight_p = re.compile(r'(?P<q>\d+\.?\d*).*', flags=re.I)

    def weight(self, src):
        str_src = src[5].lower()
        res = self.weight_p.search(str_src)
        if res:
            v = res.groupdict()['q']
            return float(v) if float(v)<70 else float(v)/1000
        logger.error('cannot get weight for: '+ str_src)
        return 0

    def quantity(self, src):
        str_src = src[5]
        res = self.quantity_p.search(str_src)
        if res:
            return int(res.groupdict()['q'])
        res = self.quantity_p2.search(str_src)
        if res:
            return int(res.groupdict()['q'])
        logger.error('cannot get quantity for: '+ str_src)
        return 0
    def percent(self, src):
        str_src = src[5]
        res = self.percent_p.search(str_src)
        if res:
            return int(res.groupdict()['q'])/100
        if is_en(src):
            return 0.05
        logger.error('cannot get percent for: '+ str_src)
        return 0
    def times(self, src):
        if '临' == src[3] or '后' in src[5]:
            return 1.0

        str_src = src[5].lower()
        if 'qd' in str_src:
            return 1.0
        if 'qn' in str_src:
            return 1.0
        if 'qw' in str_src:
            return 1/7
        if 'biw' in str_src:
            return 2/7
        if 'qh' in str_src:
            return 24.0
        if 'bid' in str_src:
            return 2.0
        if 'tid' in str_src:
            return 3.0
            
        res = self.times_p2.search(str_src)
        if res:
            return int(res.groupdict()['q'])
        else:
            res = self.times_p.search(str_src)
            if res:
                if '维持' in str_src and 'q' not in str_src and int(res.groupdict()['q'])==2:
                    return 8
                return 24/int(res.groupdict()['q'])
        if '维持' in str_src:
            return 1.0
        if self.quantity(src)>200:
            return 1.0
        logger.error('cannot get times for: '+ str_src+', use 1 as default.')
        return 1

    def type(self, src):
        if is_alfare(src):
            return names.aes
        if is_breastFeeding(src):
            return names.mr
        if is_gluclose(src):
            return names.ptt
        if is_lactoseFree(src):
            return names.mrtn
        if is_neocate(src):
            return names.nkt
        if is_neotate(src):
            return names.ntt
        if is_peptide(src):
            return names.xbt
        if is_pretermInfants(src):
            return names.zn
        if is_yingnai(src):
            return names.yn
        if is_formula(src):
            return names.pfn
        if is_aminoAcid(src):
            return names.ajs
        if is_midLong(src):
            return names.zcl
        if is_fishOil(src):
            return names.yy
        # if is_babysuger(src):
        #     return names.ts
        return None

    def start(self, src):
        return src[2]
    def stop(self, src):
        return src[9]
    def dict_wet(self, src):
        return {
            'st': self.start(src),
            'w': self.weight(src)
        }

    def dict_ad(self, src):
        '''
        input:['', '', '2015-09-25 15:30', '长', '药物', '5%葡萄糖针 10ml 静滴 q12h', '', '', '谭金童', '2015-10-10 11:07', '', '谢伟', '50ml*1包/瓶', '5%葡萄糖针', '', '已停止', '已执行', '林玲']
        return:{
            'st': '2015-09-25 15:30',
            'et': '2015-10-10 11:07',
            't': 葡萄糖,
            'wt': 0.05,
            'en': False,
            'total': 20,
            'tbd': 2
        }
        '''
        t = self.type(src)
        tbd = self.times(src)
        return {
            'st': self.start(src),
            'et': self.stop(src),
            't': t,
            'wt': self.percent(src) if t == names.ptt else 1,
            'en': t != names.ptt or is_en(src),
            'total': self.quantity(src) * tbd,
            'tbd': tbd
        }
    def dict(self, src):
        '''
        return 
            None
        or
            {'st': '2014-10-31 19:37', 'w': 7.0}
        or 
            {'total': 60.0, 'et': '2014-11-07 12:45', 'st': '2014-11-05 14:06', 'en': False, 't': '葡萄糖', 'tbd': 3}
        or
            {'total': 60.0, 'et': '', 'st': '2014-11-05 14:06', 'en': False, 't': '葡萄糖'}
        '''
        if is_weight(src):
            return self.dict_wet(src)
        la5 = src[5].lower()
        if  '''/h''' not in la5 and ('ml' in la5 or 'q' in la5 or '毫升' in la5) and is_executed(src):
            name = is_nutrition(src)
            if name:
                return self.dict_ad(src)
        return None


test_case = [
    '婴儿氨基酸型配方奶7mQ8H PO与糖水交替',
    '5％GS 5ml q3h po',
    '5%葡萄糖针 50ml 口服',
    '10%葡萄糖针 50ml 静滴 st',
    '5%葡萄糖针 42 ml 鼻饲',
    'ss29%ss555mlllll'
]
test_case_times = [
    '早奶 44ml×4次胃造瘘空肠管滴入(45分钟/次)',
    '蔼尔舒 53ml×8次胃造瘘空肠管滴入(60分钟/次)（97.3kcal/kg）'
]
test_parse_case=            [ 
                "", 
                "", 
                "2015-03-20 10:51", 
                "临", 
                "药物", 
                "◎小儿复方氨基酸针 60ml 静滴", 
                "", 
                "", 
                "xxx", 
                "2015-03-20 18:53", 
                "", 
                "xxx", 
                "100ml*1瓶/瓶", 
                "◎小儿复方氨基酸针(18AA-Ⅱ▲B", 
                "", 
                "已作废", 
                "已执行", 
                "xxx"
            ]


def main():
    _get = get()
    for t in test_case:
        print(_get.quantity_p2.search(t).group('q'))
        print(_get.percent_p.search(t).group('q'))
    for t in test_case_times:
        print(_get.times_p2.search(t).group('q'))
    print(_get.dict(test_parse_case))
if __name__ == '__main__':
    main()
