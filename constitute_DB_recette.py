from langchain_community.document_loaders import TextLoader
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain

import os
import torch




device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")


API_KEY = os.getenv("MISTRAL_API_KEY")

loader =  TextLoader("text.txt")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter()
split_docs = splitter.split_documents(docs)
embeddings = MistralAIEmbeddings(model = "mistral-embed", api_key=API_KEY)

vector = FAISS.from_documents(split_docs, embeddings)

print("Vector store created")
print(vector)

