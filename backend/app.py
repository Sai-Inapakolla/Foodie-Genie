from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from ml_model import RecipeRecommender

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this_prod'  # Required for session

# Global Recommender Instance
recommender = RecipeRecommender()
unique_ingredients = set()

def load_data_and_train():
    global unique_ingredients
    try:
        with open("recipes.json", "r") as f:
            recipes = json.load(f)
        recommender.train(recipes)
        
        # Build unique ingredients set
        print("Building unique ingredients list...")
        # Add normalization rules
        unique_ingredients = set(recommender.normalization_map.keys())
        
        print(f"Data loaded, model trained. {len(unique_ingredients)} unique ingredient terms.")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        # Initialize with empty if fail, to prevent crash
        recommender.train([])

# Train on startup
load_data_and_train()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/api/suggestions')
def suggestions():
    query = request.args.get('q', '').lower().strip()
    if not query:
        return json.dumps([])
    
    # Simple prefix match (or 'contains')
    # Limit to 10 results
    matches = []
    count = 0
    for i in unique_ingredients:
        if query in i:
            matches.append(i)
            count += 1
            if count >= 10:
                break
                
    # Sort nicely (shortest first is usually good)
    matches.sort(key=len)
    return json.dumps(matches)


@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        raw = request.form.get("ingredients", "")
        # Store in session
        # We store the raw string list or split it
        # The new recommender handles comma-separated string well.
        parts = [i.strip() for i in raw.split(",") if i.strip()]
        session['user_ingredients'] = parts
        return redirect(url_for('recipes'))
    
    return render_template("ingredients.html")


@app.route('/recipes')
def recipes():
    user_ingredients = session.get('user_ingredients', [])
    
    if not user_ingredients:
        return redirect(url_for('ingredients'))

    # Get recommendations from ML model
    # Pass list directly (new recommender handles list or string)
    recommendations = recommender.recommend(user_ingredients, top_n=50)
    
    processed_recs = []
    
    for rec in recommendations:
        if rec['confidence_score'] < 10:
            continue
            
        # Adaptation for template to avoid breaking it completely while supporting new features
        # New keys: recipe_name, confidence_score, matched_ingredients, missing_ingredients, substitutions, instructions, missing_main_warning
        
        # Map to old keys expected by template for backward compat + new keys
        mapped = rec.copy()
        
        mapped['name'] = rec['recipe_name']
        mapped['score'] = rec['confidence_score'] / 100.0 # Template expects 0-1 float to multiply by 100
        mapped['available'] = rec['matched_ingredients']
        mapped['missing'] = rec['missing_ingredients']
        
        # Determine strict "missing" list for badges
        # If missing_main_warning is present, we might want to highlight those specifics
        # but the badges logic is fine.
        
        # steps expects a list
        if isinstance(rec['instructions'], str):
            mapped['steps'] = [rec['instructions']]
        else:
             mapped['steps'] = rec['instructions']
             
        processed_recs.append(mapped)

    return render_template("recipes.html",
                           recipes=processed_recs,
                           ingredients=user_ingredients)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """
    Endpoint for Learning From Users (Rule 7)
    Expects JSON: { "recipe_id": 123, "action": "select" | "reject" }
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400
        
    recipe_id = data.get('recipe_id')
    action = data.get('action')
    
    if recipe_id and action in ['select', 'reject']:
        recommender.update_feedback(recipe_id, action)
        return jsonify({"status": "success", "message": "Feedback recorded"}), 200
        
    return jsonify({"status": "error", "message": "Invalid input"}), 400

if __name__ == "__main__":
    app.run(debug=True)
