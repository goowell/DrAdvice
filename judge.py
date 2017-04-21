def is_neocate(data):
    '纽康特'
    return '纽康特' if '纽康特' in data[5] else None

def is_lactoseFree(data):
    '免乳糖奶'
    return '免乳糖奶' if '免乳' in data[5] else None

def is_alfare(data):
    '蔼尔舒'
    return '蔼尔舒' if '蔼' in data[5] or '霭' in data[5] else None

def is_breastFeeding(data):
    '母乳'
    return '母乳' if '母乳' in data[5] else None

def is_yingnai(data):
    '婴奶'
    return '婴奶' if '婴' in data[5] else None

def is_pretermInfants(data):
    '早奶'
    return '早奶' if '早' in data[5] else None

def is_formula(data):
    '配方奶'
    return '配方奶' if '配方' in data[5] else None

def is_peptide(data):
    '小百肽'
    return '小百肽' if '小百肽' in data[5] else None

def is_gluclose(data):
    '葡萄糖'
    d = data[5]
    return '葡萄糖' if (('葡' in d or 'gs' in d.lower()) and '抽胃液' not in d)  else None

def is_weight(data):
    '体重'
    return '体重' in data[5] and '测' not in data[5]

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

def is_en(data):
    la5 = data[5].lower()
    return '口服' in la5 or '鼻饲' in la5 or 'po' in la5

is_nutritions = [is_alfare, is_breastFeeding, is_formula, is_gluclose, is_lactoseFree, is_neocate, is_peptide, is_pretermInfants, is_yingnai]

def is_nutrition(data):
    for j in is_nutritions:
        if j(data):
            return j(data)
    return False


import re

class get(object):
    quantity_p = re.compile(r'(?P<q>\d+)\s*((ml)|(毫升)).*', flags=re.I)
    times_p = re.compile(r'(q|(维持))(?P<q>\d+)h', flags=re.I)
    times_p2 = re.compile(r'\*(?P<q>\d+)', flags=re.I)
    weight_p = re.compile(r'(?P<q>\d+\.?\d*)((g)|(kg)).*')

    def weight(self, src):
        str_src = src[5].lower()
        res = self.weight_p.search(str_src)
        if res:
            v = res.groupdict()['q']
            return float(v) if 'kg' in str_src else float(v)/1000
        return 0

    def quantity(self, src):
        str_src = src[5]
        res = self.quantity_p.search(str_src)
        if res:
            return int(res.groupdict()['q'])
        return 0
        # return self.quantity_p.search(str_src)
    def times(self, src):
        str_src = src[5].lower()
        if 'qd' in str_src:
            return 1.0
        if 'bid' in str_src:
            return 2.0
        if 'tid' in str_src:
            return 3.0
            
        if '*' in str_src:
            res = self.times_p2.search(str_src)
            if res:
                return int(res.groupdict()['q'])
        else:
            res = self.times_p.search(str_src)
        if res:
            return 24/int(res.groupdict()['q'])
        
        if '临' == src[3]:
            return 1.0
        return 0

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
        if is_peptide(src):
            return '小百肽'
        if is_pretermInfants(src):
            return '早奶'
        if is_yingnai(src):
            return '婴奶'
        if is_formula(src):
            return '配方奶'
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
        return {
            'st': self.start(src),
            'et': self.stop(src),
            't': self.type(src),
            'en': self.type(src) != '葡萄糖' or is_en(src),
            'total': self.quantity(src) * self.times(src)
        }
    def dict(self, src):
        '''
        return 
            None
        or
            {'st': '2014-10-31 19:37', 'w': 7.0}
        or 
            {'total': 60.0, 'et': '2014-11-07 12:45', 'st': '2014-11-05 14:06', 'en': False, 't': '葡萄糖'}
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
    '5%葡萄糖针 50ml 口服',
    '10%葡萄糖针 50ml 静滴 st',
    '5%葡萄糖针 42 ml 鼻饲',
    'ssss555mlllll'
]

def main():
    _get = get()
    for t in test_case:
        print(_get.quantity(t))

if __name__ == '__main__':
    main()