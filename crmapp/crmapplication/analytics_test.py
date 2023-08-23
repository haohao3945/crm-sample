import os
import django
import io
import sys
import random
import string
import pandas as pd
from datetime import datetime, timedelta
from lifetimes.utils import summary_data_from_transaction_data
from lifetimes import BetaGeoFitter
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from lifetimes.plotting import plot_period_transactions
from openpyxl import Workbook

def change_column_names(df, column_name_changes):
   return df.rename(columns=column_name_changes)

   
def analyze_data():
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



    invoice_df = invoice_df.astype({'customer_id':'string'})
    invoice_for_prediction = invoice_df.groupby(['customer_id', 'invoice_date'])['amount'].sum().reset_index()
    #print(invoice_for_prediction)


    """
    Code for comparisons purpose
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
    """
    
    
    # Calculate the summary data for each scenario
    summary_data_original = summary_data_from_transaction_data(invoice_for_prediction, 'customer_id', 'invoice_date', 'amount')
    #summary_data_outlier_removed = summary_data_from_transaction_data(result_outlier_removed, 'customer_id', 'invoice_date', 'amount')
    #summary_data_scaled = summary_data_from_transaction_data(result_scaled, 'customer_id', 'invoice_date', 'amount')
    #summary_data_outlier_removed_scaled = summary_data_from_transaction_data(result_outlier_removed_scaled, 'customer_id', 'invoice_date', 'amount')


    # one time buyer 
    one_time_buyer = round(sum(summary_data_original['frequency'] == 0)/float(len(summary_data_original))*100,2)

    # Initialize the BetaGeoFitter model
    bgf = BetaGeoFitter()

    # Fit the model for each scenario
    bgf.fit(summary_data_original['frequency'], summary_data_original['recency'], summary_data_original['T'])

    #print(summary_data_original[['monetary_value','frequency']].corr())
    shorlisted_summary_data = summary_data_original[summary_data_original['frequency'] > 0]
    shorlisted_summary_data = shorlisted_summary_data[shorlisted_summary_data['monetary_value'] > 0]
    #print(shorlisted_summary_data.head().reset_index())

    from lifetimes import GammaGammaFitter
    ggf = GammaGammaFitter(penalizer_coef = 0)
    ggf.fit(shorlisted_summary_data['frequency'],
                shorlisted_summary_data['monetary_value'])

    print(ggf)

 
    summary_data_original['CLV'] = round(ggf.customer_lifetime_value(
        bgf, # the model to use to predict the number of future transactions
        summary_data_original['frequency'],
        summary_data_original['recency'],
        summary_data_original['T'],
        summary_data_original['monetary_value'],
        time = 12, #months
        discount_rate = 0.01 #assume month discount rate - 12.7
        
    ),2)
    
    
    """
    Testing for  checking whether mix max scale and outliers affect the prediction results.
    
    """
    #bgf_outlier_removed = BetaGeoFitter()
    #bgf_outlier_removed.fit(summary_data_outlier_removed['frequency'], summary_data_outlier_removed['recency'], summary_data_outlier_removed['T'])
    #bgf_scaled = BetaGeoFitter()
    #bgf_scaled.fit(summary_data_scaled['frequency'], summary_data_scaled['recency'], summary_data_scaled['T'])
    #bgf_outlier_removed_scaled = BetaGeoFitter()
    #bgf_outlier_removed_scaled.fit(summary_data_outlier_removed_scaled['frequency'], summary_data_outlier_removed_scaled['recency'], summary_data_outlier_removed_scaled['T'])




    # Generate predictions for each scenario
    #summary_data_original['predicted_purchases'] = bgf.predict(1, summary_data_original['frequency'], summary_data_original['recency'], #summary_data_original['T'])
    #summary_data_outlier_removed['predicted_purchases'] = bgf_outlier_removed.predict(1, summary_data_outlier_removed['frequency'], summary_data_outlier_removed['recency'], summary_data_outlier_removed['T'])
    #summary_data_scaled['predicted_purchases'] = bgf_scaled.predict(1, summary_data_scaled['frequency'], summary_data_scaled['recency'], summary_data_scaled['T'])
    #summary_data_outlier_removed_scaled['predicted_purchases'] = bgf_outlier_removed_scaled.predict(1, summary_data_outlier_removed_scaled['frequency'], #summary_data_outlier_removed_scaled['recency'], summary_data_outlier_removed_scaled['T'])

    # Define a threshold to classify as active or not
    #threshold = 0.5

    # Apply threshold to generate classification labels
    #summary_data_original['predicted_active'] = (summary_data_original['predicted_purchases'] > threshold).astype(int)
    #summary_data_outlier_removed['predicted_active'] = (summary_data_outlier_removed['predicted_purchases'] > threshold).astype(int)
    #summary_data_scaled['predicted_active'] = (summary_data_scaled['predicted_purchases'] > threshold).astype(int)
    #summary_data_outlier_removed_scaled['predicted_active'] = (summary_data_outlier_removed_scaled['predicted_purchases'] > threshold).astype(int)

    # Calculate accuracy for each scenario
    #accuracy_original = accuracy_score(summary_data_original['predicted_active'], summary_data_original['frequency'])
    #accuracy_outlier_removed = accuracy_score(summary_data_outlier_removed['predicted_active'], summary_data_outlier_removed['frequency'])
    #accuracy_scaled = accuracy_score(summary_data_scaled['predicted_active'], summary_data_scaled['frequency'])
    #accuracy_outlier_removed_scaled = accuracy_score(summary_data_outlier_removed_scaled['predicted_active'], summary_data_outlier_removed_scaled['frequency'])

    # Display accuracy results
    #print("Accuracy without outlier removal and scaling:", accuracy_original)
    #print("Accuracy with outlier removal:", accuracy_outlier_removed)
    #print("Accuracy with scaling:", accuracy_scaled)
    #print("Accuracy with outlier removal and scaling:", accuracy_outlier_removed_scaled)


    # data cleaning for life time value
    clv_data = summary_data_original.sort_values(by='CLV',ascending = False).reset_index()
    
    clv_data['Last_Buying'] = clv_data['T'] - clv_data['recency']
    
    column_name_changes = {'frequency': 'Repeat_Sales_Time', 'recency': 'Active_Period','monetary_value':'Average_Repeat_Sales_Value'}
    
    
    clv_data = change_column_names(clv_data,column_name_changes)
    clv_data = clv_data.drop(columns=['T'])

    #print(clv_data)
    column_name = clv_data.columns
    
    #print(column_name)
    clv_data.to_excel('summary_data_original.xlsx', index=False)
    
    """
    The data is split based on the follow up progress and let users know what to did for each stage easily without need to list the lead one by one
    """
    # Split the data based on the condition
    high_ticket = clv_data[clv_data['Average_Repeat_Sales_Value'] > 1000]
    one_buyer = clv_data[clv_data['Active_Period'] < 1]
    clv_data = clv_data[clv_data['Active_Period'] >= 1]
    hot_clv = clv_data[clv_data['Last_Buying'] < 74]
    cold_clv = clv_data[clv_data['Last_Buying'] >= 74]

    return {
        'customer_life_time_value' : clv_data,
        'one_time_buyer': one_time_buyer,
        'high_ticket':high_ticket,
        'one_buyer':one_buyer,
        'hot_clv':hot_clv,
        'cold_clv':cold_clv,

    }