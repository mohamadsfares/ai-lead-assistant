from app.chunking import load_documents, split_into_chunks
from app.embeddings import embed_texts
from app.db import supabase 


def main():
    docs=load_documents("knowledge_base")
    all_chunks=[]
    for doc in docs:
         all_chunks.extend(split_into_chunks(doc))
    texts=[chunk['text'] for chunk in all_chunks]
    vectors=embed_texts(texts)
    rows=[]
    for chunk, vector in zip(all_chunks, vectors):
        rows.append({
            "source": chunk['source'],
            "section": chunk['section'],
            "content": chunk['text'],
            "embedding": vector
        }
        )
    supabase.table("chunks").delete().neq("id",0).execute()
    supabase.table("chunks").insert(rows).execute()


    print(f"Inserted {len(rows)} chunks")




if __name__ == "__main__":
    main()