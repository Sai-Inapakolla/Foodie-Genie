import pandas as pd
import json
import os
import ast

def clean_ingredients(ing_str):
    if pd.isna(ing_str):
        return []
    # Try to handle various formats
    try:
        # If it looks like a list string "['a', 'b']"
        if ing_str.strip().startswith('['):
            return ast.literal_eval(ing_str)
        # If it's comma separated
        return [x.strip() for x in ing_str.split(',')]
    except:
        return [x.strip() for x in str(ing_str).split(',')]

def clean_steps(steps_str):
    if pd.isna(steps_str):
        return []
    try:
        if steps_str.strip().startswith('['):
            return ast.literal_eval(steps_str)
        return [x.strip() for x in steps_str.split('. ')]
    except:
        return [str(steps_str)]

def main():
    all_recipes = []
    current_id = 1
    
    # File paths (relative to backend folder)
    files = [
        {"path": "../data/indian_food.csv", "type": "indian"},
        {"path": "../data/recipes.csv", "type": "general"},
        {"path": "../data/ALL-NEW-Recepies.csv", "type": "new"}
    ]
    
    print("Starting import...")
    
    for f in files:
        if not os.path.exists(f["path"]):
            print(f"WARNING: File not found {f['path']}")
            continue
            
        print(f"Reading {f['path']}...")
        try:
            df = pd.read_csv(f['path'])
            
            for _, row in df.iterrows():
                name = ""
                ingredients = []
                steps = []
                
                # normalize columns based on file type or common names
                # strict logic based on typical CSV headers for these datasets
                
                # Indian Food CSV
                if f['type'] == 'indian':
                    name = row.get('name', 'Unknown Indian Dish')
                    ingredients = clean_ingredients(row.get('ingredients', ''))
                    # instructions might not represent steps well in some datasets, check col names
                    # assuming 'instructions' or similar? indian_food.csv usually has 'ingredients', 'diet', 'prep_time', etc.
                    # It might NOT have instructions. Let's provide a generic one if missing.
                    if 'instructions' in row:
                        steps = clean_steps(row['instructions'])
                    else:
                        steps = ["Mix ingredients and cook according to tradition."]
                
                # Generic/New CSVs
                else:
                    # Try to find name col
                    for col in ['recipe_name', 'name', 'title', 'Recipe Name']:
                        if col in df.columns:
                            name = row[col]
                            break
                    
                    # Try to find ingredients col
                    for col in ['ingredients', 'composition', 'Ingredients']:
                        if col in df.columns:
                            ingredients = clean_ingredients(row[col])
                            break
                            
                    # Try to find steps/instructions
                    for col in ['prep', 'instructions', 'steps', 'Directions', 'Instructions']:
                        if col in df.columns:
                            steps = clean_steps(row[col])
                            break
                
                if name and ingredients:
                    all_recipes.append({
                        "id": current_id,
                        "name": str(name).title(),
                        "ingredients": [str(i).lower() for i in ingredients],
                        "steps": steps if steps else ["Cook until done."]
                    })
                    current_id += 1
                    
        except Exception as e:
            print(f"Error reading {f['path']}: {e}")

    print(f"Imported {len(all_recipes)} recipes.")
    
    with open("recipes.json", "w") as f:
        json.dump(all_recipes, f, indent=2)
    
    print("Saved to recipes.json")

if __name__ == "__main__":
    main()
