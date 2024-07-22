import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import extract_report_json
import os
import random

class BildirimTextProcessor:
    def __init__(self, language='turkish'):
        try:
            nltk.data.path.append('/Users/ygzhkki/nltk_data')

            # Download stopwords for the specified language
            nltk.download('stopwords')
            nltk.download('punkt')
            self.stop_words = list(stopwords.words(language))
        except Exception as e:
            print(f"Error downloading NLTK data: {e}")
            self.stop_words = []

    # Document preprocessing
    def preprocess(self, json_doc):
        try:
            # Load JSON data
            with open(json_doc, 'r', encoding='utf-8') as file:
                data = json.load(file)

            pages_content = []
            
            
            text_string = ""

            # Extract text data
            text_data = data["yazi"]
            for title, content in text_data.items():
                text_string += f"{title}:\n{json.dumps({title: content}, indent=4, ensure_ascii=False)}\n\n"

            pages_content.append(text_string.strip())
            
            # Extract table data 
            table_data = data["tablo"]
            for title, content in table_data.items():
                table_string= ""
                table_string += f"{title}:\n{json.dumps(content, indent=4, ensure_ascii=False)}\n\n"
                pages_content.append(table_string.strip())
            

            return pages_content
        except FileNotFoundError:
            print(f"File {json_doc} not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {json_doc}.")
            return []
        except Exception as e:
            print(f"An error occurred while preprocessing the document: {e}")
            return []

    # Convert text to TF-IDF vectors
    def vectorize_text(self, pages_content, question):
        try:
            vectorizer = TfidfVectorizer(stop_words=self.stop_words, tokenizer=word_tokenize)
            vectors = vectorizer.fit_transform(pages_content + [question])
            page_vectors = vectors[:-1]
            question_vector = vectors[-1]
            return page_vectors, question_vector
        except Exception as e:
            print(f"An error occurred while vectorizing the text: {e}")
            return None, None
        
    def find_most_relevant_page(self, page_vectors, question_vector, top_n):
        try:
            similarities = cosine_similarity(question_vector, page_vectors).flatten()
            top_indices = np.argsort(similarities)[-top_n:][::-1]  # Get the indices of the top N similarities
            top_similarities = similarities[top_indices]  # Get the top N similarity scores
            return top_indices, top_similarities
        except Exception as e:
            print(f"An error occurred while finding the most relevant page: {e}")
            return [], []
        
    # Main function to retrieve relevant page content
    def get_relevant_page(self, json_doc, question, top_n=3):
        try:
            pages_content = self.preprocess(json_doc)
            if not pages_content:
                return [], [], []

            page_vectors, question_vector = self.vectorize_text(pages_content, question)
            if page_vectors is None or question_vector is None:
                return [], [], []

            top_indices, top_similarities = self.find_most_relevant_page(page_vectors, question_vector, top_n)
            top_pages = [pages_content[i] for i in top_indices]
            return top_pages, top_similarities, top_indices
        except Exception as e:
            print(f"An error occurred while getting the relevant page: {e}")
            return [], [], []

    def get_most_relevant_two_pages(self, json_path, question):
        try:
            relevant_pages, similarities, indices = self.get_relevant_page(json_path, question, 2)

            if len(relevant_pages) == 2:
                return relevant_pages[0], relevant_pages[1], similarities, indices
            elif len(relevant_pages) == 1:
                return relevant_pages[0], None, similarities, indices
            else:
                return None, None, None, None
        except Exception as e:
            print(f"An error occurred while getting the most relevant two pages: {e}")
            return None, None, None, None

