import google.generativeai as genai
import chromadb
import sys

print("Python executable:", sys.executable)
try:
    print("Generative AI Version:", genai.__version__)
    print("ChromaDB Version:", chromadb.__version__)
    print("SUCCESS: Libraries are installed correctly!")
except Exception as e:
    print("ERROR:", e)