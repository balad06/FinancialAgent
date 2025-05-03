# nvidia_chat.py

from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
import asyncio

class NvidiaChatClient:
    def __init__(self, api_key: str, base_url: str = "https://integrate.api.nvidia.com/v1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1"

    async def insights(self,finances:list ,temperature =0.0,top_p=0.95,max_tokens=4096):
        prompt = f"<s>[INST] You are a financial expert. Provide insights of the transaction by the user that help in reducing unwanted costs and where the person spends the most\n\nContext: {finances} [/INST]</s>"

        print(prompt)

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
    def stream_chat(self, system_prompt: str, user_prompt: str, temperature=0.0, top_p=0.95, max_tokens=4096):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        completion = self.client.responses.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
