# streamlit_app/dashboard.py
import streamlit as st
import pandas as pd
import requests
import time
import json
import socketio

# Set page title
st.set_page_config(page_title="CSV Processor Dashboard", layout="wide")

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Flask API endpoint
API_URL = "http://localhost:5000"

# Function to fetch data from the Flask API
def fetch_data():
    try:
        response = requests.get(f"{API_URL}/data")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to the server: {str(e)}")
        return []

# Create a SocketIO client
sio = socketio.Client()

@sio.event
def connect():
    st.session_state.connected = True
    st.experimental_rerun()

@sio.event
def disconnect():
    st.session_state.connected = False
    st.experimental_rerun()

@sio.on('csv_update')
def on_csv_update(data):
    st.session_state.data = data
    st.session_state.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
    st.experimental_rerun()

# Try to connect to the SocketIO server if not already connected
if 'connected' not in st.session_state or not st.session_state.connected:
    try:
        sio.connect(API_URL)
    except:
        st.warning("Could not connect to the SocketIO server. Using polling instead.")

# Title and description
st.title("CSV Processor Dashboard")
st.markdown("""
This dashboard displays the most recently processed CSV data from our distributed processing system.
Data is updated in real-time as new CSV files are processed.
""")

# Show connection status
if 'connected' in st.session_state and st.session_state.connected:
    st.success("Connected to real-time updates")
else:
    st.warning("Using polling for updates")
    
    # Add a refresh button when using polling
    if st.button("Refresh Data"):
        data = fetch_data()
        st.session_state.data = data
        st.session_state.last_update = time.strftime("%Y-%m-%d %H:%M:%S")

# Show last update time
if st.session_state.last_update:
    st.write(f"Last updated: {st.session_state.last_update}")

# Display the data
if st.session_state.data:
    # Convert to DataFrame for better display
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df)
    
    # Show some basic statistics
    st.subheader("Data Statistics")
    st.write(f"Number of rows: {len(df)}")
    st.write(f"Number of columns: {len(df.columns)}")
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="processed_data.csv",
        mime="text/csv",
    )
else:
    st.info("No data available yet. Waiting for CSV processing...")

