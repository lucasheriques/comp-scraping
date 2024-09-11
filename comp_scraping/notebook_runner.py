import subprocess
import webbrowser
import time

def main():
    # Start Jupyter notebook server
    subprocess.Popen(["jupyter", "notebook"])

    # Wait for the server to start
    time.sleep(2)

    # Open the analysis notebook in the default web browser
    webbrowser.open("http://localhost:8888/doc/tree/comp_scraping/data_analysis.ipynb")

if __name__ == "__main__":
    main()
