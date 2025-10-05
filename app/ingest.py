import pandas as pd
import numpy as np
from tinydb import TinyDB
from pathlib import Path
from qdrant_client import QdrantClient, models
from conversation_repository import ConversationRepository
import os



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


    qd_client.create_collection(
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

    print("Inserting " + str(len(points)) + " FAQ points.")

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
    
    print("Inserting " + str(len(couriers_profiles_df)) + " courier profiles points in NoSql DB.")
    db.insert_multiple(couriers_profiles_df.to_dict('records'))

    return db

def delete_similar_faq_data(qd_client, collection_name):
    ### Delete similar questions based on high cosine similarity.
    ### Run 3 times for best result.

    all_points = list(qd_client.scroll(
        collection_name=collection_name,
        with_vectors=True,
        limit=100000
    )[0])

    points_to_delete = set()
    processed_points = set()

    for point in all_points:
        point_id = point.id

        if point_id in processed_points:
            continue 

        #Search for nearest neighbors using the current point's vector
        search_results = qd_client.query_points(
            collection_name=collection_name,
            query=point.vector,
            limit=25,          
            score_threshold=0.9999, 
        )

        #Identify duplicates (points with high similarity)
        duplicates = []
        for hit in search_results.points:
            if hit.id != point_id:
                duplicates.append(hit.id)

        #Mark the original point as processed and duplicates for deletion
        processed_points.add(point_id)
        for dup_id in duplicates:
            points_to_delete.add(dup_id)
            processed_points.add(dup_id) 


    # Convert the set of IDs to a list
    deletion_list = list(points_to_delete)

    if deletion_list:
        qd_client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(
                points=deletion_list
            )
        )
        print(f"Successfully deleted {len(deletion_list)} duplicate FAQ points in vector DB.")
    else:
        print("No FAQ duplicates found above the threshold.")

print("Inisialising PostgreSQL database for conversations.")
# os.environ['RUN_TIMEZONE_CHECK'] = '0'
ConversationRepository().init_db()

QD_SERVER = os.environ.get("QD_SERVER", "localhost:6333")
print(f"Using Qdrant server at: {QD_SERVER}")
TINY_DB_FILE = "tmp_datastore/tmp_tinydb_storage/courier_profiles_db.json"
print(f"Using TinyDB file: {TINY_DB_FILE}")


print("Ingest FAQ data to Qdrant DB")
source_faq_data_file = "dataset/couriers_faq.csv"
db_server = QD_SERVER
collection_name = "courier_faq"

qd_client = ingest_faq_data_to_db(source_faq_data_file, db_server, collection_name)
delete_similar_faq_data(qd_client, collection_name)

print("Ingest Courier profiles to TinyDB")
source_courier_profile_file = "dataset/courier_profiles.csv"
db_file_store = TINY_DB_FILE

tinydb = ingest_courier_profiles_to_db(source_courier_profile_file, db_file_store)

print("Ingestion completed.")