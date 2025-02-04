import json
import os
import nltk
import matplotlib.pyplot as plt
import seaborn as sns

from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure VADER Lexicon is downloaded
nltk.download("vader_lexicon")

# Fake diverse reviews
arrayReview = [
    "I love this product! It is amazing!",
    "I hate this product! It is terrible!",
    "I am indifferent about this product. It is okay.",
    "The quality is fantastic, and I highly recommend it.",
    "Worst purchase ever! Do not buy this.",
    "It works fine, but nothing extraordinary.",
    "Amazing customer service! They resolved my issue instantly.",
    "The shipping took forever, but the product is decent.",
    "I’ve had better, but it’s not the worst either.",
    "Great value for money, I’m really happy with it."
]
sia = SentimentIntensityAnalyzer()

def generate_sentiment_graph():
    scores = [sia.polarity_scores(review)["compound"] for review in arrayReview]
    
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=range(len(scores)), y=scores, hue=scores, palette="coolwarm", s=100)
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel("Review Index")
    plt.ylabel("Sentiment Score (Compound)")
    plt.title("Sentiment Analysis - Cloud Point Graph")
    
    graph_path = "./sentiment_graph.png"
    plt.savefig(graph_path)
    plt.close()
    
    return graph_path

def handler(event, context):
    """
    AWS Lambda function to analyze sentiment of multiple reviews using VADER.
    """
    try:
        # Analyze all fake reviews
        graph_path = generate_sentiment_graph()

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Graph generated successfully.", "graph_path": graph_path})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
