from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import setting
    
client = MongoClient(setting.db_ip)
paients_source = client.xinhuahos.paients
paients_splited = client.xinhuahos.paients_splited
paients_splited_with_excel = client.xinhuahos.paients_splited_with_excel
paients_merged = client.xinhuahos.paients_merged
paients_calculated = client.xinhuahos.paients_calculated
paients_pn = client.xinhuahos.paients_pn
paients_info = client.xinhuahos.paients_info
chemical_source = client.xinhuahos.chemical_source
chemical_splited = client.xinhuahos.chemical_splited

