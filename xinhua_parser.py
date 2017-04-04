import re
from os import listdir, path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient


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
    return parser.profile, parser.doctor_advice


def parse_one(dir, file_name):
    a, b = parse_one_file(dir + file_name)
    c, d = parse_one_file(dir + file_name.replace('.', 'S.'))
    b.extend(d)
    return {'_id': file_name.split('.')[0], 'd': {'info': a, 'doctor_advice': b}}


def main():
    from datetime import datetime

    start = datetime.now()
    print('hello..')
    dir = "C:/data/xxxxxxxxx/data/"
    all_html = [f for f in listdir(dir) if f.endswith('htm')and len(f) == 10]
    client = MongoClient('192.168.2.110')
    collection = client.xinhuahos.paients
    # collection.save(parse_one(dir, 'B30827.htm'))
    # collection.save(parse_one(dir, 'B31008.htm'))

    def _save(f): 
        print(f)
        return collection.save(parse_one(dir, f))
    # for f in all_html:
    #     collection.save(parse_one(dir, f))
    #     print(f)

    with ThreadPoolExecutor(max_workers=8) as executor:
        fs = executor.map(_save, all_html)
        list(fs)

    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()
