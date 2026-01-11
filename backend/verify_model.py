from ml_model import RecipeRecommender
import json

def test_model():
    print("Loading data...")
    try:
        with open("recipes.json", "r") as f:
            recipes = json.load(f)
        print(f"Loaded {len(recipes)} recipes.")
    except Exception as e:
        print(f"FAILED to load recipes: {e}")
        return

    print("Initializing Recommender...")
    rec = RecipeRecommender()
    
    print("Training Model...")
    rec.train(recipes)
    
    test_ingredients = ["chicken", "rice", "salt"]
    print(f"Testing recommendation for: {test_ingredients}")
    
    results = rec.recommend(test_ingredients, top_n=5)
    
    if results:
        print("SUCCESS: Recommendations generated:")
        for r in results:
            print(f"- {r['name']} (Score: {r['score']:.2f})")
    else:
        print("WARNING: No recommendations found (this might be normal if randomness was unlucky, but unlikely with 1000+ recipes).")

if __name__ == "__main__":
    test_model()
