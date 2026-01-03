from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

class RecipeRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.df = None
        self.recipes = []

    def train(self, recipes_data):
        """
        Trains the TF-IDF model on the recipe ingredients.
        recipes_data: list of dicts with 'id', 'name', 'ingredients', 'steps'
        """
        self.recipes = recipes_data
        self.df = pd.DataFrame(recipes_data)
        
        # Combine ingredients into a single string for each recipe
        # data cleaning: lowercase and strip
        self.df['ingredients_str'] = self.df['ingredients'].apply(
            lambda x: ' '.join([i.lower().strip() for i in x])
        )
        
        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['ingredients_str'])
        print("Model trained successfully.")

    def recommend(self, user_ingredients, top_n=10):
        """
        Recommends recipes based on user ingredients.
        user_ingredients: list of strings
        """
        if self.tfidf_matrix is None:
            return []

        # Preprocess user input
        user_input_str = ' '.join([i.lower().strip() for i in user_ingredients])
        
        # Transform user input to the same TF-IDF space
        user_tfidf = self.vectorizer.transform([user_input_str])
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(user_tfidf, self.tfidf_matrix).flatten()
        
        # Get top N indices
        # We use argsort and take the last top_n (highest similarity)
        top_indices = cosine_sim.argsort()[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            score = cosine_sim[idx]
            if score > 0.1: # Filter out very low relevance results
                rec = self.recipes[idx]
                
                # Calculate missing ingredients strictly for display
                rec_ingredients_set = set([i.lower().strip() for i in rec['ingredients']])
                user_ingredients_set = set([i.lower().strip() for i in user_ingredients])
                
                missing = list(rec_ingredients_set - user_ingredients_set)
                
                recommendations.append({
                    "id": rec['id'],
                    "name": rec['name'],
                    "steps": rec['steps'],
                    "ingredients": rec['ingredients'],
                    "missing": missing,
                    "score": float(score)
                })
        
        return recommendations
