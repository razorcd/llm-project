from flask import Flask, request, jsonify
from rag import Rag, FaqRepository
from tinydb import TinyDB, Query
import helpers
import uuid

app = Flask(__name__)


# curl --request POST 'http://127.0.0.1:5000/question' \
# --header 'Content-Type: application/json' \
# -d '{"question": "Can I keep the bike?", "courier_id": 0}'
@app.route('/question', methods=['POST'])
def handle_question():
    data = request.json
    question = data.get('question')
    courier_id = data.get('courier_id')
    conversation_id = uuid.uuid4().hex

    if not question or courier_id is None:
        return jsonify({"error": "Missing 'question' or 'courier_id' in request body"}), 400

    faq_db = FaqRepository("localhost:6333", "courier_faq")
    related_faq = faq_db.vector_search(question, "DE", 0.7, 5)

    db_file_store = "tmp_tinydb_storage/courier_profiles_db.json"
    tinydb = TinyDB(db_file_store)
    courier = tinydb.search(Query().index == courier_id)[0]
    courier['age'] = helpers.get_age_by_birthdate(courier['date_of_birth'])

    rag = Rag("gpt-4o-mini")
    answer_llm = rag.get_llm_answer(question, courier, related_faq)

    return jsonify({"conversation_id":conversation_id, "answer": answer_llm})

# curl --request POST 'http://127.0.0.1:5000/feedback' \
# --header 'Content-Type: application/json' \
# -d '{"conversation_id": "11111111", "positive": true, "feedback": "Good"}'
@app.route('/feedback', methods=['POST'])
def handle_feedback():
    data = request.json
    conversation_id = data.get('conversation_id')
    positive = data.get('positive')
    feedback = data.get('feedback')

    if not conversation_id or positive is None or feedback is None:
        return jsonify({"error": "Missing 'conversation_id', 'positive' or 'feedback' in request body"}), 400

    # store the feedback

    print(f"Received feedback for conversation {conversation_id}: {feedback}")

    return jsonify({"message": "Feedback received"}), 200

if __name__ == '__main__':
    app.run(debug=True)