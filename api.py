from fastapi import FastAPI
from pydantic import BaseModel

from pii_detection_agent import PIIDetectionAgent

app = FastAPI()
agent = PIIDetectionAgent()

class PIIItem(BaseModel):
    text: str

@app.post("/pii_scan")
async def pii_scan(pii_input: PIIItem):
    text = pii_input.text
    openai_response = agent.detect_client_information(text)
    return agent.format_output(openai_response)