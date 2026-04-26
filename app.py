from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os

# Fix HuggingFace tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)


load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
GROQ_API_KEY=os.environ.get('GROQ_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot" 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)




retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Using FREE Groq instead of OpenAI - 14,400 free requests per day!
chatModel = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=200  # Reasonable response length
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)



@app.route("/")
def index():
    return render_template('chat.html')



@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form["msg"]
        input = msg
        print(f"User query: {input}")
        
        # Add basic input validation
        if not msg or len(msg.strip()) == 0:
            return "Please enter a valid question."
        
        if len(msg) > 500:  # Limit input length to control costs
            return "Please keep your question under 500 characters."
        
        response = rag_chain.invoke({"input": msg})
        print("Response : ", response["answer"])
        return str(response["answer"])
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
            return "Sorry, the service is temporarily unavailable due to usage limits. Please try again later or contact support."
        elif "insufficient_quota" in str(e).lower():
            return "The API quota has been exceeded. Please check your OpenAI account billing and usage limits."
        else:
            return "Sorry, there was an error processing your request. Please try again."



if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)
