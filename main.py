import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Function to get dates for the next two weeks
def get_dates():
    today = datetime.today()
    dates = [today + timedelta(days=i) for i in range(14)]
    return [date.strftime("%Y-%m-%d") for date in dates]

# Function to check and create CSV if not exists
def check_and_create_csv(file_name, columns):
    if not os.path.isfile(file_name):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_name, index=False)

# Initialize CSV files for data storage
def init_csv():
    check_and_create_csv('persons.csv', ['person', 'parking_slot'])
    check_and_create_csv('parking.csv', ['parking_slot', 'date', 'person'])

# Function to reset persons table with new names
def reset_persons_table():
    data = [
        ['Khushal', 'Parking 1'], ['Devdutt', 'Parking 1'],
        ['Mohit', 'Parking 2'], ['Bapurao', 'Parking 2'],
        ['Girish', 'Parking 3'], ['Dhiraj', 'Parking 3'],
        ['Sanjay', 'Parking 4'], ['Amol', 'Parking 4'],
        ['Jagdish', 'Parking 5'], ['Vinayak', 'Parking 5']
    ]
    df = pd.DataFrame(data, columns=['person', 'parking_slot'])
    df.to_csv('persons.csv', index=False)

# Function to load parking data from CSV
def load_parking_data():
    return pd.read_csv('parking.csv')

# Function to load persons data from CSV
def load_persons_data():
    return pd.read_csv('persons.csv')

# Function to save parking data to CSV
def save_parking_data(parking_slot, date, person):
    df = load_parking_data()
    new_row = pd.DataFrame([{'parking_slot': parking_slot, 'date': date, 'person': person}])
    mask = (df['parking_slot'] == parking_slot) & (df['date'] == date)
    if mask.any():
        df.loc[mask, 'person'] = person
    else:
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('parking.csv', index=False)

# Main Streamlit app function
def main():
    st.title('Pune Parking Occupancy')

    dates = get_dates()
    parking_slots = [f'Parking {i+1}' for i in range(5)]
    
    # Load persons data
    persons_data = load_persons_data()
    parking_persons = {slot: list(set(group['person'])) for slot, group in persons_data.groupby('parking_slot')}
    persons = persons_data['person'].tolist()

    # Function to render the parking data
    def render_parking_data():
        try:
            parking_data_df = load_parking_data()
            parking_data = pd.DataFrame(index=parking_slots, columns=dates)
            for _, row in parking_data_df.iterrows():
                parking_data.at[row['parking_slot'], row['date']] = row['person']
            st.write("Parking Allotment Table")
            st.dataframe(parking_data.fillna(""))
        except FileNotFoundError:
            st.error("Parking data file not found. Please initialize data.")

    render_parking_data()

    st.write("Update Parking Allotment")
    selected_person = st.selectbox('Select Person', persons)
    selected_parking = st.selectbox('Select Parking Slot', parking_slots, 
                                    format_func=lambda x: f"{x} ({', '.join(parking_persons[x])})")
    selected_dates = st.multiselect('Select Dates', dates)  # Updated to multiselect

    if selected_person in parking_persons[selected_parking]:
        if st.button('Update'):
            for date in selected_dates:
                save_parking_data(selected_parking, date, selected_person)
            st.success(f'Parking updated for {selected_person} on {", ".join(selected_dates)} in {selected_parking}')
            render_parking_data()
    else:
        st.error(f'{selected_person} is not allowed to update {selected_parking}')

if __name__ == '__main__':
    init_csv()  # Initialize CSV files
    reset_persons_table()  # Run this once initially to set up the data
    main()
