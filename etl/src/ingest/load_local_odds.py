from pathlib import Path
import json

def load_local_odds(path: Path):
    with open(path, "r") as file:
        return json.load(file)
    
