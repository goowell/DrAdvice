from logger import logger
def is_neocate(data):
    '纽康特'
    return '纽康特' if '纽康特' in data[5] else None

def is_neotate(data):
    '纽太特'
    return '纽太特' if ('纽太特' in data[5] or '纽肽特' in data[5]) else None

def is_lactoseFree(data):
    '免乳糖奶'
    return '免乳糖奶' if '免乳' in data[5] else None

def is_alfare(data):
    '蔼尔舒'
    return '蔼尔舒' if ('舒'in data[5] and ('蔼' in data[5] or '霭' in data[5])) else None

def is_breastFeeding(data):
    '母乳'
    return '母乳' if '母乳' in data[5] else None

def is_yingnai(data):
    '婴奶'
    return '婴奶' if '婴' in data[5] else None

def is_pretermInfants(data):
    '早奶'
    return '早奶' if '早' in data[5] and 'ml' in data[5] else None

def is_formula(data):
    '配方奶'
    return '配方奶' if '配方' in data[5] else None

def is_peptide(data):
    '小百肽'
    return '小百肽' if '小百肽' in data[5] else None

def is_gluclose(data):
    '葡萄糖'
    d = data[5].lower()
    return '葡萄糖' if ('葡萄' in d or 'gs' in d.lower()) and ('抽胃液' not in d) and ('%' in d or '％' in d ) and ('tpn' not in d) and ('长期' not in d) and ('酸钙' not in d) else None

def is_weight(data):
    '体重'
    return '体重' in data[5] and ('测' not in data[5] and '称' not in data[5])

def is_aminoAcid(data):
    '小儿复方氨基酸针'
    return '小儿复方氨基酸针' in data[5]

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

def is_en(data):
    la5 = data[5].lower()
    return '口服' in la5 or '鼻饲' in la5 or 'po' in la5 or '空肠' in la5 or '胃造瘘' in la5 or '胃管' in la5

is_nutritions = [is_alfare, is_breastFeeding, is_formula, is_gluclose, is_lactoseFree, is_neocate, is_peptide, is_pretermInfants, is_yingnai, is_aminoAcid, is_neotate]

def is_nutrition(data):
    for j in is_nutritions:
        if j(data):
            return j(data)
    return False


import re

class get(object):
    quantity_p = re.compile(r'(?P<q>\d+)\s*((ml)|(毫升)).*', flags=re.I)
    quantity_p2 = re.compile(r'(?P<q>\d+)(\s|m).*', flags=re.I)
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
            return '蔼尔舒'
        if is_breastFeeding(src):
            return '母乳'
        if is_gluclose(src):
            return '葡萄糖'
        if is_lactoseFree(src):
            return '免乳糖奶'
        if is_neocate(src):
            return '纽康特'
        if is_neotate(src):
            return '纽太特'
        if is_peptide(src):
            return '小百肽'
        if is_pretermInfants(src):
            return '早奶'
        if is_yingnai(src):
            return '婴奶'
        if is_formula(src):
            return '配方奶'
        if is_aminoAcid(src):
            return '氨基酸'
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
            'wt': self.percent(src) if t == '葡萄糖' else 1,
            'en': t != '葡萄糖' or is_en(src),
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