import os
from pathlib import Path
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv
# pyrefly: ignore[missing-import]
from groq import Groq
# pyrefly: ignore[missing-import]
from deepeval.models import DeepEvalBaseLLM

load_dotenv(Path(__file__).parent.parent / "chatbot" / ".env")

class GroqJudge(DeepEvalBaseLLM):

    def __init__(self, model_name):
        self.model_name = model_name
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        super().__init__(model_name)

    def load_model(self):
        return self.client

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model = self.model_name,
            temperature=0,
            messages=[{"role":"user","content": prompt}]
        )
        return response.choices[0].message.content

    async def a_generate(self , prompt):
        return self.generate(prompt)

    def get_model_name(self):
        return self.model_name
