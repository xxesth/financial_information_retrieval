import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import fitz  # PyMuPDF
import threading
from concurrent.futures import ThreadPoolExecutor

class PdfTextProcessor:
    def __init__(self, language='turkish'):
        try:

            nltk.download('stopwords')
            nltk.download('punkt')
            self.stop_words = list(stopwords.words(language))
        except Exception as e:
            print(f"Error downloading NLTK data: {e}")
            self.stop_words = []

    def preprocess(self, json_content):
        pages_content = []
        for page in json_content['pages']:
            content = ""
            paragraphs = page.get('paragraphs', [])
            for paragraph in paragraphs:
                content += paragraph + "\n"
            tables = page.get('tables', [])
            for table in tables:
                table_str = " | ".join(table)
                content += table_str + "\n"
            pages_content.append(content.strip())
        return pages_content

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
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            top_similarities = similarities[top_indices]
            return top_indices, top_similarities
        except Exception as e:
            print(f"An error occurred while finding the most relevant page: {e}")
            return [], []

    def get_relevant_page(self, json_content, question, top_n=3):
        try:
            pages_content = self.preprocess(json_content)
            page_vectors, question_vector = self.vectorize_text(pages_content, question)
            if page_vectors is None or question_vector is None:
                return [], [], []

            top_indices, top_similarities = self.find_most_relevant_page(page_vectors, question_vector, top_n)
            top_pages = [pages_content[i] for i in top_indices]
            return top_pages, top_similarities, top_indices
        except Exception as e:
            print(f"An error occurred while getting the relevant page: {e}")
            return [], [], []

    def get_most_relevant_two_pages(self, pdf_path, question):
        try:
            doc = fitz.open(pdf_path)
            json_content = {'pages': []}
            for page_num in range(len(doc)):
                page_text = doc.load_page(page_num).get_text()
                json_content['pages'].append({'paragraphs': [page_text]})
            
            relevant_pages, similarities, indices = self.get_relevant_page(json_content, question, 2)
            if len(relevant_pages) == 2:
                return relevant_pages[0], relevant_pages[1], similarities, indices
            elif len(relevant_pages) == 1:
                return relevant_pages[0], None, similarities, indices
            else:
                return None, None, None, None
        except Exception as e:
            print(f"An error occurred while getting the most relevant two pages: {e}")
            return None, None, None, None