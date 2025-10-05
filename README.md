# llm-project
LLM capstone project for the LLM training

### Project description
Support agent for couriers of a food delivery company called iDelivery. The support agent is integrated with AI, uses a FAQ dataset and also knows about each courier profile.

### Architecture design
![Architecture design](architecture_design.png)

### Technolofgies

- Qdrant vector DB to store FAQ data
- TinyDB NoSql DB to store Courier profile data
- OpenAi as LLM for RAG AI integration
- Flask as API server

### Running the Jupyter notebooks locally

1. use Python v3.10.x
1. `pip install pipenv`
1. `pipenv shell`
2. `pipenv install` to install all dependencies
3. Start Qdrant: `podman run --rm -p 6333:6333 -p 6334:6334 -v "$(pwd)/tmp_qdrant_storage:/qdrant/storage:z" qdrant/qdrant`
4. Qdrant UI: `http://localhost:6333/dashboard#/collections`
5. `python -m ipykernel install --user --name=my_openai_env --display-name="OpenAI Project"`
6. run `jupyter notebook`
7. in Jupyter notebook select Python kernel "OpenAI Project"
5. add your OpenAI API key to `keys_secret.py`

### Evaluation retrieval

- present in `evaluation-retrieval.ipynb`
- initial evaluation results using default query parameters: `{'hit_rate': 0.81, 'mrr': 0.43}`
- after evaluating multiple query parameter combinations, results have improuved to:
`{'hit_rate': 0.94, 'mrr': 0.862}` using params: `'score_threshold': 0.7,'limit': 5}`

### Evaluation RAG

Evaluation was done by sending the question, LLM answer and correct answer to LLM using OpenAI 3.5 Turbo.

I evaluated generating the LLM answers separately with `gpt-3.5-turbo`, `gpt-4o-mini` and `gpt-4o`.
LLM answer was generated based on the provided prompt template with FAQ answers as context and the courier profile.

- evaluation code is present in `evaluation-RAD.ipynb`
- evaluation results based on 100 records: 
    - with `gpt-3.5-turbo`:
        ```
        PARTLY_RELEVANT    52
        RELEVANT           37
        NON_RELEVANT       11
        ```
- with `gpt-4o-mini`:
        ```
        RELEVANT           55
        PARTLY_RELEVANT    35
        NON_RELEVANT       10
        ```
- with `gpt-4o`:
        ```
        RELEVANT           51
        PARTLY_RELEVANT    40
        NON_RELEVANT        9

        ```

### Running the Python APP locally

Run commands from root folder:
- use Python v3.10.x
- `pip install pipenv`
- `pipenv shell`
- `pipenv install` to install all dependencies
- optionally run `pipenv requirements > requirements.txt` to regenerate the requirements.txt which is used in the dockerised version of this app
- Start Qdrant: `podman run --rm -p 6333:6333 -p 6334:6334 -v "$(pwd)/tmp_qdrant_storage:/qdrant/storage:z" qdrant/qdrant`
- Qdrant UI: `http://localhost:6333/dashboard#/collections`
- copy and rename `keys_secret.py.tmp` to `app/keys_secret.py`
- fill in `app/keys_secret.py` with the correct secrets
- run `export TOKENIZERS_PARALLELISM=false` to disable now noisy warning
-  `python app/ingest.py` to ingest FAQ and Courier profile data to DBs using
- start API server running one of:
    - `gunicorn --bind 0.0.0.0:9696 --chdir=app server:app`
- run curl commands to interact with entire system:
```sh
$ curl --request POST 'http://127.0.0.1:5000/question' \
--header 'Content-Type: application/json' \
-d '{"question": "Can I keep the provided bike?", "courier_id": 0}'

{
  "answer": "No, you cannot keep the provided bike. The company provides the bike for your use while working, but it must be returned when you are no longer employed or no longer require it for deliveries.",
  "conversation_id": "f22806b91d8845ce86c19897a9eea344"
}
```

```sh
$ curl --request POST 'http://127.0.0.1:5000/feedback' \
--header 'Content-Type: application/json' \
-d '{"conversation_id": "11111111", "positive": true, "feedback": "Good"}'

{
  "message": "Feedback received"
}
```
### Run dockerised verion

- `docker-compose up --build`
- run the `curl` commands from above

### Monitoring

Application is saving conversations data in PostgresDB. Grafana is used to monitor the application in realtime.
Monitoring trtacks:
- courier feedback
- LLM evaluation relevance
- OpenAI tokens
- OpenAI costs
- API tesponse time (including LLM answer generation and LLM evaluation)

![alt text](image.png)

### TODO:

- [x] generate random Delviery courier profiles unsig AI
- [x] persist courier profiles to a NoSQL DB (TinyDb)
- [x] generate random FAQ courier questions unsig AI
- [x] persist FAQ and answers to a Vector DB (Qdrant)
- [x] generate Courier working contracts (employee and freelance) using AI for a file
- [x] generate complete prompt with non private courier profile information, courier question and best matching FAQ data
- [x] use LLM to get an answer
- [x] generate ground truth data for evaluation
- [x] implement evaluation retrieval
- [x] hyperparameter tuning for evaluation retrieval
- [x] implement evaluation RAG
- [x] evaluation of different LLMs for RAG
- [x] put all code behind an API
- [ ] add live LLM evaluation
- [ ] add monitoring
- [x] dockerise application
- [ ] add better logging

Optional:
- [ ] use LLM to ask for Contract data when needed
- [ ] use LLM to ask for more profile information when needed by queying the NoSql DB
- [ ] use LLM to ask for more FAQ data when needed by queying the Vector DB
- [ ] use LLM to update Courier profile 
- [ ] use LLM to add new questions and answers to the FAQ DB
- [ ] add chat history on demand to improuve prompt accuracy
