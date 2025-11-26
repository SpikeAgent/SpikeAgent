import subprocess
import sys
import os

def main():
    # Get the directory where this script is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    python = sys.executable
    subprocess.run([
        python, "-m",
        "streamlit", "run", os.path.join(app_dir, "app.py")
    ])

if __name__ == "__main__":
    main()
