#Packages
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
from scipy import stats

@st.cache_data  # Cache the function to enhance performance
def load_data():
    # Define the file path
    file_path = 'https://github.com/Cheide20/assignments/raw/main/DatabankWide.xlsx'
    df = pd.read_excel(file_path)

    return df
df = load_data()

# Set the app title and sidebar header
st.title("Welcome to our first app, used to run analysis on the data")
st.sidebar.header("Filters 📊")

# Introduction
st.markdown("""
Welcome, the following app will help you run an analysis on the data based on your specified guidelines.
""")


with st.expander("📊 **Objective**"):
    st.markdown("""
This dashboard shows the filtered data.
""")

#The following is a subset that limits the dataset. Is extended a little bit from our initial "opgave kan ikke lige huske oversættelsen"
columns_to_include = [
    "Country name", "Country code", "Year", "Adult populaiton", "Region", "Income group",
    "Account (% age 15+)", "Financial institution account (% age 15+)",
    "First financial institution account ever was opened to receive a wage payment or money from the government (% age 15+)",
    "First financial institution account ever was opened to receive a wage payment (% age 15+)",
    "First financial institution ever account was opened to receive money from the government (% age 15+)",
    "Owns a credit card (% age 15+)", "Used a credit card (% age 15+)", 
    "Used a credit card: in-store (% age 15+)", "Used a credit card: in-store (% who used a credit card, age 15+)",
    "Paid off all credit card balances in full by their due date (% age 15+)", 
    "Paid off all credit card balances in full by their due date (% who used a credit card, age 15+)", 
    "Owns a debit card (% age 15+)", "Used a debit card (% age 15+)", 
    "Used a debit card in-store (% age 15+)", "Used a debit card: in-store (% who used a debit card, age 15+)", 
    "Owns a debit or credit card (% age 15+)", "Used a debit or credit card (% age 15+)", 
    "Uses a debit or credit card: in-store (% age 15+)", 
    "Used a debit or credit card: in-store (% who use a credit or debit card, age 15+)"
]

#Det subsettede data
df_subset = df[columns_to_include]

#Kode til valg af kolonner
selected_columns = st.sidebar.multiselect("Select Columns to Display", columns_to_include, default=columns_to_include)

if selected_columns:
    filtered_df = df_subset[selected_columns]
    cleaned_data = filtered_df.dropna(subset=['Region', 'Income group', 'Adult populaiton'])
    data_na = cleaned_data.fillna({
    'First financial institution account ever was opened to receive a wage payment or money from the government (% age 15+)': cleaned_data['First financial institution account ever was opened to receive a wage payment or money from the government (% age 15+)'].mean(),
    'Used a credit card: in-store (% age 15+)': cleaned_data['Used a credit card: in-store (% age 15+)'].median(),
    'Paid off all credit card balances in full by their due date (% age 15+)': cleaned_data['Paid off all credit card balances in full by their due date (% age 15+)'].mean(),
    'Owns a credit card (% age 15+)': cleaned_data['Owns a credit card (% age 15+)'].fillna(0),
    'Adult populaiton': cleaned_data['Adult populaiton'].mean(),  # Assuming you want to fill the mean for population
    'Income group': cleaned_data['Income group'].ffill(),  # Using forward fill for categorical data like income group
    'Financial institution account (% age 15+)': cleaned_data['Financial institution account (% age 15+)'].median(),
    'Used a debit card in-store (% age 15+)': cleaned_data['Used a debit card in-store (% age 15+)'].median(),
    'Owns a debit card (% age 15+)': cleaned_data['Owns a debit card (% age 15+)'].fillna(0),
    'Used a debit card (% age 15+)': cleaned_data['Used a debit card (% age 15+)'].median(),
    'Uses a debit or credit card: in-store (% age 15+)': cleaned_data['Uses a debit or credit card: in-store (% age 15+)'].median()})
    st.dataframe(data_na)


#Kode til at identificere hvilken form for statistisk information man vil have printet
st.title("Dataset Summary")
st.write("### Full Dataset Summary")
st.write(data_na.describe())  # Static summary statistics

#Bruges til at vise hvilke kolonner der skal fremvises
st.write("### Choose Columns and Statistics to Display")

stat_options = st.multiselect(
    "Select Statistics to Display", 
    ["Mean", "Median", "Standard Deviation (std)", "Minimum (min)", "Maximum (max)", "Quartiles"]
)

selected_columns = st.multiselect("Select Columns", cleaned_data.columns.tolist())

def display_column_statistics(data_na, selected_columns, stat_options):
    if not selected_columns:
        st.warning("Please select at least one column.")
        return
    
for col in selected_columns:
        st.subheader(f"Statistics for {col}")
        for stat in stat_options:
            if stat == "Mean":
                st.write(f"**Mean**: {data_na[col].mean()}")
            elif stat == "Median":
                st.write(f"**Median**: {data_na[col].median()}")
            elif stat == "Standard Deviation (std)":
                st.write(f"**Standard Deviation**: {data_na[col].std()}")
            elif stat == "Minimum (min)":
                st.write(f"**Minimum**: {data_na[col].min()}")
            elif stat == "Maximum (max)":
                st.write(f"**Maximum**: {data_na[col].max()}")
            elif stat == "Quartiles":
                st.write(f"**Quartiles**: {data_na[col].quantile([0.25, 0.5, 0.75])}")
        st.markdown("---")


# Kalder på funktionen for hvad der skal fremvises
if selected_columns and stat_options:
    display_column_statistics(cleaned_data, selected_columns, stat_options)


#Laver et flexibelt boxplot
st.title("Flexible Boxplot")

def create_boxplot(data, x_col, y_col):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, x=x_col, y=y_col)
    plt.title(f'Box Plot of {y_col} by {x_col}')
    st.pyplot(plt)

x_axis = st.selectbox("Select X-axis (Categorical)", data_na.columns.tolist(), index=0)
y_axis = st.selectbox("Select Y-axis (Numerical)", data_na.columns.tolist(), index=1)

if x_axis and y_axis:
    create_boxplot(data_na, x_axis, y_axis)


# App title and introduction
st.title("Outlier Detection and Quartile Analysis")

# Dropdown for variable selection
selected_variable = st.selectbox("Select a variable for outlier detection and quartile analysis:", columns_to_include[3:])

# Dynamic calculation of Z-scores, IQR, and outliers for the selected variable (hidden in the app)
if selected_variable:
    # Remove NaN values for the selected variable
    data_na = df_subset.dropna(subset=[selected_variable])

    # Calculate Z-scores (not displayed)
    data_na['Z_score'] = stats.zscore(data_na[selected_variable].dropna())

    # Calculate Quartiles and IQR
    Q1 = data_na[selected_variable].quantile(0.25)
    Q3 = data_na[selected_variable].quantile(0.75)
    IQR = Q3 - Q1

    # Calculate lower and upper bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Flag outliers (not displayed)
    data_na['Outlier'] = (data_na[selected_variable] < lower_bound) | (data_na[selected_variable] > upper_bound)

    # Plot the distribution (optional, you can keep this for other variables)
    st.write(f"**Distribution of {selected_variable}**")
    plt.figure(figsize=(10, 6))
    sns.histplot(data_na[selected_variable], kde=True, color='blue')
    plt.title(f'Distribution of {selected_variable}')
    st.pyplot(plt)

    # Display the quartiles and IQR
    st.write(f"**Quartile Analysis for {selected_variable}**")
    st.write(f"Q1 (25th percentile): {Q1}")
    st.write(f"Q3 (75th percentile): {Q3}")
    st.write(f"IQR (Interquartile Range): {IQR}")
    st.write(f"Lower Bound for Outliers: {lower_bound}")
    st.write(f"Upper Bound for Outliers: {upper_bound}")

 # Plot the distribution of the selected variable with and without outliers
    st.write(f"**Distribution of {selected_variable} with and without outliers**")
    plt.figure(figsize=(10, 6))
    sns.histplot(data_na[selected_variable], kde=True, color='blue', label='All data')
    sns.histplot(data_na.loc[~data_na['Outlier'], selected_variable], kde=True, color='green', label='Without Outliers')
    plt.title(f'Distribution of {selected_variable} with and without outliers')
    plt.legend()
    st.pyplot(plt)

# App title and introduction
st.title("Statistics Calculation for Selected Variables")

# Multiselect for variable selection
selected_variables = st.multiselect(
    "Select one or more variables for statistics calculation:", 
    ["Owns a credit card (% age 15+)", "Used a credit card (% age 15+)", 
     "Owns a debit card (% age 15+)", "Used a debit card (% age 15+)"]
)

# Button to calculate statistics for the selected variables
if st.button("Calculate Statistics"):
    if not selected_variables:
        st.warning("Please select at least one variable.")
    else:
        for variable in selected_variables:
            # Remove NaN values for the selected variable
            data_na = df_subset.dropna(subset=[variable])

            # Calculating the range, standard deviation, and variance
            var_range = data_na[variable].max() - data_na[variable].min()
            std_dev = data_na[variable].std()
            variance = data_na[variable].var()

            # Calculating the kurtosis and skewness
            kurtosis = data_na[variable].kurtosis()
            skewness = data_na[variable].skew()

            # Display the results for each variable
            st.subheader(f"Statistics for {variable}")
            st.write(f"**Range**: {var_range}")
            st.write(f"**Standard Deviation**: {std_dev}")
            st.write(f"**Variance**: {variance}")
            st.write(f"**Kurtosis**: {kurtosis}")
            st.write(f"**Skewness**: {skewness}")
            st.markdown("---")