from csv_loader import load_csv
from data_profile import dataset_info
from gemini_analyzer import GeminiAnalyzer
import pandas as pd

# -------------------------------
# Configuration
# -------------------------------

api_key = "AQ.Ab8RN6LEVbTmVyBqcW9ad5G_LIHmgBJXqyJfxX4nd5botL-oXQ"

file = "data/sales.csv"

#-------------------------------
# Load Dataset
# -------------------------------

df = load_csv(file)


# -------------------------------
# Create Revenue Column
# -------------------------------

if "Quantity" in df.columns and "Price" in df.columns:
    df["Revenue"] = df["Quantity"] * df["Price"]

else:
    print("Quantity or Price column missing")
    exit()


# -------------------------------
# Dataset Information
# -------------------------------

print("\nDataset Information")
print("-------------------")
print(dataset_info(df))


# -------------------------------
# Initialize Gemini
# -------------------------------

gemini = GeminiAnalyzer(api_key)


# -------------------------------
# Ask Questions
# -------------------------------

while True:

    q = input("\nAsk a question about your data (type exit to quit): ")

    q = q.lower()


    # Exit
    if q == "exit":
        print("Goodbye!")
        break


    # -------------------------------
    # Category Revenue Analysis
    # -------------------------------

    elif "category" in q:

        if "Category" in df.columns:

            category = df.groupby("Category")["Revenue"].sum()

            print("\nRevenue by Category")
            print("----------------------")
            print(category)

        else:
            print("Category column not found in dataset")

        continue



    # -------------------------------
    # Total Revenue
    # -------------------------------

    elif "total revenue" in q:

        total_revenue = df["Revenue"].sum()

        print("\nTotal Revenue")
        print("----------------")
        print(total_revenue)

        continue



    # -------------------------------
    # Top Products
    # -------------------------------

    elif "top product" in q:

        if "Product" in df.columns:

            top_products = (
                df.groupby("Product")["Revenue"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            print("\nTop Products")
            print("----------------")
            print(top_products)

        else:
            print("Product column not found")

        continue



    # -------------------------------
    # Gemini AI Analysis
    # -------------------------------

    else:

        response = gemini.ask(
            df,
            q
        )

        print("\nGemini Analysis")
        print("----------------")
        print(response)