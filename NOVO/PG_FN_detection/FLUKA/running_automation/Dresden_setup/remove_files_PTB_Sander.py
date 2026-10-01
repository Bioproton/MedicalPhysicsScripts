import os
import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("param1", type=str, help="subfolder") 
args = parser.parse_args()  # Now parse the args
subfolder = args.param1 

script_dir = Path(__file__).resolve().parent
subfolder_path = (script_dir / subfolder).resolve()
files = list(subfolder_path.iterdir())

result_folder = subfolder_path / "scintillator_interactions"
result_folder.mkdir(exist_ok=True)


# Moving files into a single folder
for file in files:
    file_name = file.name

    # For scintillator_interactions.txt-files from Sander's scipts
    if "scintillator_interactions" in file_name:
        shutil.move(str(file), str(result_folder / file_name))
    
    # Remove unwanted files
    if (
        "fort.19" in file_name or
        file_name.endswith(".log") or
        file_name.endswith(".err") or
        file_name.endswith(".out") or
        file_name.endswith(".map") or
        "_test" in file_name or
        "USRDUMP" in file_name or
        file_name.startswith("ran") or 
        file_name.endswith(".inp") and "_spawn_" in file_name or
        file_name == "mgdrawOncoRay"
    ):
        if file.is_file():
            file.unlink()
        continue

    



