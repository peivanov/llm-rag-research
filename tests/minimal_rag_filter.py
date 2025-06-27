import json
from sentence_transformers import SentenceTransformer
import faiss
import ollama

# Load company policies from JSON
with open('policy.json', 'r') as f:
    data = json.load(f)
    docs = data['policies']

# Embed policies
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model.encode(docs)

# Create FAISS index
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

# Function to check prompt
def is_prompt_safe(prompt, k=2, threshold=0.6):
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

# Example usage
user_prompt = ["Here is our API key: test_key...",
"What is the time in New York?",
"""
        def _generate_key(self, password):
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'supersecretsalt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
""",
"""
    def convert_ip_int_to_string(self, ip_int):
        return str(ipaddress.ip_address(int(ip_int)))
"""]

for prompt in user_prompt:
    decision = is_prompt_safe(prompt)
    print("LLM says:", decision)
                                                                                                                                                                                          63,1          Bot
