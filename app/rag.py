

from tinydb import TinyDB, Query
from openai import OpenAI
import keys_secret
import helpers
from faq_repository import FaqRepository
from time import time

class Rag:
    ai_model: str
    openai_client: OpenAI

    def __init__(self, ai_model):
        self.openai_client = OpenAI(api_key=keys_secret.openai_api_key)
        self.ai_model = ai_model

    def _llm_aswer(self, prompt):
        response = self.openai_client.chat.completions.create(
            model=self.ai_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer_llm = response.choices[0].message.content
        token_stats = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        return answer_llm, token_stats
        

    def _build_prompt(self, question, related_faq, courier):
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
        start_time = time()

        prompt = self._build_prompt(question, related_faq, courier)
        # print(prompt)
        # print()
        # print("LLM answer:")
        answer_llm, token_stats = self._llm_aswer(prompt)
        # print(answer_llm)
        relevance, rel_token_stats = {}, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens":0} #evaluate_relevance(query, answer)

        openai_cost_rag = self._calculate_openai_cost(self.ai_model, token_stats)
        # openai_cost_eval = self._calculate_openai_cost(self.ai_model, rel_token_stats)

        openai_cost = openai_cost_rag #+ openai_cost_eval

        answer_data = {
                "answer": answer_llm,
                "model_used": self.ai_model,
                "response_time": (time() - start_time),
                "relevance": relevance.get("Relevance", "UNKNOWN"),
                "relevance_explanation": relevance.get(
                    "Explanation", "Failed to parse evaluation"
                ),
                "prompt_tokens": token_stats["prompt_tokens"],
                "completion_tokens": token_stats["completion_tokens"],
                "total_tokens": token_stats["total_tokens"],
                "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
                "eval_completion_tokens": rel_token_stats["completion_tokens"],
                "eval_total_tokens": rel_token_stats["total_tokens"],
                "openai_cost": openai_cost,
            }

        return answer_data
    
    def _calculate_openai_cost(self, model, tokens):
        openai_cost = 0

        if model == "gpt-4o-mini":
            openai_cost = (
                tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
            ) / 1000
        else:
            print("Model not recognized. OpenAI cost calculation failed.")

        return openai_cost

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

