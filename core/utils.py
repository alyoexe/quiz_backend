import fitz  # PyMuPDF
import openai
import os
from dotenv import load_dotenv
load_dotenv()


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# Set Groq credentials
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"


def generate_mcqs_from_text(text, num_questions=5):
    prompt = f"""Generate exactly {num_questions} multiple choice questions from this text. For each question, provide 4 options and mark the correct answer.

Text to generate questions from:
{text}

Respond in this exact JSON format with no additional text:
[
    {{
        "question": "What is...",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "answer": "a"
    }}
]"""

    try:
        response = openai.ChatCompletion.create(
            model="llama-3.1-8b-instant",  # Using Groq's Mixtral model
            messages=[{
                "role": "system",
                "content": "You are a quiz generator that always responds with valid JSON containing multiple choice questions."
            },
            {
                "role": "user",
                "content": prompt
            }],
            temperature=0.7
        )
        import json
        content = response['choices'][0]['message']['content'].strip()
        # Remove any markdown code block markers if present
        content = content.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print("Error generating questions:", str(e))
        return []
