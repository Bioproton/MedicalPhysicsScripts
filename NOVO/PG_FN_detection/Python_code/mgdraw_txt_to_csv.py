"""
Simple script to go from ..._merged.txt-files from mgdraw to csv-files
Formatting change
"""
import os
import csv
from mgdraw_txt_file_reader import collect_detection_data

txt_file_directory = r"C:\\Users\\sathu8821\\OneDrive - University of Bergen\\NOVO\\FLUKA\\Delt mappe\\mgdraw_detection_results_28_04_25\\prompt_gamma_300425_gammas_detected_merged.txt"
primaries_per_spawn = 200000


csv_file_directory = txt_file_directory[:-3] + "csv"
txt_file = open(txt_file_directory, "r")


n, mother_ncase, current_icode, previous_icode, incoming_particle, outgoing_particle, scatter_avoided, secondary_particle_energy, \
    mother_particle_energy, Xs, Ys, Zs, Xs_source, Ys_source, Zs_source, energy_in_bins = collect_detection_data(txt_file_directory, primaries_per_spawn=primaries_per_spawn)

with open(csv_file_directory, "w", newline="") as csv_file:
    csv_file_writer = csv.writer(csv_file)
    csv_file_writer.writerow([\
        "x", "y", "z", "sourceX", "sourceY", "sourceZ", "PDG", "edepMeV", "trackLocalTime", "trackID", "parentID", "eventID", "targetA", "targetZ", "processName"\
            ])
    for i in range(len(mother_ncase)):
        #csv_file_writer.writerow([mother_ncase[i], current_icode[i], previous_icode[i], Xs[i], Ys[i], Zs[i], Xs_source[i], Ys_source[i], Zs_source[i]])
        if outgoing_particle[i] == 3 and scatter_avoided[i] == 1: # If particle == 3 (electron), then write csv file. (Kinetic energy of electron = energy deposited)
            csv_file_writer.writerow([\
                 Xs[i], Ys[i], Zs[i], Xs_source[i], Ys_source[i], Zs_source[i], 22, round(1000 * secondary_particle_energy[i], 6), i, 1, 0, mother_ncase[i], 0, 0, current_icode[i]\
                    ])
csv_file.close()




