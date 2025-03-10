# -*- coding: utf-8 -*-
"""Final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13nfUwlG8m_07yTh4by9xpQrh8QGQ_LZa

# import packages
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

"""# Data Exploration & Processing


"""

# Read data
df = pd.read_csv('https://raw.githubusercontent.com/15love39/Book-Recommendation-System-for-MAS651/refs/heads/main/data.csv')

df.info()

df.head()

df.describe()

df.isnull().sum()

# 1. Histogram of average_rating
plt.figure(figsize=(10, 6))
plt.hist(df['average_rating'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribution of Average Ratings', fontsize=14)
plt.xlabel('Average Rating', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

# 2. Scatter plot of average_rating vs. ratings_count
plt.figure(figsize=(10, 6))
plt.scatter(df['ratings_count'], df['average_rating'], color='coral', alpha=0.5)
plt.title('Average Rating vs. Ratings Count', fontsize=14)
plt.xlabel('Ratings Count', fontsize=12)
plt.ylabel('Average Rating', fontsize=12)
plt.xscale('log') # Log scale for ratings_count due to wide range plt.grid(True, linestyle='--', alpha=0.7) # Highlight "The Four Loves" as an example four_loves_idx = df[df['title'] == 'The Four Loves'].index[0] plt.scatter(df['ratings_count'][four_loves_idx], df['average_rating'][four_loves_idx], color='red', s=100, label='The Four Loves (33,684 ratings)') plt.legend()
plt.show()

"""## Collaborative Filtering"""

# Select only rating-related features for collaborative filtering
df['average_rating'] = df['average_rating'].fillna(df['average_rating'].mean())
df['ratings_count'] = df['ratings_count'].fillna(0)

# Normalize rating data (to prevent large value ranges)
df['norm_rating'] = df['average_rating'] / df['average_rating'].max()
df['norm_ratings_count'] = df['ratings_count'] / df['ratings_count'].max()

"""## Content-Based"""

# Select relevant features for content-based recommendation
selected_features = ['title', 'authors', 'categories', 'description']

# Handle missing values
for feature in selected_features:
    df[feature] = df[feature].fillna('')

# Combine features into a single text data column
df['content'] = df['title'] + ' ' + df['authors'] + ' ' + df['categories'] + ' ' + df['description']

"""# Building Recommendation System - Collaborative Filtering"""

# Create rating matrix
ratings_matrix = df[['norm_rating', 'norm_ratings_count']].values  # Convert to numpy array

# Apply SVD with dynamic k
n_rows, n_cols = ratings_matrix.shape
k = min(n_rows - 1, n_cols - 1, 2)  # Ensure k < min(A.shape) and at least 1

U, sigma, Vt = svds(ratings_matrix, k=k)
sigma = np.diag(sigma)
ratings_matrix_svd = np.dot(np.dot(U, sigma), Vt)

# Compute cosine similarity
cosine_similarities1 = cosine_similarity(ratings_matrix_svd)

# Create recommendation results dictionary
results_cf = {}
titles = [t.lower() for t in df['title'].tolist()]

for idx, title in enumerate(df['title'].tolist()):
    similar_indices = cosine_similarities1[idx].argsort()[:-100:-1]
    similar_items = [(cosine_similarities1[idx][i], titles[i]) for i in similar_indices]
    results_cf[title.lower()] = similar_items[1:]  # Exclude itself

print('Collaborative filtering recommendation system based on ratings with SVD has been built!')

# Recommendation function (case-insensitive)
def recommend1(title, num=5):
    title = title.lower()
    print("----------------------------------------------------")
    print(f"Collaborative filtering recommendation based on ratings - Top {num} books similar to \"{title}\":")
    print("----------------------------------------------------")
    recs = results_cf[title][:num]
    i = 1
    for rec in recs:
        print(f"Recommended{i}: {rec[1]}")
        i += 1
        print(' ')

"""# Building Recommendation System - Content-Based"""

# Building Recommendation System - Content-Based
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0.01, stop_words='english')
tfidf_matrix = tf.fit_transform(df['content'])
cosine_similarities2 = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Create recommendation results dictionary
results = {}
for idx, row in df.iterrows():
    similar_indices = cosine_similarities2[idx].argsort()[:-100:-1]
    similar_items = [(cosine_similarities2[idx][i], df['title'][i]) for i in similar_indices]
    results[row['title'].lower()] = similar_items[1:]  # Exclude itself

print('Content-based filtering recommendation system has been built!')

# Content-based recommendation function (case-insensitive)
def recommend2(title, num=5):
    title = title.lower()
    print("----------------------------------------------------")
    print(f"Content-based filtering recommendation - Top {num} books similar to \"{title}\":")
    print("----------------------------------------------------")
    recs = results[title][:num]
    i = 1
    for rec in recs:
        print(f"Recommended{i}: {rec[1]}")
        i += 1
        print(' ')

"""# Testing the Recommendation System"""

# Testing the Recommendation System
while True:
    title = input("Enter book title: ").lower()
    if title in results_cf:
        break
    print("Book not found. Please try again!")
num = int(input("Enter how many recommendations do you want: "))
recommend1(title, num)
recommend2(title, num)
