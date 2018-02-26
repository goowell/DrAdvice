from logger import logger
from pyexcel import get_book
import xlrd
import datetime
import re
from db import paients_pn,paients_info

def main():
    logger.info('start...')
    # parse_pn_from_excel()
    parse_sn_from_excel()
    logger.info('done')

def parse_sn_from_excel():
    filenames=[
        r"C:\data\xxxxxxxxx\基本信息-最新\2014PSICU1入院登记 基本信息 .xls",
        r"C:\data\xxxxxxxxx\基本信息-最新\2015年基本信息.xlsx",
        r"C:\data\xxxxxxxxx\基本信息-最新\2016年基本信息.xlsx",
        r"C:\data\xxxxxxxxx\基本信息-最新\2017年基本信息.xlsx"
    ]
    patients=[]
    '''
    [
        {
            'namexx':'snxx'
            ...
        },
    ...
        
    ]
    '''
    for filename in filenames:
        onefilesn(filename, patients)
    paients_info.remove()
    for p in patients:
        paients_info.insert_one(p)
    print(patients)

def onefilesn(filename, patients):
    a = xlrd.open_workbook(filename=filename)
    # year = re.findall("\d+", filename)[0]
    print(a.sheet_names())
    for sheet_name in a.sheet_names():
        print(sheet_name)
        # patients={}
        # sns_key = year + '-' +sheet_name[:-1]
        sheet=a.sheet_by_name(sheet_name)
        idx_name=0
        idx_sn=0
        idx_checkin=0
        if sheet.nrows<3:
            continue
        row0 = sheet.row(0)
        row1 = sheet.row(1)

        for r in sheet.get_rows():
            if idx_name==0:
                for d in r:
                    if d.value=='姓名':
                        break
                    idx_name += 1
                for d in r:
                    if d.value=='住院号':
                        break
                    idx_sn += 1
                for d in r:
                    if d.value=='入科日期':
                        break
                    idx_checkin += 1
                if idx_checkin > 20 or idx_name > 12 or idx_sn> 12:
                    raise Exception('invalid data: '+sheet_name)
                print(idx_name,idx_sn, idx_checkin)
                continue
            if r[idx_name].value != '' and r[1].ctype==xlrd.XL_CELL_TEXT:
                # _getSN(r, idx_name, idx_checkin, patients, idx_sn, sheet_name)
                one_info = {}
                for i in range(len(r)):
                    one_info.update({row0[i].value if row1[i].ctype==xlrd.XL_CELL_EMPTY else
                        row1[i].value :r[i].value if r[i].ctype!=xlrd.XL_CELL_DATE else xlrd.xldate_as_datetime(r[i].value,0).isoformat()})
                patients.append(one_info)

def _getSN(r, idx_name, idx_checkin, patients, idx_sn, sheet_name):
    k=r[idx_name].value+xlrd.xldate_as_datetime(r[idx_checkin].value,0).date().isoformat()
    if k in patients.keys():
        print({k:r[idx_sn].value},sheet_name)
        print(patients[k])
    else:
        patients.update({k:r[idx_sn].value})
        # patients.update({sns_key:sns})
    
    
def parse_pn_from_excel():
    filenames=[
        r"C:\data\xxxxxxxxx\基本信息-原始\2014年能量.xlsx",
        r"C:\data\xxxxxxxxx\基本信息-原始\2015年能量.xlsx",
        r"C:\data\xxxxxxxxx\基本信息-原始\2016年能量.xlsx",
        r"C:\data\xxxxxxxxx\基本信息-原始\2017年能量.xlsx"
    ]
    patients=[]
    '''
    [
        {
            name:'xxx2015-01-10',
            month:'2015-01',
            pn:[
                {
                    date:'2015-01-10',
                    '脂肪乳':10,
                    '6%AA':10,
                    '10%GS':20,
                    '20%GS':20
                }
            ]
        },
        {}
    ]
    '''
    for filename in filenames:
        onefile(filename, patients)
    paients_pn.remove()
    sns = paients_info.find_one()
    for p in patients:
        try:
            p.update({'sn':sns[p['name']]})
        except KeyError as identifier:
            print(p['name'])
            for sn in sns.keys():
                if p['name'][:3] in sn or ((p['name'][0] in sn or p['name'][1] in sn or p['name'][-12:-13] in sn) and p['name'][-8:] in sn):
                    p.update({'sn':sns[sn]})
        paients_pn.insert_one(p)

def onefile(filename, patients):
    a = xlrd.open_workbook(filename=filename)
    print(a.sheet_names())
    for sheet_name in a.sheet_names():
        _month = filename[-12:-8] +'-'+ sheet_name[:-1]
        sheet=a.sheet_by_name(sheet_name)
        print(sheet.nrows,sheet.ncols)
        print(_month)
        idx_date = 0
        idx_zfr = 0
        p=[]
        for r in sheet.get_rows():
            # print(r)
            if idx_date == 0:
                for d in r:
                    if d.value=='入科日期':
                        break
                    idx_date += 1
                continue
            if idx_zfr == 0:
                for d in r:
                    if d.value=='脂肪乳':
                        break
                    idx_zfr += 1
                if idx_date==0 or idx_zfr==0 or idx_date>12 or idx_zfr>12:
                    raise Exception('invalid data:' + sheet_name)
                idx_6aa = idx_zfr+1
                idx_10gs = idx_zfr+2
                idx_25gs = idx_zfr+3
                print(idx_zfr,idx_date)
                continue
            if r[1].value != '' and r[1].ctype==xlrd.XL_CELL_TEXT:
                if p:
                    patients.append(p)
                p = {
                        'name':r[1].value+xlrd.xldate_as_datetime(r[idx_date].value,0).date().isoformat(),
                        'month':_month,
                        'pn':[]
                    }
            if r[idx_date].ctype==xlrd.XL_CELL_DATE:
                one_pn={
                    'date':xlrd.xldate_as_datetime(r[idx_date].value,0).date().isoformat(),
                    '脂肪乳':r[idx_zfr].value if r[idx_zfr].ctype==xlrd.XL_CELL_NUMBER else 0,
                    '6%AA':r[idx_6aa].value if r[idx_6aa].ctype==xlrd.XL_CELL_NUMBER else 0,
                    '10%GS':r[idx_10gs].value if r[idx_10gs].ctype==xlrd.XL_CELL_NUMBER else 0,
                    '25%GS':r[idx_25gs].value if r[idx_25gs].ctype==xlrd.XL_CELL_NUMBER else 0                    
                }
                p['pn'].append(one_pn)




if __name__ == '__main__':
    main()