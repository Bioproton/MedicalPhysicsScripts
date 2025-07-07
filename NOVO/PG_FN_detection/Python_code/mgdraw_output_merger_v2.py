'''
mgdraw output .txt-file merger for several spawns
'''
import os

def output_merger(folder_directory, fluka_run_name=None, mgdraw_output_name=None, overwrite_merged_file=False) -> str:
    # Requires input of what folder to look in: folder_directory
    # fluka_run_name is the name of the selected FLUKA run name. 
    # Example: "NOVO_detector_ab001_parts_leaving_target.txt" should have a fluka_run_name="NOVO_detector"

    # mgdraw_output_name is the name of the selected mgdraw output file
    # Example: "NOVO_detector_ab001_parts_leaving_target.txt" should have a mgdraw_run_name="parts_leaving_target"

    # Returns the merged file name. Will create a _merged.txt-file in same directory as given in {folder_directory}
    # Merged file will contain all inputs of all corresponding output files with corresponding fluka_run_name and mgdraw_output_name

    # If no {fluka_run_name}/{mgdraw_output_name} is given, the code will assume naming parameters from the first file in folder_directory
    # A prompt will be given to make the user confirm that the first file is the wanted file (Y/N)


    # Code does work for multiple runs (i.e. different aa001, aa002-numbers) ONLY if {fluka_run_name} is given
        # It has not been tested, but it should work nonetheless due to aa001 being higher in the folder than aa002

    folder_directory = folder_directory.replace("\\", "/")

    # Finding correct run name if not given
    for filename in os.listdir(folder_directory):
        if fluka_run_name != None and mgdraw_output_name != None:  # Need to find the correct run name if not given. Only performed once
            break
        else:
            name_selection = "A"
            while name_selection != "Y" and name_selection != "N":
                name_selection = input(f"Current file '{filename}' selected. Should output files with similar names med merged? [Y/N]:  ").capitalize()
            if name_selection == "N":
                if os.listdir(folder_directory).index(filename) < 1: # Decides how many filenames that should be examined before stopping. Currently 2 filenames
                    continue
                else:
                    return "Error: Please input fluka_run_name and mgdraw_output_name"
            if name_selection == "Y":
                fluka_run_name = ""
                for j, i in enumerate(filename.split("_")):
                    if "001" not in i:
                        fluka_run_name = "_".join([fluka_run_name, i])
                    else:
                        fluka_run_name = fluka_run_name[1:] # Remove extra "_" in "_filename"
                        # Finds mgdraw_output name. Adds everything after i.e. aa001 and removes .txt at the end
                        mgdraw_output_name = "_".join(filename.split("_")[j + 1:])[:-4]
                        print(f"fluka_run_name: '{fluka_run_name}', mgdraw_output_name: '{mgdraw_output_name}'")
                        break
    # Create new file containing all the merged _detected.txt-results
    merged_file_name = fluka_run_name + "_" + mgdraw_output_name + "_MERGED.txt"
    if os.path.exists(folder_directory + "//" + merged_file_name) and not overwrite_merged_file:
        print(f"Merged file {merged_file_name} already exists, merging aborted")
        return merged_file_name
    merged_file = open(folder_directory + "//" + merged_file_name, "w")   # CAREFUL! Will overwrite if previous file exists
    
    # Finding correct .txt files to merge
    spawn_number = 0
    for filename in os.listdir(folder_directory):
        if fluka_run_name in filename and mgdraw_output_name in filename and "MERGED" not in filename:
            spawn_number += 1
            with open(folder_directory + "//" + filename, "r") as spawn_file:
                # Adding a line with the spawn number as NCASEs might be the same in two different spawns
                merged_file.write(f"Spawn number: {spawn_number} \n")  

                # Writing/appending all lines in _detected.txt files to the merged file
                for line in spawn_file:
                    merged_file.write(line)

                spawn_file.close()

    merged_file.close()
    assert spawn_number != 0, f"No files were found with the combination: {fluka_run_name}_*****_{mgdraw_output_name}.txt"
    print(f"Merged file has been created: {merged_file_name}. \n" 
          "Number of files merged: {spawn_number}")
    return merged_file_name

#test_adress = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\FLUKA\\Delt mappe\\NOVO_detector_bxdraw_16_06_25"
#output_merger(test_adress, fluka_run_name="prompt_gamma_detecc")
#print(output_merger(test_adress))