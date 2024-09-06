from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

def run_llm(prompt, model, temperature=1):
  completion = client.chat.completions.create(
    model=model,
    temperature=temperature,
    response_format={"type": "json_object"},
    messages=[
      {"role": "user", "content": prompt}
    ]
  )
  return completion.choices[0].message.content
