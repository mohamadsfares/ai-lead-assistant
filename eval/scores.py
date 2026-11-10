from eval.run_eval import questions 
from app.retrieval import search


rows = []
for q in questions:
    chunks=search(q["question"])
    best=chunks[0]["similarity"]
    rows.append((round(best, 2), q["id"], q["type"]))


for row in sorted(rows):
     print(row)
