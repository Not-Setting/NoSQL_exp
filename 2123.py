# Re-importing required libraries and reloading data after the environment reset
import pandas as pd

# File path for the uploaded data
file_path = './data/csv/cleaned_hotels.csv'

# Read the CSV file
hotel_data = pd.read_csv(file_path)

# Perform analysis: count by 'hotel_grade_text' and 'hotel_city_name'
grade_count = hotel_data['hotel_grade_text'].value_counts().reset_index()
grade_count.columns = ['hotel_grade_text', 'count']

city_count = hotel_data['hotel_city_name'].value_counts().reset_index()
city_count.columns = ['hotel_city_name', 'count']

city_count = hotel_data['hotel_city_name'].value_counts().reset_index()
city_count.columns = ['hotel_city_name', 'count']
# Display the results

print(grade_count)
print(city_count)