import json
import random

# Common ingredients to mix and match
ingredients_list = [
    "chicken", "beef", "pork", "fish", "shrimp", "tofu", "egg", "rice", "pasta", "noodles",
    "potato", "onion", "garlic", "ginger", "tomato", "cucumber", "carrot", "broccoli",
    "spinach", "lettuce", "cheese", "milk", "cream", "butter", "oil", "soy sauce",
    "vinegar", "sugar", "salt", "pepper", "chili", "curry powder", "flour", "bread",
    "mushroom", "corn", "peas", "beans", "lentils", "lemon", "lime", "parsley", "basil"
]

adjectives = ["Spicy", "Savory", "Sweet", "Sour", "Creamy", "Crispy", "Grilled", "Fried", "Baked", "Roasted", "Steamed", "Quick", "Slow-Cooked", "Grandma's", "Traditional", "Modern"]
types = ["Stew", "Soup", "Salad", "Stir-fry", "Casserole", "Curry", "Pasta", "Rice Bowl", "Sandwich", "Wrap", "Tacos", "Burger", "Pie", "Roast", "Skillet"]

def generate_recipe(id):
    num_ingredients = random.randint(4, 10)
    recipe_ingredients = random.sample(ingredients_list, num_ingredients)
    
    main_ingredient = recipe_ingredients[0]
    adj = random.choice(adjectives)
    typ = random.choice(types)
    name = f"{adj} {main_ingredient.capitalize()} {typ}"
    
    steps = [
        f"Prepare the {main_ingredient}.",
        f"Chop the {', '.join(recipe_ingredients[1:3])}.",
        "Heat the pan and add oil.",
        f"Cook the {main_ingredient} until done.",
        f"Add {', '.join(recipe_ingredients[3:])} and simmer.",
        "Season with salt and pepper to taste.",
        "Serve hot and enjoy!"
    ]
    
    return {
        "id": id,
        "name": name,
        "ingredients": recipe_ingredients,
        "steps": steps
    }

def main():
    recipes = []
    # Generate 10000 recipes
    for i in range(1, 10001):
        recipes.append(generate_recipe(i))
        
    with open("recipes.json", "w") as f:
        json.dump(recipes, f, indent=2)
    
    print(f"Generated {len(recipes)} recipes in recipes.json")

if __name__ == "__main__":
    main()
