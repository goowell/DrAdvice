db_ip = '192.168.2.109'
# db_ip = '10.10.2.110'
# db_ip = '10.10.111.22'

class names(object):
    ptt='葡萄糖'
    xbt='小百肽'
    pfn='配方奶'
    zn='早奶'
    yn='婴奶'
    mr='母乳'
    aes='蔼尔舒'
    mrtn='免乳糖奶'
    nkt='纽康特'
    ntt='纽太特'
    ajs='氨基酸'
    zcl='中长链脂肪乳'
    yy='鱼油脂肪乳'
    ts='糖水'




nu_per_ml = {
    names.ptt   :4,     #100%葡萄糖/ml
    names.xbt   :1,     #/ml
    names.pfn   :0.67,
    names.zn    :0.81,
    names.yn    :0.67,
    names.mr    :0.68,
    names.aes   :0.67,
    names.mrtn  :0.66,
    names.nkt   :0.71,
    names.ntt   :0.71,
    names.ajs   :4,     #100%AA/ml
    names.zcl   :2,     #/ml
    names.yy    :1      #/ml
}
protein_per_ml = {
    names.ptt   :0,
    names.xbt   :0.0385,
    names.pfn   :0.015,
    names.zn    :0.025,
    names.yn    :0.015,
    names.mr    :0.01,
    names.aes   :0.021,
    names.mrtn  :0.014,
    names.nkt   :0.0195,
    names.ntt   :0.0193,
    names.ajs   :1,         #100%AA/ml    
    names.zcl   :0,
    names.yy    :0    
}
weight_dict = {
    'D64385': 5,
    'C28069': 6,
    'C31838': 5.5,
    'D56128': 4,
    'C06324': 8,
    'C24275': 3.8,
    'B64954': 6.5,
    'B78836': 4.4,
    'B79668': 3.6,
    'C61762': 6.8,
    'B30827': 2.7,
    'D37175': 2.5,
    'E09679': 5.8,
    'B74640': 6.9
}
