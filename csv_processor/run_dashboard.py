# run_dashboard.py
import os
import subprocess

if __name__ == '__main__':
    # Run the Streamlit app
    subprocess.run(['streamlit', 'run', 'streamlit_app/dashboard.py'])