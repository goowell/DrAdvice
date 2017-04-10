def is_neocate(data):
    '纽康特'
    return '纽康特' in data[5]

def is_lactoseFree(data):
    '免乳糖奶'
    return '免乳' in data[5]

def is_alfare(data):
    '蔼尔舒'
    return '蔼' in data[5]

def is_breastFeeding(data):
    '母乳'
    return '母乳' in data[5]

def is_yingnai(data):
    '婴奶'
    return '婴' in data[5]

def is_pretermInfants(data):
    '早奶'
    return '早' in data[5]

def is_gluclose(data):
    '葡萄糖'
    return '葡' in data[5] or 'gs' in data[5].lower()

def is_executed(data):
    '已执行'
    return '已执行' == data[16]

