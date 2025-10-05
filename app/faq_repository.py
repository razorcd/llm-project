from qdrant_client import QdrantClient, models

class FaqRepository:
    qd_client: QdrantClient
    collection_name: str
    MODEL_HANDLE = "jinaai/jina-embeddings-v2-small-en"
    # EMBEDDING_DIMENSIONALITY = 512
    
    def __init__(self, db_server, collection_name):
        self.qd_client = QdrantClient(db_server)
        self.collection_name = collection_name

    def vector_search(self, question, country, score_threshold, limit):
        # print('vector_search is called on question: '+question)
        
        query_points = self.qd_client.query_points(
            collection_name=self.collection_name,
            query=models.Document(
                text=question,
                model=self.MODEL_HANDLE 
            ),
            query_filter=models.Filter( 
                must=[
                    models.FieldCondition(
                        key="country",
                        match=models.MatchAny(any=[country, "all"] )
                    )
                ]
            ),
            score_threshold = score_threshold,
            limit=limit,
            with_payload=True
        )

        results = []
        
        for point in query_points.points:
            results.append(point.payload)
        
        return results
