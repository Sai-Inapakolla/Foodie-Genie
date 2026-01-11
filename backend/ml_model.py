import re
import json
import os

class RecipeRecommender:
    def __init__(self):
        self.recipes_list = []
        self.normalization_map = {}
        # Global Assumptions: "always available" ingredients
        self.COMMON_INGREDIENTS = {"salt", "oil", "water", "onion", "ginger", "garlic", "spices", "basic spices", "chilli", "red chilli", "turmeric"}
        
        # Substitution Map (User Rule 4)
        self.SUBSTITUTION_MAP = {
            "capsicum": ["carrot", "bell pepper"],
            "cream": ["milk", "malai"], # simplified logic for "milk + butter"
            "butter": ["ghee", "oil"],
            "ghee": ["butter", "oil"],
            "sugar": ["jaggery", "honey"],
            "jaggery": ["sugar", "brown sugar"],
            "paneer": ["tofu", "chicken"],
            "chicken": ["paneer", "tofu", "soya chunks"],
            "lemon": ["vinegar", "amchur"],
            "yogurt": ["curd", "buttermilk"],
            "maida": ["wheat flour", "atta"],
            "corn flour": ["rice flour", "arrowroot powder"]
        }
        
        self.weights = {} # For learning from users
        self.weights_file = "model_weights.json"

    def _singularize(self, word):
        """
        Simple heuristic singularization.
        """
        word = word.strip()
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('es') and not word.endswith('oes') and not word.endswith('ses'):
             return word[:-2]
        if word.endswith('oes'):
             return word[:-2]
        if word.endswith('s') and not word.endswith('ss') and not word.endswith('us'):
            return word[:-1]
        return word

    def load_weights(self):
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r') as f:
                    self.weights = json.load(f)
                print(f"Loaded weights for {len(self.weights)} recipes.")
            except:
                print("Error loading weights, starting fresh.")
                self.weights = {}

    def save_weights(self):
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.weights, f)
        except Exception as e:
            print(f"Error saving weights: {e}")

    def update_feedback(self, recipe_id, action):
        """
        Rule 7: Learning From Users
        """
        recipe_id = str(recipe_id)
        current_weight = self.weights.get(recipe_id, 1.0)
        
        if action == 'select':
            self.weights[recipe_id] = current_weight + 0.1
        elif action == 'reject':
            self.weights[recipe_id] = max(0.1, current_weight - 0.1)
            
        self.save_weights()

    def train(self, recipes_data):
        self.recipes_list = recipes_data
        self.normalization_map = {}
        self.load_weights()
        
        # Build normalization map
        for rec in self.recipes_list:
            if 'ingredients' in rec:
                for ing in rec['ingredients']:
                    norm = self._clean_text(ing)
                    if norm:
                        self.normalization_map[norm] = norm
                        singular = self._singularize(norm)
                        if singular != norm:
                             self.normalization_map[singular] = singular
                             self.normalization_map[norm] = singular
                        else:
                             self.normalization_map[norm] = norm
                             
        print(f"Model initialized. {len(self.normalization_map)} normalization terms loaded.")

    def _clean_text(self, text):
        """
        Internal normalization logic using robust regex.
        Rule 2: Normalize ingredients
        """
        if not text:
            return ""
        
        p = text.strip().lower()
        
        # 1. Remove quantities
        p = re.sub(r'\d+/\d+', '', p)
        units = r'(?:g|gm|grams?|kgs?|ml|l|litres?|liters?|cups?|tbsp|tsp|teaspoons?|tablespoons?|oz|ounces?|lbs?|pounds?|pieces?|slices?)'
        p = re.sub(r'\d*\.?\d+\s*' + units + r'\b', '', p)
        p = re.sub(r'\b' + units + r'\b', '', p)
        p = re.sub(r'\b\d+\b', '', p)
        
        # Remove description noise
        noise_words = r'\b(boneless|fresh|chopped|sliced|cooked|raw|boiled|diced|minced|grated|peeled|mashed|crushed|whole|large|medium|small|dried|powder|powdered|paste|seeds|leaves|pods|sticks|bulbs|cloves|stems|roots)\b'
        p = re.sub(noise_words, '', p)
        
        # Remove punctuation
        p = re.sub(r'[^\w\s]', ' ', p)
        
        # Collapse spaces
        p = re.sub(r'\s+', ' ', p).strip()
        
        # Hardcoded synonym fixes (Rule 2)
        synonyms = {
            "brinjal": "eggplant",
            "chilli": "chili",
            "red chili": "chili",
            "chillies": "chili"
        }
        if p in synonyms:
            p = synonyms[p]
            
        return p

    def normalize_input(self, text):
        if not text:
            return []
        if isinstance(text, list):
            parts = text
        else:
            parts = text.split(',')
            
        normalized_result = set()
        for part in parts:
            cleaned = self._clean_text(part)
            if cleaned:
                if cleaned in self.normalization_map:
                    normalized_result.add(self.normalization_map[cleaned])
                else:
                    singular = self._singularize(cleaned)
                    if singular in self.normalization_map:
                        normalized_result.add(self.normalization_map[singular])
                    else:
                        normalized_result.add(singular)
        return list(normalized_result)

    def identify_main_ingredients(self, normalized_ingredients):
        """
        Rule 1: Main Ingredient Rule.
        Main ingredients are those NOT in COMMON_INGREDIENTS.
        """
        return [i for i in normalized_ingredients if i not in self.COMMON_INGREDIENTS]

    def check_substitutions(self, missing_ingredient, user_ingredients):
        """
        Rule 4: Substitution Intelligence
        Returns (substituted_by, penalty_score) or (None, 0)
        """
        # Check direct map
        possible_subs = self.SUBSTITUTION_MAP.get(missing_ingredient, [])
        for sub in possible_subs:
            # Check if user has 'sub' (User Input -> Clean -> Check)
            # But user_ingredients passed here is already a set of normalized strings
            if sub in user_ingredients:
                return sub, 15 # 15 point penalty for using substitution
        
        return None, 0

    def recommend(self, user_input_raw, top_n=50):
        if not self.recipes_list:
            return []
            
        # 1. Normalize User Input
        user_norm_list = self.normalize_input(user_input_raw)
        user_norm_set = set(user_norm_list)
        
        # 2. Normalize Common Ingredients to match recipe/user normalization
        # We process common ingredients through the same pipeline to ensure matching keys (e.g. "spices" -> "spic")
        common_norm_list = self.normalize_input(list(self.COMMON_INGREDIENTS))
        common_norm_set = set(common_norm_list)
        
        # Available = User + Common
        available_set = user_norm_set.union(common_norm_set)
        
        valid_recipes = [] # Confidence > 0
        closest_recipes = [] # Missing main ingredients
        
        for rec in self.recipes_list:
            rec_id = str(rec.get('id'))
            rec_name = rec.get('name')
            raw_ingredients = rec.get('ingredients', [])
            instructions = rec.get('steps', ["Cook until done."])[0] # Assuming list of 1 string
            
            # Normalize Recipe Ingredients
            rec_norm_list = []
            for ing in raw_ingredients:
                n = self._clean_text(ing)
                # Map to canonical if possible
                if n in self.normalization_map:
                    n = self.normalization_map[n]
                else:
                    n = self._singularize(n)
                rec_norm_list.append(n)
            
            rec_norm_set = set(rec_norm_list)
            
            # Identify Main Ingredients
            # Main ingredients are those NOT in Common (Normalized)
            main_ingredients = [i for i in rec_norm_list if i not in common_norm_set]
            
            # --- Check Rule 1: Missing Main Ingredients ---
            missing_main = []
            matched_main_count = 0
            
            matched_ingredients = []
            missing_ingredients = []
            substitutions = {}
            total_substitution_penalty = 0
            
            for ing in rec_norm_set:
                if ing in available_set:
                    matched_ingredients.append(ing)
                    if ing in main_ingredients:
                        matched_main_count += 1
                else:
                    # Check Substitutions (Rule 3 & 4)
                    sub, penalty = self.check_substitutions(ing, user_norm_set)
                    if sub:
                        substitutions[ing] = sub
                        matched_ingredients.append(f"{ing} (sub: {sub})")
                        total_substitution_penalty += penalty
                        # Count as matched main if it was a main ingredient
                        if ing in main_ingredients:
                            matched_main_count += 1
                    else:
                        missing_ingredients.append(ing)
                        if ing in main_ingredients:
                            missing_main.append(ing)

            # Rule 1: If ANY main ingredient is missing -> Closest
            can_cook = len(missing_main) == 0
            
            # --- Rule 5: Calculate Confidence Score ---
            # Weights
            # Revised Scoring: Prioritize matching USER provided ingredients
            
            matched_user_provided = [ing for ing in matched_ingredients if ing in user_norm_set and ing not in common_norm_set]
            user_input_match_count = len(matched_user_provided)
            
            # Check if we have ANY user specific match
            # If user_norm_set is empty, then any match is fine (e.g. user just hit search?)
            # But normally user provides input.
            has_user_match = user_input_match_count > 0 or len(user_norm_set) == 0
            
            W_MAIN = 0.5
            W_PCT = 0.3
            
            total_ingredients = len(rec_norm_set) if len(rec_norm_set) > 0 else 1
            total_main = len(main_ingredients) if len(main_ingredients) > 0 else 1
            
            main_match_ratio = matched_main_count / total_main
            overall_match_ratio = len(matched_ingredients) / total_ingredients
            
            base_score = (main_match_ratio * W_MAIN * 100) + (overall_match_ratio * W_PCT * 100)
            
            # Boost logic
            if has_user_match:
                base_score += 20 # Bonus for relevance
            else:
                base_score *= 0.1 # Penalty for irrelevance (only matching common)
            
            # Apply penalties
            final_score = base_score - total_substitution_penalty
            
            # Apply User Learning Weight
            user_weight = self.weights.get(rec_id, 1.0)
            final_score *= user_weight
            
            # Cap at 100
            final_score = min(100, max(0, int(final_score)))
            
            mapped_result = {
                "id": rec_id,
                "recipe_name": rec_name,
                "confidence_score": final_score,
                "can_cook": can_cook,
                "matched_ingredients": matched_ingredients,
                "missing_ingredients": missing_ingredients,
                "substitutions": substitutions,
                "instructions": instructions,
                "missing_main_warning": (f"Missing main ingredient(s): {', '.join(missing_main)}. Suggested if you plan to buy it" if not can_cook else "")
            }
            
            if can_cook:
                valid_recipes.append(mapped_result)
            else:
                # Only add to closest if it has SOME relevance or good match
                if has_user_match or overall_match_ratio > 0.4: 
                    closest_recipes.append(mapped_result)

        # Rule 6: Ranking
        # 1. Valid recipes first
        # 2. Sort by confidence desc
        valid_recipes.sort(key=lambda x: x['confidence_score'], reverse=True)
        closest_recipes.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return valid_recipes + closest_recipes[:top_n]
