from flask import Flask, render_template, request, redirect, url_for, session
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
        for r in recipes:
            for i in r['ingredients']:
                unique_ingredients.add(i.lower().strip())
        print(f"Data loaded, model trained. {len(unique_ingredients)} unique ingredients.")
        
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
    matches = [i for i in unique_ingredients if query in i][:10]
    # Sort nicely (shortest first is usually good)
    matches.sort(key=len)
    return json.dumps(matches)


@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        raw = request.form.get("ingredients", "")
        # Store in session instead of global
        session['user_ingredients'] = [i.strip().lower() for i in raw.split(",") if i.strip()]
        return redirect(url_for('recipes'))
    
    return render_template("ingredients.html")


@app.route('/recipes')
def recipes():
    user_ingredients = session.get('user_ingredients', [])
    
    if not user_ingredients:
        return redirect(url_for('ingredients'))

    # Get recommendations from ML model
    recommendations = recommender.recommend(user_ingredients, top_n=20)
    
    # Split into 'possible' (high match/low missing) for this simplistic UI logic,
    # or just pass all recommendations.
    # For now, let's keep the UI logic similar: 
    # 'possible' = 0 missing ingredients (or very high score?)
    # 'missing' = some missing ingredients
    
    processed_recs = []
    
    for rec in recommendations:
        # Calculate available ingredients for display
        # We need to preserve the original casing from the recipe ingredients list if possible, 
        # but for simplicity we rely on what's in 'ingredients' list of the recipe.
        
        # normalized comparison
        missing_set = set([m.lower().strip() for m in rec['missing']])
        all_ing = rec['ingredients']
        
        available = [ing for ing in all_ing if ing.lower().strip() not in missing_set]
        
        rec['available'] = available
        processed_recs.append(rec)

    # For the template, we just pass the processed list. 
    # We can remove the 'possible'/'missing' split if we want a unified list sorted by score,
    # or keep it. The user asked to "show available ingredients as main ingredients".
    # Let's pass the single sorted list to simplify the template logic and show interactions.
    
    return render_template("recipes.html",
                           recipes=processed_recs,
                           ingredients=user_ingredients)


if __name__ == "__main__":
    app.run(debug=True)
