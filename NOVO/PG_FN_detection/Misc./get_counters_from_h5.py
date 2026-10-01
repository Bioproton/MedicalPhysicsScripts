"""
Script to read and write .h5 files from ngimager (https://github.com/Lindt8/ng-imager/tree/main/src/ngimager)

Input: Path to .h5 file
Output: .txt file with counter information
"""

def get_counters_from_h5(h5_PATH: str):
    import h5py

    # Sanity check
    assert h5_PATH.endswith(".h5"), f"{h5_PATH} is not a h5-file!"

    # Initializing the .txt-file 
    txt_PATH = h5_PATH[:-3] + "_counters.txt"
    with open(txt_PATH, "w") as txt_file:

        # Loading .h5-file
        with h5py.File(h5_PATH, "r") as h5_file:
            
            # Loading the meta/counter subfolder
            metadata = h5_file["meta/counters"]

            # Get the counter dictionary (saved as attributes)
            counters = dict(metadata.attrs)
            
            # Loop through all entries and paste them in the _counters.txt-file
            for key, item in counters.items():
                txt_file.write(f"{key}: {item}\n")

        h5_file.close()
    txt_file.close()

    print(f"File \"{txt_PATH}\" successfully written")


if __name__ == "__main__":
    test_PATH = r"C:\Users\sathu8821\OneDrive - University of Bergen\NOVO\PTB model\Simulations\2025-12_OncoRay_round2\NOVO51\FLUKA_NOVO_events.h5" 
    get_counters_from_h5(h5_PATH=test_PATH)
