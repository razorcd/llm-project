
from qdrant_client import QdrantClient, models
from tinydb import TinyDB, Query
from openai import OpenAI
import keys_secret
import helpers

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

class Rag:

    ai_model: str
    openai_client: OpenAI

    def __init__(self, ai_model):
        self.openai_client = OpenAI(api_key=keys_secret.openai_api_key)
        self.ai_model = ai_model

    def llm_aswer(self, prompt):
        response = self.openai_client.chat.completions.create(
            model=self.ai_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    def build_prompt(self, question, related_faq, courier):
        prompt_template = """
    You are the courier suport agent of a iDelivery company that handles food delivery in Germany, Netherlands and UK. 
    The couriers working for this company are employees or freelancers. 

    The courier {courier_first_name} is {courier_age} years old, has a {courier_contract_type} working contract and uses a {courier_vehicle_type} for delivery.
        
    Answer the courier's QUESTION based on the CONTEXT from the FAQ database.
    Use only the facts from the CONTEXT when answering the QUESTION.

    QUESTION: {question}

    CONTEXT: 
    {context}

    """.strip()

        context = ""
        
        for doc in related_faq:
            context = context + f"country: {doc['country']}\nquestion: {doc['question']}\nanswer: {doc['answer']}\n\n"

        # print(courier)
        prompt = prompt_template.format(question=question, 
                                        context=context, 
                                        courier_first_name=courier['first_name'],
                                        courier_age=courier['age'],
                                        courier_contract_type=courier['contract_type'],
                                        courier_vehicle_type=courier['vehicle_type'],
                                    ).strip()
        return prompt


    def get_llm_answer(self, question, courier, related_faq):
        prompt = self.build_prompt(question, related_faq, courier)
        # print(prompt)
        # print()
        # print("LLM answer:")
        answer_llm = self.llm_aswer(prompt)
        # print(answer_llm)

        return answer_llm

# question = "Can I deliver alcohol with my bike?"
# courier_id = 0

# faq_db = FaqRepository("localhost:6333", "courier_faq")
# related_faq = faq_db.vector_search(question, "DE", 0.7, 5)
# # print(related_faq)

# db_file_store = "tmp_tinydb_storage/courier_profiles_db.json"
# tinydb = TinyDB(db_file_store)
# courier = tinydb.search(Query().index == courier_id)[0]
# courier['age'] = helpers.get_age_by_birthdate(courier['date_of_birth'])

# rag = Rag("gpt-4o-mini")
# llm_answer = rag.get_llm_answer(question, courier, related_faq)

# print(llm_answer)

