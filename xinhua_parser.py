import re
from os import listdir, path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from datetime import datetime
from logger import logger

replace_p = re.compile(r'<\w+( [^>]+)>')

class MyHtmlParser(HTMLParser):

    def init(self):
        self.div_count = 0
        self.div_open = False
        self.tr_open = False
        self.td_open = False
        self.profile_open = False
        self.profile_keyword = '详细内容'
        self.dadvice_keyword = '核对护士'
        self.profile_keyword_open = False
        self.dadvice_keyword_open = False
        self.single_advie = []

        self.doctor_advice = []
        self.profile = []

    def handle_data(self, data):
        if self.td_open:
            if self.profile_open:
                self.profile.append(data)
                self.td_open = False
            elif self.div_open:
                self.single_advie.append(data)
                self.td_open = False

        if data == self.profile_keyword:
            self.profile_keyword_open = True
        elif data == self.dadvice_keyword:
            self.dadvice_keyword_open = True

    def handle_starttag(self, tag, attrs):
        if self.div_open:
            if tag == 'div':
                self.div_count += 1
            elif tag == 'tr':
                self.tr_open = True
            elif tag == 'td':
                self.td_open = True

        elif self.profile_open:
            if tag == 'td':
                self.td_open = True
        if tag == 'div' and self.dadvice_keyword_open and self.check_style(attrs, "x-grid3-scroller"):
            self.div_open = True
        elif tag == 'table' and self.profile_keyword_open:
            self.profile_open = True

    def handle_endtag(self, tag):
        if self.profile_open and tag == 'table':
            self.profile_open = False
            self.profile_keyword_open = False

        elif self.div_open:
            is_div = tag == "div"
            if is_div and self.div_count > 0:
                self.div_count -= 1
            elif is_div:
                self.div_open = False

            elif tag == 'tr':
                self.doctor_advice.append(self.single_advie)
                self.single_advie = []
                self.tr_open = False
            elif tag == 'td' and self.tr_open:
                if self.td_open:
                    self.single_advie.append('')
                    self.td_open = False
        elif tag == 'td' and self.profile_open and self.td_open:
            self.profile.append('')
            self.td_open = False

    def check_style(self, attrs, style):
        for attr in attrs:
            if attr[0] == 'class' and attr[1] == style:
                return True
        return False


def parse_one_file(file_path):
    parser = MyHtmlParser()
    parser.init()
    with open(file_path, encoding='UTF-8') as f:
        c = f.read()
        idx = c.find('归档状态')
        c = c[idx:]
        idx = c.find('任务列表')
        s1 = c[:idx]
        idx2 = c.rfind('停止医生')
        s2 = c[idx2:]
        parser.feed(s1 + s2)

        # parser.feed(c)
    return parser.profile, parser.doctor_advice


def parse_one(file_path):
    a, b = parse_one_file(file_path)
    if a == [] or b == []:
        logger.error('invalid file: %s', file_path)
    c, d = parse_one_file(file_path.replace('.htm', 'S.htm'))
    if c == [] or d == []:
        logger.error('invalid file: %s S', file_path)
    b.extend(d)
    id = path.basename(file_path).split('.')[0]
    return {'_id': id, 'd': {'info': a, 'doctor_advice': b}}

def collect_files(dir_root):
    dir_list = listdir(dir_root)
    files = [path.join(dir_root, f) for f in dir_list if f.endswith('htm')and len(f) == 10]
    for d in dir_list:
        if '_files' not in d:
            sub_dir = path.join(dir_root, d)
            if path.isdir(sub_dir):
                files.extend(collect_files(sub_dir))
    return files

def refresh_db(dir_root):
    client = MongoClient('192.168.4.12')
    collection = client.xinhuahos.paients
    all_html = collect_files(dir_root)
    def _save(f): 
        logger.debug(f)
        return collection.save(parse_one(f))

    with ThreadPoolExecutor(max_workers=8) as executor:
        fs = executor.map(_save, all_html)
        list(fs)

    client.close()

def test_parse_file():
    files = [
        'C:\\data\\xxxxxxxxx\\基本信息-原始\\raw_data\\data2016\\201606\\C81461.htm', 'C:\\data\\xxxxxxxxx\\基本信息-原始\\raw_data\\data2016\\201606\\C81493.htm', 'C:\\data\\xxxxxxxxx\\基本信息-原始\\raw_data\\data2016\\201606\\C82016.htm', 'C:\\data\\xxxxxxxxx\\基本信息-原始\\raw_data\\data2016\\201606\\C82372.htm'
    ]
    for f in files:
        print(f)
        parse_one(f)
        break 

def remove_style(strs):
    # aa = replace_p.findall(strs)
    
    # for n in aa:
    #     if 'x-grid3-scroller' not in n:
    #         strs = strs.replace(n, '')
    return strs

def main():
    test_str = r'<div style="position: absolute; left: 200px; top: 0px; width: 5px; height: 410px; " id="x-auto-163773" class="x-vsplitbar x-component x-unselectable" unselectable="on"></div></div>aaaaa</div></div></div></div><div role="presentation" class="x-window-bl"><div role="presentation" class="x-window-br"><div role="presentation" class="x-window-bc"><div role="presentation" class="x-window-footer"><div class=" x-panel-btns"><div class=" x-small-editor x-panel-fbar x-component x-toolbar-layout-ct" id="x-auto-163757" style="width: 916px; "><table cellspacing="0" class="x-toolbar-ct" role="presentation"><tbody>'

    start = datetime.now()
    logger.info('hello..' + start.strftime('%H:%M:%S'))
    dir_root = r"C:\data\xxxxxxxxx\基本信息-原始\raw_data"
    refresh_db(dir_root)
    # test_parse_file()
    # remove_style(test_str)
    logger.info(datetime.now() - start)


if __name__ == '__main__':
    main()
