# Foodie Genie 🧞‍♂️🍽️

**Cook Smarter, Not Harder.**

Foodie Genie is an AI-powered kitchen assistant that helps you turn leftover ingredients into 5-star meals. Using a Content-Based Recommendation System (TF-IDF & Cosine Similarity), it suggests the best recipes based on what you currently have in your fridge.

## ✨ Features

- **Smart Ingredient Search**: Add ingredients one by one with auto-suggestions.
- **AI-Powered Recommendations**: Uses Machine Learning to find recipes that match your input.
- **Match Score**: See how well a recipe matches your ingredients (e.g., "95% Match").
- **Missing Ingredients**: Clearly shows what you have vs. what you need to buy.
- **Interactive UI**: Beautiful, dark-themed, responsive design.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Machine Learning**: Scikit-Learn (TfidfVectorizer, Cosine Similarity), Pandas, NumPy
- **Frontend**: HTML5, CSS3 (Custom Design), JavaScript
- **Data**: Kaggle Recipe Datasets (Indian Food & Generic Recipes)

## 📂 Project Structure

```
Foodie Genie/
├── backend/
│   ├── app.py                 # Main Flask Application
│   ├── ml_model.py            # ML Logic (TF-IDF)
│   ├── import_data.py         # Script to import CSVs to JSON
│   ├── templates/             # HTML Templates
│   └── static/                # CSS, Images, JS
├── data/                      # Source CSV Data Files
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/foodie-genie.git
    cd "Foodie Genie"
    ```

2.  **Install Dependencies**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python app.py
    ```

4.  **Open in Browser**
    Visit `http://127.0.0.1:5000` to start cooking!

## 🧠 How It Works

1.  **Data Loading**: On startup, the app loads recipes from `recipes.json` and trains a TF-IDF model on all ingredient lists.
2.  **User Input**: You enter ingredients you have (e.g., "chicken, tomato, onion").
3.  **Vectorization**: Your input is converted into a vector in the same high-dimensional space as the recipes.
4.  **Similarity Search**: We calculate the cosine similarity between your input vector and every recipe vector.
5.  **Ranking**: The top closest matches are returned, sorted by relevance.

---
*Developed for DAA Project.*
