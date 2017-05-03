from pymongo import MongoClient
import setting
    
client = MongoClient(setting.db_ip)
paients_source = client.xinhuahos.paients
paients_splited = client.xinhuahos.paients_splited
paients_merged = client.xinhuahos.paients_merged
paients_calculated = client.xinhuahos.paients_calculated
