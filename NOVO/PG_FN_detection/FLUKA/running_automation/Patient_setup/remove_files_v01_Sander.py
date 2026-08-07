import os
import argparse
import shutil

#parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument("param1", type=int, help="spot") 
#parser.add_argument("param2", type=int, help="spawn")  # Define the argument first
args = parser.parse_args()  # Now parse the args
spot = args.param1 
#spawns_no = args.param2 # Access the argument value
#args = parser.parse_args()
# Delete excess fort-files
#parser.add_argument("param1",type=int,help="spot")
fort_files = []
files = os.listdir(".")
script_dir = os.path.dirname(os.path.abspath(__file__))

counter = 0
for file in files:
    break   # Tror ikke dette blir brukt til noe jeg trenger (Sander)
    if "fort.50" in file and counter < spawns_no: # vurder å legge 40 inn som argument
        fort_files.append(file)
        counter+=1
    elif "fort.50" in file and counter == spawns_no:
        file_41 = file.replace("fort.50", "fort.41")
        file_40 = file.replace("fort.50", "fort.40")
        os.remove(script_dir + "/"+ file_41)
        os.remove(script_dir + "/"+ file_40)
        os.remove(script_dir + "/"+ file)
    
    
# Create folder for data

#spot = args.param1

newpath = "Results_spot_" + str(spot)
exist_OK = False
if os.path.exists(newpath):
    #shutil.rmtree(newpath)
    exist_OK = True
os.makedirs(newpath, exist_ok=exist_OK)

# I don't need these in my case (Sander)
#subdirs = ["pg_produced",
#    "FN_produced", "BNNLIS"]

subdirs = ["scintillator_interactions"]

for sub in subdirs:
        os.makedirs(os.path.join(newpath, sub), exist_ok=exist_OK)


# Moving files into a single folder
for file in files:
    # pg_produced from Anna's scripts
    if "pg_produced" in file:
        bnn_file_corresponding = file.replace("pg_produced.txt", "fort.50")
        if bnn_file_corresponding in fort_files:
            shutil.move(file, newpath + "/pg_produced"+ "/" + file) 
        else: 
            os.remove(script_dir + "/"+ file)

    # For FN_produced from Anna's scripts
    if "FN_produced" in file:
        bnn_file_corresponding = file.replace("FN_produced.txt", "fort.50")
        if bnn_file_corresponding in fort_files:
            shutil.move(file, newpath + "/FN_produced"+ "/" + file) 
        else: 
            os.remove(script_dir + "/" + file)

    # For scintillator_interactions.txt-files from Sander's scipts
    if "scintillator_interactions" in file:
        shutil.move(file, newpath + "/scintillator_interactions/" + file)
    
    # Removes files: fort.19, .log, .err, .out and _test
    if "fort.19" in file or ".log" in file or ".err" in file or ".out" in file or "_test" in file: 
        os.remove(script_dir + "/" + file)

    # Removes USRDUMP files
    if "USRDUMP" in file:
        os.remove(script_dir + "/" + file)

    # Moves the "plan"_spot_y.map file to the results folder
    if "spot_" + str(spot) + ".map" in file:
        shutil.move(file, newpath + "/" + file)

    # Removes .ran files
    if file[:3] == "ran":
        os.remove(script_dir + "/" + file)

    # Removes .inp files for each spot
    if ".inp" in file and "spot" in file:
        os.remove(script_dir + "/" + file)
    



