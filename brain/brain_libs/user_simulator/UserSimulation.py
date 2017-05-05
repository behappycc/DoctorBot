import sys
import random
sys.path.append('../LU_model')
import db
sys.path.pop()
sys.path.append('../data_resource')
import CrawlerTimeTable

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection

class User(object):
    def __init__(self):
        client = db.MongoClient(DB_IP, DB_PORT)

        collection_division = client[DB_NAME]["division"]
        collection_disease = client[DB_NAME]["disease"]
        self.goal = {'intent': random.randint(1, 5),
                     'slot': {'disease': None, 'division': None, 'doctor': None, 'time': None}}


def main():
    print(User().goal)

if __name__ == '__main__':
        main()
