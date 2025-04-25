import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional
import json
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_flashcards(
    topic: str,  #WILL CHANGE LATER TO PROJECT FILES
    card_count: int = 10
):
    prompt = f"""
    Create {card_count} flashcards about {topic}.
    
    Format your response as a JSON object with an array of flashcards.
    Each flashcard should have a 'question' and 'answer' field.
    For example: 
    {{
      "flashcards": [
        {{ "question": "What is X?", "answer": "X is Y." }},
        {{ "question": "Who discovered Z?", "answer": "Z was discovered by W." }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model = 'gpt-4o-mini',
        response_format={"type": "json_object"},
        messages=[{"role": "developer", "content": prompt},
                  {"role": "user", "content": "Please generate flashcards based on the topic provided."}],
    )

    response_content = response.choices[0].message.content
    flashcards_data = json.loads(response_content)
    flashcards = flashcards_data.get("flashcards", []) # asking chatgpt to return the flashcards as "flashcards" as a list
    return flashcards
    