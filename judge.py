def is_neocate(data):
    '纽康特'
    return '纽康特' in data[5]

def is_lactoseFree(data):
    '免乳糖奶'
    return '免乳' in data[5]

def is_alfare(data):
    '蔼尔舒'
    return '舒' in data[5]

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
    return '葡' in data[5] or 'gs' in data[5].lower()

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

import re

class get(object):
    quantity_p = re.compile(r'(?P<q>\d+)\s*ml.*', flags=re.I)
    times_p = re.compile(r'q(?P<q>\d+)h', flags=re.I)
    def quantity(self, str_src):
        print(str_src)
        res = self.quantity_p.search(str_src)
        if res:
            return int(res.groupdict()['q'])
        return 0
        # return self.quantity_p.search(str_src)
    def times(self, str_src):
        print(str_src)
        if 'qd' in str_src.lower():
            return 24.0
        res = self.times_p.search(str_src)
        if res:
            return 24/int(res.groupdict()['q'])
        return 0

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