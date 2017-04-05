from pymongo import MongoClient
import csv
import ast

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection


def drop_db(client, db_name):
    client.drop_database(db_name)


def remove_all_documents(collection):
    result = collection.delete_many({})
    print (result.deleted_count)


def create_division(collection_division, division):
    disease = ast.literal_eval(division[1])
    doctor = ast.literal_eval(division[2])
    division = {
        "department": division[0],
        "disease": disease,
        "doctor": doctor
    }

    collection_division.insert_one(division).inserted_id


def create_disease(collection_disease, disease):
    disease_e = ast.literal_eval(disease[1])
    department = ast.literal_eval(disease[2])
    organ = ast.literal_eval(disease[3])
    symptom = ast.literal_eval(disease[4])

    disease = {
        "disease_c": disease[0],
        "disease_e": disease_e,
        "department": department,
        "organ": organ,
        "symptom": symptom,
        "url": disease[5]
    }

    collection_disease.insert_one(disease).inserted_id


def create_collection_division(collection_division):
    remove_all_documents(collection_division)
    with open('data_resource/division.csv', 'r') as csvfile:
        for row in csv.reader(csvfile):
            create_division(collection_division, row)


def create_collection_disease(collection_disease):
    remove_all_documents(collection_disease)
    with open('data_resource/disease.csv', 'r') as csvfile:
        for row in csv.reader(csvfile):
            create_disease(collection_disease, row)


def main():
    client = MongoClient(DB_IP, DB_PORT)
    # drop_db(client, DB_NAME)

    collection_division = client[DB_NAME]["division"]
    collection_disease = client[DB_NAME]["disease"]
    print (collection_division.count())
    print (collection_disease.count())

    # create_collection_division(collection_division)
    # create_collection_disease(collection_disease)

    for division in collection_division.find({"doctor": "王秀枝"}):
        print (division)

    for disease in collection_disease.find({"symptom": "流鼻水", "disease_c": "百日咳"}):
        print (disease)


if __name__ == '__main__':
    main()
