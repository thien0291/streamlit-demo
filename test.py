from fastapi import FastAPI
import uvicorn
import subprocess

def run_cli_command():
    try:
        subprocess.run(["chainlit", "run", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

app = FastAPI()

@app.get("/")
async def root():
    return run_cli_command()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)