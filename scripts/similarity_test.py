from app.embeddings import embed_texts


def similarity(a,b):
    return sum(x*y for x,y in zip(a,b))


question = "How much does it cost to redo my roof?"
chunk_a = "Price Ranges > Roofing\nAsphalt shingle roof replacement : $9,500 to $22,000"
chunk_b = "Warranty > Roofing Warranty\nWorkmanship warranty on roof replacements: 10 years."


vectors =embed_texts([question, chunk_a, chunk_b])


q_vec = vectors[0]
a_vec = vectors[1]
b_vec = vectors[2]

print("Question vs Price chunk: ",similarity(q_vec, a_vec))
print("Question vs Warranty chunk: ",similarity(q_vec, b_vec))