import os
from transformers import pipeline

def download_model():
    """
    Downloads the sentiment analysis model from Hugging Face
    and saves it to a local directory.
    """
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    local_path = "/app/models/sentiment-model"

    if not os.path.exists(local_path):
        print(f"Downloading model '{model_name}' to '{local_path}'...")
        # Use a pipeline to download and cache the model and tokenizer
        sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
        sentiment_pipeline.save_pretrained(local_path)
        print("Model download complete.")
    else:
        print("Model already downloaded.")

if __name__ == "__main__":
    download_model()
