def is_neocate(data):
    '纽康特'
    return '纽康特' in data[5]

def is_lactoseFree(data):
    '免乳糖奶'
    return '免乳' in data[5]

def is_alfare(data):
    '蔼尔舒'
    return '蔼' in data[5] or '霭' in data[5]

def is_breastFeeding(data):
    '母乳'
    return '母乳' in data[5]

def is_yingnai(data):
    '婴奶'
    return '婴' in data[5]

def is_pretermInfants(data):
    '早奶'
    return '早' in data[5]

def is_formula(data):
    '配方奶'
    return '配方' in data[5]

def is_peptide(data):
    '小百肽'
    return '小百肽' in data[5]

def is_gluclose(data):
    '葡萄糖'
    d = data[5]
    return '抽胃液' not in d and ('葡' in d or 'gs' in d.lower())

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

def is_en(data):
    la5 = data[5].lower()
    return '口服' in la5 or '鼻饲' in la5 or 'po' in la5

import re

class get(object):
    quantity_p = re.compile(r'(?P<q>\d+)\s*((ml)|(毫升)).*', flags=re.I)
    times_p = re.compile(r'(q|(维持))(?P<q>\d+)h', flags=re.I)
    times_p2 = re.compile(r'\*(?P<q>\d+)', flags=re.I)
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
    def dict_ad(self, src):
        return {
            'st': self.start(src),
            'et': self.stop(src),
            't': self.type(src),
            'en': self.type(src) != '葡萄糖' or is_en(src),
            'total': self.quantity(src) * self.times(src)
        }
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