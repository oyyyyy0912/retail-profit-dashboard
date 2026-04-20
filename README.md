[README.md](https://github.com/user-attachments/files/26906869/README.md)
# 📊 Retail Profit Intelligence Dashboard

## 1. Project Overview

This project develops an interactive data analysis tool using Python and Streamlit to explore retail sales performance and profitability.

The dashboard allows users to analyse how different factors such as region, category, and discount levels affect business outcomes.

---

## 2. Objective

The main objective of this project is to answer the following business question:

**How can discount strategies be managed to improve sales performance without reducing profitability?**

---

## 3. Target Users

This dashboard is designed for:

- Retail managers  
- Business analysts  
- Decision-makers interested in pricing and promotion strategies  

---

## 4. Dataset

- Dataset: Sample Superstore dataset (Kaggle)  
- Date accessed: April 2026  
- Type: Retail transaction data  

---

## 5. Key Features

The dashboard includes the following functionalities:

- Interactive filtering by:
  - Region
  - Category
  - Segment
  - Sub-Category
  - Date range
  - Discount level  

- Key performance indicators (KPIs):
  - Total Sales
  - Total Profit
  - Average Discount
  - Profit Margin  

- Visualisations:
  - Sales by Category
  - Sales by Region
  - Monthly Sales Trend
  - Discount vs Profit analysis (3 charts)
  - Top N Products  

- Dynamic insights that update based on user selections  

---

## 6. How to Run the Project

Step 1: Open terminal (Command Prompt)

Step 2: Navigate to the project folder:
cd Desktop\Interactive_Retail_Profit_Analysis


Step 3: Run the Streamlit application:
streamlit run app.py


Step 4: Open the browser link (usually http://localhost:8501)

---

## 7. File Structure
Interactive_Retail_Profit_Analysis/
│
├── app.py # Streamlit dashboard
├── samplesuperstore.csv # Dataset
├── notebook.ipynb # Data analysis notebook
└── README.md # Project documentation


---

## 8. Limitations

- The dataset is a sample dataset and may not fully represent real-world business complexity  
- The analysis is descriptive and does not include predictive modelling  
- Results may vary depending on selected filters  

---

## 9. Notes

This project demonstrates how Python can be used to transform raw data into an interactive decision-support tool.
