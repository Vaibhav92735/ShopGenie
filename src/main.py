import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Create in-memory SQLite DB (or use 'cart.db' to save to file)
conn = sqlite3.connect(":memory:")  # Use 'cart.db' for persistent file
cursor = conn.cursor()

# Create the user_cart table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_cart (
    user_id TEXT,
    product_id TEXT,
    product_name TEXT,
    combined_details TEXT,
    PRIMARY KEY (user_id, product_id)
)
""")
conn.commit()

print("-----------Table Creation Completed------------")

def add_to_cart(user_id, product_id, product_name, combined_details):
    try:
        cursor.execute(
            """
            INSERT INTO user_cart (user_id, product_id, product_name, combined_details)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, product_id, product_name, combined_details)
        )
        conn.commit()
        return {"message": f"Product '{product_name}' added to cart for user {user_id}"}
    except sqlite3.IntegrityError:
        return {"message": f"Product '{product_name}' already in cart for user {user_id}"}

def get_cart(user_id):
    cursor.execute(
        "SELECT product_id, product_name, combined_details FROM user_cart WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    if not rows:
        return {"message": "Cart is empty."}
    products = [
        {"product_id": row[0], "product_name": row[1], "details": row[2]}
        for row in rows
    ]
    return {"user_id": user_id, "products": products}

print("-----------------Starting RAG building----------------")

import getpass
import os

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

import pandas as pd

print("--------------------Loading Datasets-------------------")
df = pd.read_parquet("hf://datasets/philschmid/amazon-product-descriptions-vlm/data/train-00000-of-00001.parquet")

df['combined_text'] = df.apply(
    lambda row: f"About Product: {row['About Product']}\n"
                f"Product Specification: {row['Product Specification']}\n"
                f"Technical Details: {row['Technical Details']}\n"
                f"Description: {row['description']}", axis=1
)

print("-------------------Sentence Transformers---------------")
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Compute embeddings
df['embedding'] = df['combined_text'].apply(lambda x: embed_model.encode(x, convert_to_numpy=True))

import faiss

# Convert embeddings to numpy array
embedding_matrix = np.stack(df['embedding'].values)

# Create FAISS index
index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)


# Remove from Cart function is defined here

def remove_from_cart(user_id, user_input):
    # Step 1: Get all products in the user's cart
    cursor.execute(
        "SELECT product_id, product_name, combined_details FROM user_cart WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Cart is empty. Nothing to remove."}

    # Step 2: Encode user input and all cart items
    input_embedding = embed_model.encode(user_input, convert_to_numpy=True)

    cart_embeddings = []
    product_info = []
    for row in rows:
        combined_text = f"{row[1]} - {row[2]}"  # product_name - combined_details
        cart_embeddings.append(embed_model.encode(combined_text, convert_to_numpy=True))
        product_info.append({
            "product_id": row[0],
            "product_name": row[1],
            "combined_details": row[2]
        })

    # Step 3: Compute cosine similarity
    similarities = cosine_similarity([input_embedding], cart_embeddings)[0]
    best_index = int(np.argmax(similarities))
    best_match = product_info[best_index]

    # Step 4: Remove the most similar product
    cursor.execute(
        "DELETE FROM user_cart WHERE user_id = ? AND product_id = ?",
        (user_id, best_match["product_id"])
    )
    conn.commit()

    return {
        "message": f"Removed product '{best_match['product_name']}' from cart.",
        "matched_details": best_match["combined_details"]
    }

def retrieve_best_product_metadata(user_query, top_k=1):
    query_embedding = embed_model.encode(user_query, convert_to_numpy=True)
    scores, indices = index.search(np.array([query_embedding]), top_k)

    best_match = df.iloc[indices[0][0]]

    return {
        "Uniq Id": best_match["Uniq Id"],
        "Product Name": best_match["Product Name"],
        "Combined Text": best_match["combined_text"]
    }


print("--------------------Intent Recognition configurating---------------------")
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def get_best_product_info(user_query):
    product_info = retrieve_best_product_metadata(user_query)

    prompt = f"""
    You are a helpful assistant. Based on the product details below, summarize how it fits the user's query.

    --- USER QUERY ---
    {user_query}

    --- PRODUCT DETAILS ---
    {product_info['Combined Text']}

    Respond concisely and helpfully.
    """

    response = model.generate_content(prompt, generation_config={"temperature": 0.2})

    return {
        "Uniq Id": product_info["Uniq Id"],
        "Product Name": product_info["Product Name"],
        "Gemini Response": response.text,
        "Combined Text": product_info["Combined Text"]
    }

import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Replace with your actual API key

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Define prompt template
def get_prompt(user_input):
    return f"""
You are an assistant for a shopping app. Your task is to:
1. Identify the user's intent from one of these: ["add the products", "remove the product", "show the products"]
2. Extract and list the products mentioned in the query as a list of strings.

Respond strictly in the following format (JSON-like):
Intent: {{<intent>}}
Products: [<product1>, <product2>, ..., <productN>]

Example Input: "I want a toothpaste, a 1kg horlicks pack and a nail paint of blue color"
Output:
Intent: {{add the products}}
Products: ["toothpaste", "1kg horlicks pack", "nail paint of blue color"]

Now process the following input:
"{user_input}"
"""

# Function to call Gemini and parse response
def extract_intent_and_products(user_input):
    prompt = get_prompt(user_input)
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Parse output
    lines = text.splitlines()
    intent = None
    products = []

    for line in lines:
        if line.lower().startswith("intent:"):
            intent = line.split(":", 1)[1].strip().strip("{}")
        elif line.lower().startswith("products:"):
            products_line = line.split(":", 1)[1].strip()
            try:
                products = eval(products_line)  # Use with caution; assumes well-formed Gemini output
            except:
                pass

    return intent, products

print("--------------------------Making OCR based function------------------------------]")

import google.generativeai as genai
from PIL import Image
import io

# Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini multimodal model (for image + text input)
model = genai.GenerativeModel("gemini-1.5-pro")

# Function to extract user query from image using Gemini OCR
def extract_text_from_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    image = Image.open(io.BytesIO(image_data))

    # Just ask Gemini to extract text from image
    response = model.generate_content(
        [image, "Extract the text content exactly as written from this image."]
    )
    return response.text.strip()

# import whisper

# audio_model = whisper.load_model("tiny")  # Use "small" or "medium" for better accuracy

# # Function to transcribe audio
# def extract_text_from_audio(audio_path):
#     result = audio_model.transcribe(audio_path)
#     return result['text'].strip()

import base64

def extract_text_from_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    prompt = "Please transcribe this audio file to text."

    response = model.generate_content([
        {
            "mime_type": "audio/mp3",  # or audio/wav, adjust as needed
            "data": audio_b64
        },
        prompt
    ])
    
    return response.text.strip()

import os
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from typing import List
import shutil
from pyngrok import ngrok
import nest_asyncio

# Allow running inside Colab
nest_asyncio.apply()

app = FastAPI()

@app.post("/process-image/")
async def process_image(username: str = Form(...), image: UploadFile = File(...)):
    # Save image
    image_path = f"../data/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Extract query
    user_query = extract_text_from_image(image_path)

    # Extract intent and products
    intent, products = extract_intent_and_products(user_query)

    # Get product IDs
    product_ids = []
    for product in products:
        product_info = get_best_product_info(intent + " " + product)
        product_ids.append(product_info)

    # Add to cart if applicable
    if intent == "add the products":
        for p in product_ids:
            add_to_cart(username, p["Uniq Id"], p["Product Name"], p["Combined Text"])
    elif intent == "remove the product":
        for p in products:
            remove_from_cart(username, p)
    elif intent == "show the products":
        cart = get_cart(username)
        return JSONResponse({
            "username": username,
            "query": user_query,
            "intent": intent,
            "products": products,
            "product_ids": product_ids,
            "cart": cart
        })

    return JSONResponse({
        "username": username,
        "query": user_query,
        "intent": intent,
        "products": products,
        "product_ids": product_ids
    })
print("---------------------Image API Build complete----------------------")

@app.post("/process-voice/")
async def process_voice(username: str = Form(...), audio: UploadFile = File(...)):
    # Save audio file
    if not audio.filename:
        return JSONResponse({"error": "No audio file provided."}, status_code=400)

    voice_path = f"../data/{audio.filename}"
    with open(voice_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Extract query from voice
    user_query = extract_text_from_audio(voice_path)
    if not user_query:
        return JSONResponse({"error": "Could not transcribe audio."}, status_code=422)

    # Extract intent and products
    intent, products = extract_intent_and_products(user_query)
    intent = intent.strip().lower()

    # Get product IDs
    product_ids = []
    for product in products:
        product_info = get_best_product_info(f"{intent} {product}")
        product_ids.append(product_info)

    # Handle intent
    if intent == "add the products":
        for p in product_ids:
            add_to_cart(username, p["Uniq Id"], p["Product Name"], p["Combined Text"])
    elif intent == "remove the product":
        for p in products:
            remove_from_cart(username, p)
    elif intent == "show the products":
        cart = get_cart(username)
        return JSONResponse({
            "username": username,
            "query": user_query,
            "intent": intent,
            "products": products,
            "product_ids": product_ids,
            "cart": cart
        })

    # Default response
    return JSONResponse({
        "username": username,
        "query": user_query,
        "intent": intent,
        "products": products,
        "product_ids": product_ids
    })

print("---------------------Voice API Build complete----------------------")

@app.post("/process-text/")
async def process_text(username: str = Form(...), user_query: str = Form(...)):
    user_query = user_query

    # Extract intent and products
    intent, products = extract_intent_and_products(user_query)

    # Get product IDs
    product_ids = []
    for product in products:
        product_info = get_best_product_info(intent + " " + product)
        product_ids.append(product_info)

    # Add to cart if applicable
    if intent == "add the products":
        for p in product_ids:
            add_to_cart(username, p["Uniq Id"], p["Product Name"], p["Combined Text"])
    elif intent == "remove the product":
        for p in products:
            remove_from_cart(username, p)
    elif intent == "show the products":
        cart = get_cart(username)
        return JSONResponse({
            "username": username,
            "query": user_query,
            "intent": intent,
            "products": products,
            "product_ids": product_ids,
            "cart": cart
        })

    return JSONResponse({
        "username": username,
        "query": user_query,
        "intent": intent,
        "products": products,
        "product_ids": product_ids
    })

print("---------------------Text API Build complete----------------------")