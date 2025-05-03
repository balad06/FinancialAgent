# nvidia_chat.py

from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
import asyncio
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np


class NvidiaChatClient:
    def __init__(self, api_key: str, base_url: str = "https://integrate.api.nvidia.com/v1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1"
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.id_map = {}

    async def insights(self,finances:list ,temperature =0.0,top_p=0.95,max_tokens=4096):
        prompt = f"<s>[INST] You are a financial expert. Provide insights of the transaction by the user that help in reducing unwanted costs and where the person spends the most\n\nContext: {finances} [/INST]</s>"

 

        completion = await asyncio.to_thread(self.client.chat.completions.create, 
                                         model=self.model,
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=temperature,
                                         top_p=top_p,
                                         max_tokens=max_tokens)
        # for chunk in completion:
            # if chunk.choices[0].delta.content:
                # yield chunk.choices[0].delta.content
                
        return completion.choices[0].message.content
    def load_saved_index(self):
        # Load FAISS index
        self.index = faiss.read_index(r"./faiss_transactions.index")

        # Load id_map (assumes pickle; change if it's JSON)
        with open(r"./doc_id_map.pkl", "rb") as f:
            self.id_map = pickle.load(f)
        
    async def stream_chat(self, system_prompt: str, user_prompt: str, temperature=0.0, top_p=0.95, max_tokens=4096):
        query_vector = self.embed_model.encode([user_prompt])
        _, I = self.index.search(np.array(query_vector), k=5)
        context = "\n".join([self.id_map[i] for i in I[0]])

        # Step 2: Build message
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_prompt}"}
        ]

        completion = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )

        return completion.choices[0].message.content
