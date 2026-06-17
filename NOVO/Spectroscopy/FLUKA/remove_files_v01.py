import os
import argparse
import shutil
import numpy as np


files = os.listdir(".")
script_dir = os.path.dirname(os.path.abspath(__file__))

newpath = script_dir

os.makedirs(os.path.join(newpath, "scintillator_interactions"))




for file in files:
    if "scintillator_interactions" in file:
        shutil.move(file, newpath + "/scintillator_interactions"+ "/" + file) 
    if "fort.19" in file or ".log" in file or ".err" in file or ".out" in file or "_test" in file or "exe" in file:
        os.remove(script_dir+"/"+file)
    if file[:3] == "ran":
        os.remove(script_dir+"/"+file)
    



