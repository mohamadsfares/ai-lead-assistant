from dotenv import load_dotenv 
from openai import OpenAI

load_dotenv()
client = OpenAI(timeout=30)
EMBEDDING_MODEL="text-embedding-3-small"


def embed_texts(texts):
    response=client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    vectors=[item.embedding for item in response.data]
    return vectors


if __name__=="__main__":
    vectors=embed_texts(["How much is a new roof?","Do you install solar panels?"])
    print(len(vectors))
    print(len(vectors[0]))
    print(vectors[0][:5])