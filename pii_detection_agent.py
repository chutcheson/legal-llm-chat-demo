"""PII Detection Agent"""
import os
import glob
from pathlib import Path
from typing import Dict, List

from openai import OpenAI
from sentence_transformers import SentenceTransformer
import PyPDF2

from dotenv import load_dotenv
load_dotenv()


class PIIDetectionAgent:
    def __init__(self, pdf_directory: Path = "./data") -> None:
        self.pdf_directory = pdf_directory
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        self.client_data = self._extract_client_content()

    def _extract_client_content(self) -> List[Dict[str, str]]:
        client_names = [x[0] for x in os.walk(self.pdf_directory)]
        client_data = {}
        for client_name in client_names:
            directory_path = os.path.join(self.pdf_directory, client_name)
            content = ""
            for pdf_file in glob.glob(os.path.join(directory_path, "*.pdf")):
                with open(pdf_file, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
            client_data[client_name] = {
                "content": content
            }
        
        return client_data

if __name__ == "__main__":
    agent = PIIDetectionAgent()
