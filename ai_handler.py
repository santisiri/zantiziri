import openai
from config import SCRIPT_PROMPT

class AIHandler:
    def __init__(self, model):
        self.model = model

    def summarize(self, content):
        """
        Summarizes the given content using OpenAI's API
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes content clearly and concisely."},
                    {"role": "user", "content": f"Please summarize the following content:\n\n{content}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def generate_script(self, summary, custom_prompt=""):
        """
        Generates a script based on the summary and custom prompt
        """
        try:
            # Combine the default prompt template with any custom prompt
            prompt = custom_prompt if custom_prompt else SCRIPT_PROMPT
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": summary}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate script: {str(e)}")

