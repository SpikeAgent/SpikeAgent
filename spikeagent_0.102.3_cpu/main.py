import subprocess
import sys

def main():
    python = sys.executable
    subprocess.run([
        python, "-m",
        "streamlit", "run", "app.py"
    ])

if __name__ == "__main__":
    main()
