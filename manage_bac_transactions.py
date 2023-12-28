import pandas as pd

import pandas as pd

def read_csv(data_path: str, encoding: str = "utf-8"):
    df = pd.read_csv(data_path, encoding=encoding)
    return df

df = read_csv("Monthly transactions.csv" ,encoding="latin-1")

df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(' ', '_')

# Specify the column you want to check for date values
column_to_check = 'Transaction_date'
# Try to convert the values to datetime format with the correct format string
try:
    df[column_to_check] = pd.to_datetime(df[column_to_check], format="%d/%m/%Y")
    print(f"The '{column_to_check}' column contains date values.")
except pd.errors.OutOfBoundsDatetime:
    print(f"The '{column_to_check}' column does not contain valid date values.")
except Exception as e:
    print(f"An error occurred: {e}")


# create a new column for the month, week and year
df['Month'] = df['Transaction_date'].dt.month.astype(str)
df['Week'] = df['Transaction_date'].dt.isocalendar().week.astype(str)
df['Year'] = df['Transaction_date'].dt.year.astype(str)

print(df.info())