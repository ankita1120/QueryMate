"""
suggestions.py

Generate smart AI questions based on dataset columns.
"""


def generate_questions(df):
    questions = []

    columns = [col.lower().strip() for col in df.columns]

    # -----------------------------
    # Sales / Revenue
    # -----------------------------
    if any(word in columns for word in ["sales", "revenue", "price", "amount"]):
        questions.extend([
            "What is the total revenue?",
            "Show revenue by category.",
            "Which product performs best?",
            "Which product generates the highest revenue?"
        ])

    # -----------------------------
    # Category
    # -----------------------------
    if "category" in columns:
        questions.extend([
            "Which category has the highest value?",
            "Compare all categories."
        ])

    # -----------------------------
    # Product
    # -----------------------------
    if any(word in columns for word in ["product", "item", "product_name"]):
        questions.extend([
            "Which product sells the most?",
            "Top 10 products by sales."
        ])

    # -----------------------------
    # Region / Country / City
    # -----------------------------
    if any(word in columns for word in ["region", "country", "state", "city"]):
        questions.extend([
            "Which region performs best?",
            "Compare sales across regions."
        ])

    # -----------------------------
    # Customer
    # -----------------------------
    if any(word in columns for word in ["customer", "customer_name"]):
        questions.extend([
            "Who are the top customers?",
            "Which customer contributed the most?"
        ])

    # -----------------------------
    # Profit
    # -----------------------------
    if "profit" in columns:
        questions.extend([
            "Which category has the highest profit?",
            "Show profit distribution."
        ])

    # -----------------------------
    # Date
    # -----------------------------
    if any("date" in col for col in columns):
        questions.extend([
            "Show monthly trends.",
            "Show yearly trends.",
            "How has the data changed over time?"
        ])

    # -----------------------------
    # Missing Values
    # -----------------------------
    if df.isnull().sum().sum() > 0:
        questions.append(
            "Which columns contain missing values?"
        )

    # -----------------------------
    # General AI Questions
    # -----------------------------
    questions.extend([
        "Give me a summary of this dataset.",
        "Find important insights.",
        "Detect unusual patterns.",
        "Recommend visualizations.",
        "What business insights can you find?"
    ])

    # Remove duplicates while preserving order
    unique_questions = list(dict.fromkeys(questions))

    return unique_questions[:10]