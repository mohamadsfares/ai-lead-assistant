from pathlib import Path


def load_documents(folder):
    documents = []
    for file_path in Path(folder).glob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        documents.append({"source":file_path.name,"text":text})
    return documents
def split_into_chunks(document):
    chunks= []
    parts = document['text'].split("\n## ")
    doc_title= parts[0].split("\n")[0].strip("#").strip()
    for part in parts:
        lines=part.strip().split("\n", 1)
        heading=lines[0].strip("#").strip()
        body=lines[1].strip() if len(lines)>1 else ""
        if body=="":
            continue
        chunks.append({"source":document['source'],"section":heading,"text": f"{doc_title} > {heading}\n{body}"})
    return chunks


if __name__ == "__main__":
    docs=load_documents("knowledge_base")
    all_chunks=[]
    for doc in docs:
        all_chunks.extend(split_into_chunks(doc))
    print(len(all_chunks))
    print(all_chunks[0])