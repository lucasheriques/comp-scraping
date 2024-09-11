import subprocess
import webbrowser
import time
import os

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the notebook
    notebook_path = os.path.join(current_dir, 'data_analysis.ipynb')

    # Start Jupyter notebook server in the background
    subprocess.Popen(["jupyter", "notebook"])

    # Wait for the server to start
    time.sleep(2)

    # Open the analysis notebook directly in the default web browser
    webbrowser.open(f"http://localhost:8888/doc/tree/comp_scraping/data_analysis.ipynb")

if __name__ == "__main__":
    main()
