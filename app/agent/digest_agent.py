import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance.
"""


class DigestAgent:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = "gemini-2.5-flash"
        self.system_prompt = PROMPT

    def generate_digest(
        self,
        title: str,
        content: str,
        article_type: str,
    ) -> Optional[DigestOutput]:

        try:
            user_prompt = f"""
Create a digest for this {article_type}.

Title:
{title}

Content:
{content[:8000]}
"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=DigestOutput,
                ),
            )

            return DigestOutput.model_validate_json(response.text)

        except Exception as e:
            print(f"Error generating digest: {e}")
            return None

if __name__ == "__main__":
    agent = DigestAgent()

    result = agent.generate_digest(
        title="OpenAI launches a new reasoning model",
        content="""
OpenAI has announced a new reasoning model that improves multi-step
problem solving, coding ability, and agent workflows. The model is
designed for developers building AI applications.
""",
        article_type="article"
    )

    print(result)