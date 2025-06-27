import json
from sentence_transformers import SentenceTransformer
import faiss
import ollama

# Load company policies from JSON
with open('company_policy_old.json', 'r') as f:
    data = json.load(f)

# Flatten the policies into a single list of strings
docs = data['policies']['Sensitive'] + data['policies']['Permissible']

# Embed policies
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model.encode(docs)

# Create FAISS index
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

# Function to check prompt
def is_prompt_safe(prompt, k=2, threshold=0.8):  # Adjusted threshold for stricter filtering
    prompt_embedding = model.encode([prompt])
    D, I = index.search(prompt_embedding, k)
    most_similar = [docs[i] for i in I[0]]

    context = "\n".join(most_similar)
    full_prompt = f"""You are a security filter for employee AI prompts.
Context:
{context}

Is the following prompt safe to send to a public AI provider? Only say 'Yes' or 'No' and briefly explain.

Prompt:
{prompt}
"""

    print(full_prompt)

    response = ollama.chat(model='llama3:instruct', messages=[{"role": "user", "content": full_prompt}])
    return response['message']['content']

# Load user prompt from a file
with open('user_prompt.txt', 'r') as f:
    user_prompt = f.read()

decision = is_prompt_safe(user_prompt)
print("LLM says:", decision)

