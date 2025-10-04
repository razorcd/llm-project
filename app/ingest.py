import pandas as pd
import numpy as np
from tinydb import TinyDB, Query
from pathlib import Path
from qdrant_client import QdrantClient, models

def ingest_faq_data_to_db(source_faq_data_file, db_server, collection_name):
    couriers_faq_df = pd.read_csv(source_faq_data_file)

    replacement_map = {
        'germany': 'DE',
        'netherlands': 'NL',
        'uk': 'GB'
    }
    couriers_faq_df['country'] = couriers_faq_df['country'].str.lower().replace(replacement_map)


    qd_client = QdrantClient(db_server)
    EMBEDDING_DIMENSIONALITY = 512
    model_handle = "jinaai/jina-embeddings-v2-small-en"
    collection_name = collection_name

    #prepare collection
    qd_client.delete_collection(collection_name=collection_name)

    if qd_client.collection_exists(collection_name=collection_name):
        qd_client.delete_collection(collection_name=collection_name)


    qd_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=EMBEDDING_DIMENSIONALITY,
            distance=models.Distance.COSINE
        )
    )

    qd_client.create_payload_index(
        collection_name=collection_name,
        field_name="country",
        field_schema="keyword"
    )

    points = []

    for i, doc in couriers_faq_df.iterrows() :
        text = doc['question'] + ' ' + doc['answer']
        vector = models.Document(text=text, model=model_handle)
        point = models.PointStruct(
            id=i,
            vector=vector,
            payload=doc.to_dict()
        )
        points.append(point)

    print("Inserting " + str(len(points)) + " points.")

    qd_client.upsert(
        collection_name=collection_name,
        points=points
    )

    return qd_client


def ingest_courier_profiles_to_db(source_courier_profile_file, db_file_store):
    countries = ['DE', 'NL', 'GB']
    couriers_profiles_df = pd.read_csv(source_courier_profile_file)
    couriers_profiles_df['country'] = np.random.choice(countries, size=len(couriers_profiles_df))
    couriers_profiles_df = couriers_profiles_df.reset_index()
    
    courier_profiles_db_file = Path(db_file_store)
    courier_profiles_db_file.unlink(missing_ok=True)
    db = TinyDB(courier_profiles_db_file)
    db.insert_multiple(couriers_profiles_df.to_dict('records'))

    return db


# Ingest FAQ data to Qdrant DB
source_faq_data_file = "dataset/couriers_faq.csv"
db_server = "http://localhost:6333"
collection_name = "courier_faq"

qd_client = ingest_faq_data_to_db(source_faq_data_file, db_server, collection_name)

# Ingest Courier profiles to TinyDB
source_courier_profile_file = "dataset/courier_profiles.csv"
db_file_store = "tmp_tinydb_storage/courier_profiles_db.json"

tinydb = ingest_courier_profiles_to_db(source_courier_profile_file, db_file_store)