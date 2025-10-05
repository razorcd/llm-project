

from tinydb import TinyDB, Query
from openai import OpenAI
import keys_secret
import helpers
from faq_repository import FaqRepository
import json

class RagEvaluation:
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

    def build_prompt(self, question, faq_answer, llm_answer):
        prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer compared to the original answer provided.
    Based on the relevance and similarity of the generated answer to the original answer, you will classify
    it as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Original Answer: {answer_orig}
    Generated Question: {question}
    Generated Answer: {answer_llm}

    Please analyze the content and context of the generated answer in relation to the original
    answer and provide your evaluation in parsable JSON without using code blocks:

    {{
    "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
    "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()
        
        prompt = prompt_template.format(
            answer_orig = faq_answer,
            question = question,
            answer_llm = llm_answer,
        )

        return prompt


    def evaluate_answer(self, question, faq_answer, llm_answer):
        prompt = self.build_prompt(question, faq_answer, llm_answer)
        # print(prompt)
        # print()
        answer_llm = self.llm_aswer(prompt)
        # print("LLM evaluation answer:")
        # print(answer_llm)

        return json.loads(answer_llm)


# question = "Can I deliver alcohol with my bike?"
# faq_answer = "No way!"
# llm_answer = "No, you cannot deliver alcohol with your bike."

# rag_evaluation = RagEvaluation("gpt-4o-mini")
# llm_eval_answer = rag_evaluation.evaluate_answer(question, faq_answer, llm_answer)

# print("LLM evaluation answer:", llm_eval_answer["Relevance"])
# print(llm_eval_answer)

