import re
from os import listdir, path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor

class MyHtmlParser(HTMLParser):
    print = False
    div_count = 0
    div_open = False
    tr_open = False
    td_open = False
    profile_open = False
    single_advie = []

    doctor_advice = []
    profile = []

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
            self.div_open = True
        if tag == 'table' and self.check_style(attrs, "width: 1013px; "):
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

def parser_one(file_path):
    parser = MyHtmlParser()
    with open(file_path, encoding='UTF-8') as f:
        parser.feed(f.read())
    return parser.profile, parser.doctor_advice


def main():
    print('hello..')
    all_html = ["C:/data/xxxxxxxxx/data/"+f for f in listdir("C:/data/xxxxxxxxx/data/") if f.endswith('htm')]
    b, a = parser_one(all_html[0])
    for aa in a:
        print(aa)
    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     fs = executor.map(parser_one, all_html)

    #     for f,a in fs:
    #         print(f)
    #         break



if __name__ == '__main__':
    main()
