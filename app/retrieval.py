from app.embeddings import embed_texts
from app.db import supabase


def search(question, k=3):
    query_vector = embed_texts([question])[0]
    result=supabase.rpc("match_chunks", {"query_embedding": query_vector, "match_count": k}).execute()
    return result.data


if __name__ == "__main__":
    results = search("Do you offer a discount for seniors?", k=3)
    for chunk in results:
        print(chunk["source"], "|", chunk["section"], "|", round(chunk["similarity"], 2))
