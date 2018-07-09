from datetime import datetime
from logger import logger
from os import listdir, path
from db import chemical_source, DuplicateKeyError,chemical_splited,paients_info


def chemical_examination_parse(file_root):
    chemical_source.drop()
    dir_list = listdir(file_root)
    file_list=[path.join(file_root,f) for f in dir_list]
    for f in file_list:
        logger.info(f)
        id=''
        with open(f,encoding='utf8') as fp:
            for l in fp.readlines():
                l=l.strip()
                if len(l)==6:
                    id=l.upper()
                else:
                    if len(l)>0 and id !='':
                        try:
                            chemical_source.insert_one({'_id':id,'data':l})
                        except DuplicateKeyError as identifier:
                            logger.error('duplicateKeyError: '+id)
                        id=''
                    else:
                        logger.error('wrong format: '+id)
def chemical_examination_split():
    '''
    {
        date:20160202,
        name:白细胞计数,
        value:16.93,
        unit:10^9/L,
        mark:'↑'
    }
    '''
    chemical_splited.drop()
    for r in chemical_source.find():
        results = []
        logger.info(r['_id'])
        for rr in r['data'].split('|'):
            rr = rr.strip()
            if rr:
                # print(rr)
                if '):' in rr:
                    rrs=rr.split(':')
                    date = rrs[0][-9:-1]
                    rr=rrs[1]
                rr=rr.split(' ')

                one_r=    {
                'date':date,
                'name':rr[0],
                'value':'',
                'unit':'',
                'mark':''
                }
            if len(rr)>=2:
                one_r['value']=rr[1]
            
            if len(rr)>=3:
                one_r['mark']=rr[2]
            if len(rr)>=4:
                one_r['unit']=' '.join(rr[3:])
            results.append(one_r)
        chemical_splited.insert_one({'_id':r['_id'], 'data':results})

def find_xx():
    with open('chemical_examination.csv',encoding='utf8',mode='a') as f:
        f.write('住院号,血红蛋白（入科）,血红蛋白（出科）,白蛋白（入科）,白蛋白（出科）'+'\n')
        for p in chemical_splited.find():
            info= paients_info.find_one({'住院号':p['_id']})
            if not info:
                info= paients_info.find_one({'住院号':p['_id'].lower()})
            if not info:
                logger.error('cannot find: '+p['_id'])
                continue
            # logger.info(info)
            date_in=info['入科日期'][0:10].replace('-','')
            date_out=info['出科日期'][0:10].replace('-','')
            xhdb_in=''
            xhdb_out=''
            bdb_in=''
            bdb_out=''
            date_xhdb_in=date_out
            date_xhdb_out=date_in
            date_bdb_in=date_out
            date_bdb_out=date_in
            # f.write(p['_id']+'\n')
            # [].sort()
            # p['data'].sort(key=lambda a: a['date'])
            for c in p['data']:
                if '白蛋白' == c['name'] or '白蛋白(干片法)' == c['name']:
                    if date_bdb_in>=c['date'] and c['date']>=date_in:
                        bdb_in=c['value']
                        date_bdb_in=c['date']
                    if date_bdb_out<=c['date'] and c['date']<=date_out:
                        bdb_out=c['value']
                        date_bdb_out=c['date']
                # if '血红蛋白'in c['name'] and '平均' not in c['name']:
                if '血红蛋白'== c['name']:
                    # print(c)
                    if date_xhdb_in>=c['date'] and c['date']>=date_in:
                        xhdb_in=c['value']
                        date_xhdb_in=c['date']
                    if date_xhdb_out<=c['date'] and c['date']<=date_out:
                        xhdb_out=c['value']
                        date_xhdb_out=c['date']
            f.write(','.join([p['_id'],xhdb_in,xhdb_out,bdb_in,bdb_out])+'\n')
def main():
    start = datetime.now()
    logger.info('hello..')
    dir_root = r"C:\pdata\xxxxxxxxx\huayan"
    # chemical_examination_parse(dir_root)
    # chemical_examination_split()
    find_xx()
    logger.info('done: '+str(datetime.now() - start))

if __name__ == '__main__':
    main()