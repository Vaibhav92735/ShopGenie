from datasets import load_dataset
from trl import SFTConfig, SFTTrainer, FastLanguageModel
from transformers import AutoTokenizer
from dotenv import load_dotenv
import os

load_dotenv()

# Load dataset
dataset = load_dataset("bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset", split="train")

# Hyperparameters
max_seq_length = 2048
dtype = "auto"
load_in_8bit = True

# Load model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_8bit=load_in_8bit,
    token=os.getenv("HUGGING_FACE_API_TOKEN"),
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# Training config
training_args = SFTConfig(
    packing=True,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    save_strategy="epoch",
    logging_steps=10,
    output_dir="outputs",
)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=training_args,
)

trainer.train()