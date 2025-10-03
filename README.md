# llm-project
LLM capstone project for the LLM training


#### Architecture design
![Architecture design](architecture_design.png)



### Run

1. pipenv shell
2. pipenv install
3. Start Qdrant: `podman run --rm -p 6333:6333 -p 6334:6334 -v "$(pwd)/tmp_qdrant_storage:/qdrant/storage:z" qdrant/qdrant`
4. Qdrant UI: `http://localhost:6333/dashboard#/collections`
5. python -m ipykernel install --user --name=my_openai_env --display-name="OpenAI Project"
6. jupyter notebook
7. select Python kernel "OpenAI Project"
