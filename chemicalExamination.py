from datetime import datetime
from logger import logger

def main():
    start = datetime.now()
    logger.info('hello..')
    dir_root = r"C:\data\xxxxxxxxx\基本信息-原始\raw_data\last6"
    # refresh_db(dir_root)
    # _test_parse_one()
    # print(b)
    # test_parse_file()
    # remove_style(test_str)
    # find_omitted(dir_root)
    logger.info('done: '+str(datetime.now() - start))

if __name__ == '__main__':
    main()