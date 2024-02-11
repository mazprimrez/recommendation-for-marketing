import streamlit as st
import pandas as pd
import ast
from utils.utils import get_likelihood

st.set_page_config(layout="wide")
product_list = pd.read_csv("dataset/product_list.csv")
customer_recommendation = pd.read_csv("dataset/per_customer.csv")

customer_recommendation['Recommendation'] = customer_recommendation['Recommendation'].apply(ast.literal_eval)
customer_recommendation['StockCodeRecommendation'] = customer_recommendation['Recommendation'].apply(lambda x: list(x.keys()))
customer_recommendation['Likelihood'] = customer_recommendation['Recommendation'].apply(lambda x: list(x.values()))

rfm_users = customer_recommendation.groupby("category")['CustomerID'].nunique()

st.header("Users and Product Targeting for Promotion Dashboard")
st.write("""
This dashboard contains information about product recommendation to a user (Product Recommendation), 
         list of Customer ID (Customer Targeting) to be reached for product promotion,
         and list of product with its sales number (Product and users).
""")

recommendation, customer_targeting, product_and_users  = st.tabs(["Product Recommendation", "Costumer Targeting", "Product and Users"])

with product_and_users:
     col1, col2 = st.columns(2)

     with col1:
          st.header("Product List")

          order, asc, name = st.columns(3)
     
          with order:
               columns = st.multiselect(
               'Order By',
               ['StockCode', 'Description', 'SoldCount'],
               ['SoldCount'])

          with asc:
               options = st.selectbox(
               'How',
               ('Descending', 'Ascending'))

               ascending = True if options=='Ascending' else False
          with name:
               prod_name = st.text_input("Find Products",).upper()
          
          product_list_custom = product_list.copy()

          if prod_name:
               product_list_custom = product_list_custom[product_list_custom['Description'].str.contains(prod_name)]

          if len(columns):
               product_list_custom = product_list_custom.sort_values(columns, ascending=ascending)

          st.table(product_list_custom.head(15))

     with col2:
          st.header("RFM Categories")
          st.table(rfm_users)
          st.write("""
          1. Champion is customers who have visited most recently, visited most frequently and spent the most.
          2. Loyal customer is customers who visited recently visited often and spent a great amount
          3. Promising is average recency, frequency, and monetary scores
          4. Need attention is users who visited recently visited often and spent a great amount
          5. Loose them is lowest recency, frequency, and monetary scores.
          """)

with customer_targeting:
     st.header("Recommend These Users the Product")

     stockcode, rfm_cat, number_users = st.columns(3)

     with stockcode:
          txt = st.text_input("Input Stock Code (use comma for multiplice Stock Code e.g. 1,2,3)", "15039")
     with rfm_cat:
           rfm = st.multiselect(
               'Choose RFM Category',
               ['champion', 'loose them', 'loyal customer','need attention', 'promising'],
               ['need attention'])
     with number_users:
          head = st.number_input("Input customers number you need...", value=20, 
                                 placeholder="Input customers number you need...")

     per_customer_custom = customer_recommendation.copy()
     per_customer_custom.loc[:, 'likelihood (%)'] = 0

     if txt: 
          selected_product = txt.split(",")

          st.write("You want to promote these products")
          st.table(product_list[product_list['StockCode'].isin(selected_product)])

          per_customer_custom = per_customer_custom[per_customer_custom['StockCodeRecommendation'].apply(lambda x: len(set(x).intersection(set(selected_product)))==len(selected_product))]

          per_customer_custom['likelihood (%)'] = per_customer_custom['Recommendation'].apply(lambda x: get_likelihood(x, selected_product))

     if rfm:
          per_customer_custom = per_customer_custom[per_customer_custom['category'].isin(rfm)]
     
     st.header("List of CustomerID to be reached")
     st.write("CustomerID is the ID of each customer, category is RFM categorization, \
              likelihood is the likelihood customers might response to the promotion in descending order (in %)")
     st.table(per_customer_custom[['CustomerID', 'category', 'likelihood (%)']].sort_values('likelihood (%)', ascending=False).head(head))

with recommendation:
     text_type, num_row, button= st.columns(3)
     default_customer=14821

     with button:
          if st.button("Shuffle Customer ID"):
               selected_customer = customer_recommendation.sample(n=1)
               default_customer = int(selected_customer["CustomerID"].values[0])

     with text_type:
          CustomerID = st.number_input("Input CustomerID...", value=default_customer)
          
     with num_row:
               head = st.number_input("Input number of products you need...", value=None, 
                                   placeholder="Maximum 20 rows")
               if head:
                    head = int(head)

     if CustomerID:
          selected_row = customer_recommendation[customer_recommendation['CustomerID']==CustomerID]
          category = selected_row["category"].values[0]
          st.write(f"Product Recommendation for CustomerID {CustomerID} ({category.upper()} - RFM categories)")

          reco = selected_row.explode(["StockCodeRecommendation", "Likelihood"])
          reco = reco.merge(product_list, left_on="StockCodeRecommendation", right_on="StockCode").sort_values("Likelihood", ascending=False)

               
          st.table(reco[["StockCodeRecommendation", "Description", "Likelihood"]].head(head))
