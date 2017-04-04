import re
from os import listdir, path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient

class MyHtmlParser(HTMLParser):

    def init(self):
        self.print = False
        self.div_count = 0
        self.div_open = False
        self.tr_open = False
        self.td_open = False
        self.profile_open = False
        self.single_advie = []

        self.doctor_advice = []
        self.profile = []

    def handle_data(self, data):
        if self.td_open:
            self.single_advie.append(data)
            self.td_open = False
        elif self.profile_open:
            self.profile.append(data)

    def handle_starttag(self, tag, attrs):
        if self.div_open:
            if tag == 'div':
                self.div_count += 1
            elif tag == 'tr':
                self.tr_open = True
            elif tag == 'td':
                self.td_open = True

        if tag == 'div' and self.check_style(attrs, "width: 724px; height: 332px; "):
            # self.div_open = True
            pass
        elif tag == 'table' and self.check_style(attrs, "width: 1013px; "):
            self.profile_open = True

    def handle_endtag(self, tag):
        if self.profile_open and tag == 'table':
            self.profile_open = False

        elif  self.div_open:
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

    def check_style(self, attrs, style):
        for attr in attrs:
            if attr[0] == 'style' and attr[1] == style:
                return True
        return False

def parse_one(file_path):
    parser = MyHtmlParser()
    parser.init()
    with open(file_path, encoding='UTF-8') as f:
        parser.feed(f.read())
    return parser.profile, parser.doctor_advice


def main():
    from datetime import datetime

    start = datetime.now()
    print('hello..')
    dir = "C:/data/xxxxxxxxx/data/"
    all_html = [f for f in listdir(dir) if f.endswith('htm')and len(f) == 10]
    client = MongoClient('192.168.2.110')
    collection = client.xinhuahos.paients
    for f in all_html:
        b=[]
        a, b = parse_one(dir + f)
        c, d = parse_one(dir + f.replace('.', 'S.'))
        b.extend(d)
        collection.save({'_id':f.split('.')[0],'d':{'info':a, 'doctor_advice': b}})
        print(f)
    client.close()

    print(datetime.now() - start)


if __name__ == '__main__':
    main()
