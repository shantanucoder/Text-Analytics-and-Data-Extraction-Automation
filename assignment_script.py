# -*- coding: utf-8 -*-
"""Test-Assignment

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Vz5oBqt4PnSeKEwtZH9MxrtPE4Jeina3
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

from textblob import TextBlob
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize # Import sent_tokenize

import os

#2	Data Extraction

input_df = pd.read_excel('data/Input.xlsx')
urls = input_df['URL']
input_df.head()

for index, url in enumerate(urls):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title and article text
        title = soup.find('h1').get_text(strip=True)
        article_text = soup.find('article').get_text(strip=True)

        # Save the data to a text file
        url_id = input_df['URL_ID'][index]
        file_path = f"data/extracted_articles/{url_id}.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"{title}\n{article_text}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# Combine all stop words into a single set
stop_words = set()

# Load stop words from the StopWords folder
stop_words_files = [
    'StopWords/StopWords_Auditor.txt',
    'StopWords/StopWords_Currencies.txt',
    'StopWords/StopWords_DatesandNumbers.txt',
    'StopWords/StopWords_Generic.txt',
    'StopWords/StopWords_GenericLong.txt',
    'StopWords/StopWords_Geographic.txt',
    'StopWords/StopWords_Names.txt'
]

for file_path in stop_words_files:
    with open(file_path, 'r', encoding='latin-1') as file:
        stop_words.update(file.read().splitlines())

# Load master dictionary
positive_words = set()
negative_words = set()

with open('MasterDictionary/positive-words.txt', 'r') as file:
    positive_words = set(word for word in file.read().splitlines() if word not in stop_words)

with open('MasterDictionary/negative-words.txt', 'r', encoding='latin-1') as file:
    negative_words = set(word for word in file.read().splitlines() if word not in stop_words)

# Function to determine if a word is "complex"
def is_complex_word(word):
    vowels = "aeiou"
    syllables = sum(1 for char in word.lower() if char in vowels)
    return syllables > 2

# Function to count syllables in a word
def count_syllables(word):
    vowels = "aeiou"
    return sum(1 for char in word.lower() if char in vowels)

# Function to count personal pronouns
def count_personal_pronouns(text):
    personal_pronouns = {"i", "we", "my", "ours", "us"}
    tokens = word_tokenize(text.lower())
    return sum(1 for token in tokens if token in personal_pronouns)

# Function to clean and tokenize text
def clean_and_tokenize(text):
    words = word_tokenize(text.lower())  # Tokenize and lowercase
    tokens = [word for word in words if word.isalpha() and word not in stop_words]
    return tokens

# Function to calculate sentiment and readability metrics
def analyze_text(text):
    tokens = clean_and_tokenize(text)
    sentences = sent_tokenize(text)  # Split text into sentences

    positive_score = sum(1 for token in tokens if token in positive_words)
    negative_score = sum(1 for token in tokens if token in negative_words)
    total_words = len(tokens)
    total_sentences = len(sentences)

    # Derived Variables
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (total_words + 0.000001)

    # Readability Metrics
    avg_sentence_length = total_words / (total_sentences + 0.000001)
    complex_words = sum(1 for word in tokens if is_complex_word(word))
    percent_complex_words = complex_words / (total_words + 0.000001)
    fog_index = 0.4 * (avg_sentence_length + percent_complex_words)
    avg_no_of_words_per_sentence = total_words / (total_sentences + 0.000001)
    avg_word_length = sum(len(word) for word in tokens) / (total_words + 0.000001)
    syllables_per_word = sum(count_syllables(word) for word in tokens) / (total_words + 0.000001)
    personal_pronouns = count_personal_pronouns(text)

    return {
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': round(polarity_score, 6),
        'SUBJECTIVITY SCORE': round(subjectivity_score, 6),
        'AVG SENTENCE LENGTH': round(avg_sentence_length, 6),
        'PERCENTAGE OF COMPLEX WORDS': round(percent_complex_words, 6),
        'FOG INDEX': round(fog_index, 6),
        'AVG NUMBER OF WORDS PER SENTENCE': round(avg_no_of_words_per_sentence, 6),
        'COMPLEX WORD COUNT': complex_words,
        'WORD COUNT': total_words,
        'SYLLABLE PER WORD': round(syllables_per_word, 6),
        'PERSONAL PRONOUNS': personal_pronouns,
        'AVG WORD LENGTH': round(avg_word_length, 6),
    }

# Assuming input_df is already defined and contains the 'URL_ID' column
# Create an empty DataFrame to store the results
output_df = pd.DataFrame()

# Process each extracted article:
for url_id in input_df['URL_ID']:
    file_path = f"data/extracted_articles/{url_id}.txt"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()  # Read the content of the extracted article
            analysis_result = analyze_text(text)  # Analyze the extracted article
            analysis_result['URL_ID'] = url_id  # Add the URL_ID to the result
            temp_df = pd.DataFrame([analysis_result])  # Create a temporary DataFrame for the current article
            output_df = pd.concat([output_df, temp_df], ignore_index=True)  # Append the results to the main DataFrame
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# Merge the input_df and output_df on 'URL_ID'
merged_data = pd.merge(input_df, output_df, on='URL_ID', how='left')

# Save the final merged data to an Excel file
merged_data.to_excel('Output Data Structure.xlsx', index=False)
print(f"Final output saved to 'Output Data Structure.xlsx'")

