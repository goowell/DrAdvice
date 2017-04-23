import logging

# create logger
logger = logging.getLogger('xinhua_log')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch2 = logging.FileHandler('xinhua_paser.log')
ch2.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
ch2.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
# logger.addHandler(ch2)