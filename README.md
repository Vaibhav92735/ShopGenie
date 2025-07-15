# 🛒 ShopGenie – Agentic Shopping Assistant

> A smart assistant to simplify shopping via natural language and multimodal interactions.  
> Built for Walmart Sparkathon.

---

## 👥 Team Members

- **Vaibhav Gupta**
- **Ambati Rahul Reddy**
- **Akarsh Katiyar**

🎥 [Watch Demo on YouTube](https://youtu.be/sW8fQmjzXF8)  
💻 [View Source on GitHub](https://github.com/Vaibhav92735/ShopGenie.git)

---

## 🧠 Problem Statement

Traditional shopping often involves mentally or physically maintaining a list. This process can be inefficient, especially in hands-busy or accessibility-constrained scenarios. ShopGenie addresses this by creating an **Agentic Tool Calling Framework** that:

- Interprets user instructions via **text, voice, or images**
- Identifies **user intent** (add/remove/view)
- Dynamically updates a personalized shopping cart

With features like **Natural Language Understanding**, **RAG**, and **multi-modal inputs**, ShopGenie makes shopping as seamless as talking to a real shopkeeper—with AI precision.

---

## ✅ Problems Solved

- Eliminates the need for handwritten or mental shopping lists.
- Supports **voice and image input** for enhanced accessibility.
- Avoids rigid UI—users interact naturally using language.
- Uses **Retrieval-Augmented Generation (RAG)** to fetch relevant product info.
- Ensures persistent, personalized cart management across devices.

---

## 🧩 Approach & Architecture

### 1. 📚 Dataset Acquisition
- **Product Dataset** (from HuggingFace): Contains product names, descriptions, colors, etc.
- **SFT Dataset**: Used to fine-tune the intent recognition model.

> Sources:  
> 🔗 https://huggingface.co/datasets/philschmid/amazon-product-descriptions-vlm  
> 🔗 https://huggingface.co/datasets/bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset

---

### 2. 🗃️ Database Design

Each user has a personalized cart storing:

- `product_id`
- `product_name`
- `product_description`
- Attributes (e.g., color, size)

#### Tool Functions

- `add_to_cart(user_id, product_id)`
- `remove_from_cart(user_id, product_id)`
- `show_cart(user_id)`

These are invoked dynamically by the agent based on recognized intent.

---

### 3. 🔍 Retrieval-Augmented Generation (RAG)

- Implemented using **Gemini**
- Retrieves product data from a vector store
- Provides **context-rich, grounded responses**

---

### 4. 🧠 Intent Recognition via LLM Fine-Tuning

- Fine-tuned **LLaMA 3B** using **Supervised Fine-Tuning**
- Integrated **LoRA adapters** and **8-bit quantization** for efficient training
- Maps user query to tool functions with high accuracy

---

### 5. 🎤🖼️ Multi-Modal Input Handling

- **OCR**: Extracts text from images like handwritten lists using Gemini
- **Audio**: Transcribes user voice commands to actionable queries

---

## 🧾 Conclusion

ShopGenie is a complete AI-driven shopping assistant that offers:

- Natural, intuitive interaction
- Personalized cart management
- Rich product search and retrieval
- Accessibility through multimodal input

> Imagine a virtual shopkeeper who understands what you say, sees what you show, and remembers what you want. That's ShopGenie.

---

## 📎 Links

- 🔗 [YouTube Demo](https://youtu.be/sW8fQmjzXF8)
- 💻 [GitHub Repository](https://github.com/Vaibhav92735/ShopGenie.git)

---

## 📌 Technologies Used

- Python, FastAPI
- HuggingFace Datasets
- LLaMA 3B (SFT + LoRA)
- Gemini API (OCR + RAG + STT)
- SQLite (Cart Storage)

---

