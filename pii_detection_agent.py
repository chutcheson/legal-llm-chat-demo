"""PII Detection Agent"""
import os
import glob
from pathlib import Path
from typing import Dict, List

from openai import OpenAI
from sentence_transformers import SentenceTransformer
import PyPDF2

import faiss

from dotenv import load_dotenv
load_dotenv()


def chunk_text(text):
    #TODO: create a better chunking system
    return list(filter(lambda x: len(x) > 30, text.split(".")))
    

class PIIDetectionAgent:
    def __init__(self, pdf_directory: Path = "./data") -> None:
        self.pdf_directory = pdf_directory
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        self.client_data = self._extract_client_content()
        self._construct_faiss_index()

    def _extract_client_content(self) -> List[Dict[str, str]]:
        client_names = list(os.walk(self.pdf_directory))[0][1]
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

    def _construct_faiss_index(self):
        self.all_chunks = []
        self.chunk_idx_to_name = []
        for client_name, content in self.client_data.items():
            chunks = chunk_text(content["content"])
            self.chunk_idx_to_name.extend([client_name for _ in chunks])
            self.all_chunks.extend(chunks)
        corpus_embeddings = self.encoder.encode(self.all_chunks, convert_to_tensor=True)
        self.index = faiss.IndexFlatL2(corpus_embeddings.shape[1])
        self.index.add(corpus_embeddings.cpu().numpy().astype('float32'))


    def detect_client_information(self, input_text: str, k: int = 5) -> str:
        input_embedding = self.encoder.encode([input_text])
          # number of nearest neighbors to retrieve
        distances, indices = self.index.search(input_embedding.astype('float32'), k)
        distances = distances[0]
        context = "Potential matching clients:\n"
        for i, idx in enumerate(indices[0]):
            context += f"{i+1}. Client Name: {self.chunk_idx_to_name[idx]}\n"
            context += f"Similarity Score: {distances[i]}\n"
            context += f"Excerpt: {self.all_chunks[idx][:500]}...\n\n"

        prompt = f"""
        Analyze the following input text and compare it to the provided potential matching clients from PDF files. 
        Determine if the input text could be describing one of these clients with altered or masked PII.

        Input text: {input_text}

        {context}

        Respond with:
        - 'High Match' if you're confident the input text is describing one of these clients
        - 'Potential Match' if there are similarities but it's not certain
        - 'Low Match' if the input text doesn't seem to closely match any of these clients

        Provide a brief explanation for your assessment, including which client(s) it might match and why.

        Assessment:

        Client(s) Matched:
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            temperature = 0,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    def format_output(self, openai_response: str):
        #TODO: have a better output formatter
        tagged = False
        if 'High Match' in openai_response or 'Potential Match' in openai_response:
            tagged = True
        
        tagged_client_names = []
        for client_name in self.client_data.keys():
            if client_name in openai_response:
                tagged_client_names.append(client_name)
        
        return {"tagged": tagged, "clients": tagged_client_names}

if __name__ == "__main__":
    agent = PIIDetectionAgent()
    print(agent.detect_client_information("the client reported revenue of 50.2 billion"))
