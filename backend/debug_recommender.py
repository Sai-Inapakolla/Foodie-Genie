import json
import sys
from ml_model import RecipeRecommender

def debug_recommender():
    rec = RecipeRecommender()
    
    print("Loading recipes.json...")
    with open("recipes.json", "r") as f:
        data = json.load(f)
    rec.train(data)
    
    user_input = "1/2 Chicken, tomato, onion, Basmati rice"
    print(f"\nUser Input: {user_input}")
    
    # 1. Trace Normalization
    norm_input = rec.normalize_input(user_input)
    print(f"Normalized Input: {norm_input}")
    
    # 2. Check Available
    available = set(norm_input).union(rec.COMMON_INGREDIENTS)
    print(f"Total Available (User + Common): {available}")
    
    # 3. Trace Matching for a likely candidate
    # Let's look for recipes containing 'chicken' and 'onion'
    print("\n--- Why are recipes failing? ---")
    
    candidates = []
    for r in data:
        # Simple string check to find relevant recipes to debug
        r_ing_str = " ".join(r.get('ingredients', [])).lower()
        if 'chicken' in r_ing_str and 'onion' in r_ing_str:
            candidates.append(r)
            
    # Debug first 5 candidates
    for r in candidates[:5]:
        print(f"\nRecipe: {r['name']} (ID: {r['id']})")
        
        # Rec normalization
        rec_norm = set()
        for ing in r['ingredients']:
            n = rec._clean_text(ing)
            if n in rec.normalization_map:
                rec_norm.add(rec.normalization_map[n])
            else:
                rec_norm.add(rec._singularize(n))
                
        print(f"Recipe Normalized: {rec_norm}")
        
        missing = rec_norm - available
        
        # Trace Composition
        final_missing = set()
        for m in missing:
            parts = m.split()
            if len(parts) > 1:
                is_satisfied = True
                for p in parts:
                    ps = rec._singularize(p)
                    if ps not in available and p not in available:
                        is_satisfied = False
                        break
                if is_satisfied:
                    print(f"  [Composition Match] '{m}' satisfied by parts.")
                    continue
            final_missing.add(m)
            
        print(f"Missing: {final_missing}")

if __name__ == "__main__":
    debug_recommender()
