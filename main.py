import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Function to get dates for the next two weeks, filtering out non-working days
def get_dates():
    today = datetime.today()
    dates = []
    while len(dates) < 14:
        if today.weekday() < 5:  # Monday (0) to Friday (4)
            dates.append(today)
        today += timedelta(days=1)
    return [(date.strftime("%Y-%m-%d"), date.strftime("%A")) for date in dates]

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
