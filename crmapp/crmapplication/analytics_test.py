import os
import django
import io
import sys
import random
import string
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
from datetime import datetime, timedelta
from lifetimes.utils import summary_data_from_transaction_data
from lifetimes import BetaGeoFitter
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from lifetimes.plotting import plot_period_transactions
    
# Adjust the path to include the directory containing your project
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crmapp.settings')
django.setup()

    
from crmapplication.models import Customer,Invoice  # Now you can import the model
def showrecord(df, name):
    print("Data frame name -------", name)
    print("Data inside : ")
    print(df)
    print("Data describe: ")
    print(df.describe())
    print("Data types")
    print(df.dtypes)

# Retrieve data from Customer model
customers_data = Customer.objects.all().values()
customer_df = pd.DataFrame(customers_data)
customers_data = None
#showrecord(customer_df, "Customers data")

# Retrieve data from Invoice model
invoices_data = Invoice.objects.all().values()
invoice_df = pd.DataFrame(invoices_data)
invoices_data = None
#showrecord(invoice_df, "Invoice data")
#for keyword in customer_df['progress'].unique():
#    print(keyword)

# Data processing
# Update 'progress' column to 'unattend leads' for empty cells
customer_df['progress'] = customer_df['progress'].fillna('unattend leads')

#print(invoice_df.isnull().sum())

# remove all the negative 
# remove all the negative
# Identify return and discount transactions
return_mask = (invoice_df['amount'] < 0) & (-invoice_df['amount'].isin(invoice_df['amount'].abs()))
discount_mask = (invoice_df['amount'] < 0) & (~return_mask)

# Get customer and date information for return and discount transactions
return_customers_dates = invoice_df.loc[return_mask, ['customer_id', 'invoice_date']]
discount_customers_dates = invoice_df.loc[discount_mask, ['customer_id', 'invoice_date']]


# Remove return transactions
invoice_df = invoice_df[~invoice_df.index.isin(return_customers_dates.index)]

# Remove discount transactions (only negative amounts)
invoice_df = invoice_df[~invoice_df.index.isin(discount_customers_dates.index)]


st.write("Assuming today is 9 Dec 2021 - as the last record up to here")
""" 
Please give me today lead
"""
st.write("Today Lead : ")
# Convert 'invoice_date' column to datetime if it's not already
invoice_df['invoice_date'] = pd.to_datetime(invoice_df['invoice_date'])

# Filter rows where 'invoice_date' is '9 Dec 2021'
filtered_invoices = invoice_df[invoice_df['invoice_date'] == '2021-12-9']

# Count the number of occurrences
count = filtered_invoices.shape[0]
st.write("Count of invoices with invoice_date '9 Dec 2021':", count)


""" 

Please seperate me with unattend leads, on follow up lead, follow up after, close case, give up, 
Assuming customer_df is already defined
Analysis the progress
"""
# Total count of customers
total_count = len(customer_df)

# Define keywords
unattend = 0
followup = 0
after = 0
close_case = 0
give_up = 0

# Count occurrences of keywords
for i in range(total_count):
    progress = customer_df.loc[i, 'progress']  # Get the 'progress' value at index i
    if progress == 'give up' or 'npu' in progress:
        give_up += 1
    elif progress == 'close case':
        close_case += 1
    elif 'after' in progress or progress == 'Follow-up After':
        after += 1
    elif 'follow up' in progress or progress == 'On Follow-up Lead':
        followup += 1
    else:
        unattend += 1

# Create a dictionary with the results
results = {
    'Category': ['unattend', 'follow up', 'after', 'close case', 'give up'],
    'Count': [unattend, followup, after, close_case, give_up]
}

# Convert the results to a Pandas DataFrame
results_df = pd.DataFrame(results)

# Streamlit UI
st.write("Total count of rows in customer_df:", total_count)

# Display the results in a tabular format using Streamlit
st.write("Counts by Category:")
st.dataframe(results_df)


""" 
Monthly sales
"""
end_date = datetime(2021, 12, 9)
start_date = end_date - timedelta(days=30)
filtered_df = invoice_df[(invoice_df['invoice_date'] >= start_date) & (invoice_df['invoice_date'] <= end_date)]
#print (filtered_df)

# Sum the amounts on each date
sales_summary = filtered_df.groupby('invoice_date')['amount'].sum().reset_index()

#print(sales_summary)

st.title("Sales Summary for the Last 30 Days")

fig, ax = plt.subplots()
ax.plot(sales_summary['invoice_date'], sales_summary['amount'], marker='o')

ax.set_xlabel("Date")
ax.set_ylabel("Total Amount")
ax.set_title("Sales Summary")
ax.grid(True)

# Customize x-axis tick labels with actual dates
date_ticks = sales_summary['invoice_date'].dt.strftime('%Y-%m-%d').tolist()
ax.set_xticks(sales_summary['invoice_date'])
ax.set_xticklabels(date_ticks, rotation=45)

st.pyplot(fig)

""" 
Customer lifetime value analysis
"""
invoice_df = invoice_df.astype({'customer_id':'string'})
invoice_for_prediction = invoice_df.groupby(['customer_id', 'invoice_date'])['amount'].sum().reset_index()
#print(invoice_for_prediction)


# Duplicate the result DataFrame for comparisons
result_original = invoice_for_prediction.copy()
result_outlier_removed = invoice_for_prediction.copy()
result_scaled = invoice_for_prediction.copy()
result_outlier_removed_scaled = invoice_for_prediction.copy()


# 1. Remove outlier and apply min-max scaling
# Remove outlier
mean = result_outlier_removed['amount'].mean()
result_outlier_removed['amount'] = result_outlier_removed['amount'].astype(float)
std = result_outlier_removed['amount'].std()
lower_bound = mean - std * 2
upper_bound = mean + std * 2
result_outlier_removed = result_outlier_removed[
    (result_outlier_removed['amount'] >= lower_bound) & (result_outlier_removed['amount'] <= upper_bound)
]
# Apply min-max scaling
scaler = MinMaxScaler()
result_outlier_removed['amount'] = scaler.fit_transform(result_outlier_removed[['amount']])

# 2. No outlier removal, no scaling
# ...

# 3. No outlier removal, apply min-max scaling
# Apply min-max scaling
result_scaled['amount'] = scaler.fit_transform(result_scaled[['amount']])

# 4. Remove outlier, no scaling
# Remove outlier
result_outlier_removed_scaled = result_outlier_removed_scaled[
    (result_outlier_removed_scaled['amount'] >= lower_bound) & (result_outlier_removed_scaled['amount'] <= upper_bound)
]

# Calculate the summary data for each scenario
summary_data_original = summary_data_from_transaction_data(result_original, 'customer_id', 'invoice_date', 'amount')
#summary_data_outlier_removed = summary_data_from_transaction_data(result_outlier_removed, 'customer_id', 'invoice_date', 'amount')
#summary_data_scaled = summary_data_from_transaction_data(result_scaled, 'customer_id', 'invoice_date', 'amount')
#summary_data_outlier_removed_scaled = summary_data_from_transaction_data(result_outlier_removed_scaled, 'customer_id', 'invoice_date', 'amount')


# one time buyer 
one_time_buyer = round(sum(summary_data_original['frequency'] == 0)/float(len(summary_data_original))*100,2)
st.write("The percentage of one time buyer - " , one_time_buyer , "%")

# Initialize the BetaGeoFitter model
bgf = BetaGeoFitter()

# Fit the model for each scenario
bgf.fit(summary_data_original['frequency'], summary_data_original['recency'], summary_data_original['T'])



### the  chart show the predict and actual is close
#buffer = io.BytesIO()

# Plot the period transactions
#ax = plot_period_transactions(bgf)
#ax.get_figure().savefig(buffer, format='png')
#plt.close()

# Display the captured image using st.image()
#st.image(buffer.getvalue())


#print(summary_data_original[['monetary_value','frequency']].corr())
shorlisted_summary_data = summary_data_original[summary_data_original['frequency'] > 0]
shorlisted_summary_data = shorlisted_summary_data[shorlisted_summary_data['monetary_value'] > 0]
#print(shorlisted_summary_data.head().reset_index())

from lifetimes import GammaGammaFitter
ggf = GammaGammaFitter(penalizer_coef = 0)
ggf.fit(shorlisted_summary_data['frequency'],
            shorlisted_summary_data['monetary_value'])

print(ggf)

summary_data_original['pred_txn_value'] = round(ggf.conditional_expected_average_profit(
        shorlisted_summary_data['frequency'],
        shorlisted_summary_data['monetary_value']
    ).head(10))
#print(summary_data_original['pred_txn_value'].reset_index().head())

summary_data_original['CLV'] = round(ggf.customer_lifetime_value(
    bgf, # the model to use to predict the number of future transactions
    summary_data_original['frequency'],
    summary_data_original['recency'],
    summary_data_original['T'],
    summary_data_original['monetary_value'],
    time = 12, #months
    discount_rate = 0.01 #assume month discount rate - 12.7
    
),2)
st.write("The customer life time value data : ")
st.dataframe(summary_data_original.sort_values(by='CLV',ascending = False).reset_index())

#bgf_outlier_removed = BetaGeoFitter()
#bgf_outlier_removed.fit(summary_data_outlier_removed['frequency'], summary_data_outlier_removed['recency'], summary_data_outlier_removed['T'])
#bgf_scaled = BetaGeoFitter()
#bgf_scaled.fit(summary_data_scaled['frequency'], summary_data_scaled['recency'], summary_data_scaled['T'])
#bgf_outlier_removed_scaled = BetaGeoFitter()
#bgf_outlier_removed_scaled.fit(summary_data_outlier_removed_scaled['frequency'], summary_data_outlier_removed_scaled['recency'], summary_data_outlier_removed_scaled['T'])

# Generate predictions for each scenario
summary_data_original['predicted_purchases'] = bgf.predict(1, summary_data_original['frequency'], summary_data_original['recency'], summary_data_original['T'])
#summary_data_outlier_removed['predicted_purchases'] = bgf_outlier_removed.predict(1, summary_data_outlier_removed['frequency'], summary_data_outlier_removed['recency'], summary_data_outlier_removed['T'])
#summary_data_scaled['predicted_purchases'] = bgf_scaled.predict(1, summary_data_scaled['frequency'], summary_data_scaled['recency'], summary_data_scaled['T'])
#summary_data_outlier_removed_scaled['predicted_purchases'] = bgf_outlier_removed_scaled.predict(1, summary_data_outlier_removed_scaled['frequency'], #summary_data_outlier_removed_scaled['recency'], summary_data_outlier_removed_scaled['T'])

# Define a threshold to classify as active or not
threshold = 0.5

# Apply threshold to generate classification labels
summary_data_original['predicted_active'] = (summary_data_original['predicted_purchases'] > threshold).astype(int)
#summary_data_outlier_removed['predicted_active'] = (summary_data_outlier_removed['predicted_purchases'] > threshold).astype(int)
#summary_data_scaled['predicted_active'] = (summary_data_scaled['predicted_purchases'] > threshold).astype(int)
#summary_data_outlier_removed_scaled['predicted_active'] = (summary_data_outlier_removed_scaled['predicted_purchases'] > threshold).astype(int)

# Calculate accuracy for each scenario
accuracy_original = accuracy_score(summary_data_original['predicted_active'], summary_data_original['frequency'])
#accuracy_outlier_removed = accuracy_score(summary_data_outlier_removed['predicted_active'], summary_data_outlier_removed['frequency'])
#accuracy_scaled = accuracy_score(summary_data_scaled['predicted_active'], summary_data_scaled['frequency'])
#accuracy_outlier_removed_scaled = accuracy_score(summary_data_outlier_removed_scaled['predicted_active'], summary_data_outlier_removed_scaled['frequency'])

# Display accuracy results
print("Accuracy without outlier removal and scaling:", accuracy_original)
#print("Accuracy with outlier removal:", accuracy_outlier_removed)
#print("Accuracy with scaling:", accuracy_scaled)
#print("Accuracy with outlier removal and scaling:", accuracy_outlier_removed_scaled)