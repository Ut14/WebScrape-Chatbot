# -*- coding: utf-8 -*-
"""Chatbot

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f-3bmQ6a0VaFayFpj73xMQ6v3u2AvNfj
"""

# !pip install langchain
# !pip install huggingface_hub
# !pip install sentence_transformers
# !pip install selenium beautifulsoup4
# !apt-get update
# !apt install chromium-chromedriver
# !apt-get install -y chromium-browser
# !pip install langchain-community langchain-core

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from webdriver_manager.chrome import ChromeDriverManager

!ls /usr/lib/chromium-browser/chromedriver

options=webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

"""# Get HUGGINGFACEHUB_API_KEY"""

import os
from getpass import getpass
HuggingFaceHub_API_KEY = getpass()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HuggingFaceHub_API_KEY

url = 'https://botpenguin.com'
driver.get(url)

# Get the page source
page_source = driver.page_source

# Use BeautifulSoup to parse the page source
soup = BeautifulSoup(page_source, 'html.parser')

# Extract all text content
text_content = soup.get_text(separator='\n')

# Clean up the text content
cleaned_text = re.sub(r'\n\s*\n', '\n\n', text_content)  # Remove excessive new lines
cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space

# Print the cleaned text content
print(cleaned_text)

driver.quit()

with open('cleaned_text.txt', 'w') as f:
    f.write(cleaned_text)

from langchain.document_loaders import TextLoader
loader = TextLoader('./cleaned_text.txt')
documents = loader.load()

document_text = documents[0].page_content  # Access the text content
print(len(document_text))

#Text Splitter
# from langchain.text_splitter import CharacterTextSplitter
# text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
# texts = text_splitter.split_documents(documents)

# print(f"Number of chunks: {len(texts)}")
# for i, text in enumerate(texts):
#     print(f"Chunk {i + 1} length: {len(text.page_content)}")

from langchain.docstore.document import Document

# Function to split text into chunks
def split_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return [Document(page_content=chunk) for chunk in chunks] # Create Document objects for each chunk

# Split the text
texts= split_text(document_text, 1000)
len(texts)

from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings()

# !pip install faiss-cpu

from langchain.vectorstores import FAISS
db = FAISS.from_documents(texts, embeddings)

query="Why is BotPenguin good?"
docs = db.similarity_search(query)

print((str(docs[0].page_content)))

"""# Create QnA Chain"""

from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub

llm=HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature":0.1, "max_length":512})

chain=load_qa_chain(llm, chain_type="stuff")

print("Bot: Hello I am Bot. How can I help you?(type exit to quit)")
while True:
  query=input("User: ")
  if query.lower()=="exit":
    print("Bot: Bye Bye")
    break
  answer = chain.run(input_documents=docs, question=query)
  answer=re.sub(r'\n+', '\n', answer)
  print("Bot: ", answer)

