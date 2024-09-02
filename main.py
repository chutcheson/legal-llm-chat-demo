
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
from llm import run_llm  # Import the run_llm function
import traceback

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

@app.post("/generate-response")
async def generate_response(request: TextRequest):
    try:
        prompt = f"""Respond in json as below:
        {{
            "response": <answer>
        }}

        Based on the following text, provide a detailed legal analysis or advice:
        {request.text}
        """

        print(f"Sending prompt to LLM: {prompt}")  # Log the prompt
        llm_response = run_llm(prompt, "gpt-4o")
        print(f"Received response from LLM: {llm_response}")  # Log the raw response

        parsed_response = json.loads(llm_response)
        
        if "response" not in parsed_response:
            raise ValueError("LLM response does not contain 'response' key")
        
        return {"response": parsed_response["response"]}
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        print(f"Raw LLM response: {llm_response}")
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in generate_response: {str(e)}")
        print(traceback.format_exc())  # This will print the full stack trace
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

def process_text_with_llm(text: str):
    prompt = f"""You are an AI assistant helping lawyers interact with language models. Your task is to analyze a given paragraph related to a legal problem and identify generic phrases that could be replaced with more specific alternatives. Be comprehensive, the user will benefit from a lot of options. A lot of lawyers aren't good at thinking through how to give information to language models to make their responses from them more useful.

    Focus on the legally relevant or important sections of the question. Clarification on these is going to be the most helpful to the user.

    For each identified phrase, provide 2-3 more specific alternatives. The output should be in a structured JSON format.

    Here's an example:

    Input: "I have an employee as a client who is important within a company. He took a business opportunity that might have gone to the company for himself. He is located in the United States. What is his liability?"

    Output:
    {{
        "parts": [
            {{"type": "text", "content": "I have an employee as a client who is "}},
            {{"type": "dropdown", "options": ["an officer", "a director", "a senior employee"], "selected": "important"}},
            {{"type": "text", "content": " within a company. He took a business opportunity that might have gone to the company for himself. He is located in the "}},
            {{"type": "dropdown", "options": ["State of California", "State of New York", "United States"], "selected": "United States"}},
            {{"type": "text", "content": ". What is his liability?"}}
        ]
    }}

    Now, analyze the following text and provide a similar JSON output:

    {text}

    Ensure that your response is a valid JSON object with a 'parts' key containing an array of text and dropdown objects. Each dropdown object should have 'options' and 'selected' keys.
    """

    try:
        print(f"Sending prompt to LLM: {prompt}")  # Log the prompt

        llm_response = run_llm(prompt, "gpt-4o")
        print(f"Received response from LLM: {llm_response}")  # Log the raw response

        parsed_response = json.loads(llm_response)
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        print(f"Raw LLM response: {llm_response}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM response")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())  # This will print the full stack trace
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/process-text")
async def process_text(request: TextRequest):
    try:
        result = process_text_with_llm(request.text)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
