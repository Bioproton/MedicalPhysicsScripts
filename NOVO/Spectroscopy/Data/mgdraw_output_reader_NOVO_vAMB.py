""""
Script with Class with capabilities to process data from NOVCoDA detector simulations

usage: mgdraw_07_detection_reader.py <primaries> <spot> <path>
Example: python mgdraw_07_detection_reader.py 1e7 1 /scratch/binh/tetection/scintillator_interactions/
"""

import numpy as np
import time
import os
import csv
import math
import pandas as pd
import sys
from mgdraw_txt_file_reader_vAMB import collect_txt_data
from time_converter_NOVO import convert_time
import matplotlib.pyplot as plt

class DetectionDataStorage:
    """
    Class to store and process data from NOVCoDA detector simulations
    """

    def __init__(
            self, 
            folder_path: str, 
            primaries_per_spawn: int = 10000000, 
            max_files: int = 100,
            detector: str = "OncoRay"
        ) -> None:

        self.folder_path = folder_path.replace("\\", "/")
        self.primaries_per_spawn = primaries_per_spawn
        self.max_files  = max_files
        self.feature_names = np.array([
            "ncase", "icode", "particle_in", "particle_out", "fnpg_flag",
            "targetZ", "targetA", "energy_out", "energy_in",
            "crash_x", "crash_y", "crash_z", "region", "particle_generation",
            "particle_age", "source_x", "source_y", "source_z", "mreg_prod"
            ])
        self.detector = detector
        
        # List variable to store all entries from the N number of "scintillator_interaction.txt"-files
        self.data = []

        # List-tuple variable to store NCASEs for situations where gamma chains are =3 and neutron chains =2
        # Entries will be on the form [(NCASE_1, LLOUSE_1, regions_1, edeps_1), ...], i.e. [(23421, 1, [4, 7], [0.020, 0.015]]
        # Events are therefore reconstructed

        self.neutron_events = []
        self.double_neutron_events = []     # Default
        self.triple_neutron_events = []
    
        self.gamma_events = []
        self.double_gamma_events = []
        self.triple_gamma_events = []       # Default

    def load_data(self) -> None:    
            
        folder = os.listdir(self.folder_path)
        n_files = len(os.listdir(self.folder_path))
        m = 0   # File counter
        n = 0   # Line counter

        time_stamp = time.time()

        print(f"Reading {n_files} scintillator_interactions.txt-files")

        for filename in folder:
            
            # Skip any other files
            if "scintillator_interactions.txt" not in filename:
                break

            m += 1  # Incement file counter
            if m > self.max_files:
                print(f"Max files reached: {m - 1}/{self.max_files}, stopping data collection")
                break
            data_entry = collect_txt_data(self.folder_path + "\\" + filename, primaries_per_spawn=self.primaries_per_spawn , spawn_number=m) # Shape [eg. (3000, 1), ..., (3000, 1)]
            self.data.append(data_entry)

        self.data = np.transpose(np.concatenate(self.data, axis=1))
        
        print(f"Total time used on data collection: {round(time.time() - time_stamp,2)} s")


    def filter_hits(self, time_structure = "pulsed", beam_current=2, write_hits_to_file=False):
        '''
        This function will first scrape together all hits for a certain NCASE (one history)
        It will then try to shape an event from whatever has happened into something that is reasonable

        time_structure:
        Convertion from FLUKA times, i.e. time from primary generation, to time in "real life", i.e. IBA cyclotron at OncoRay, Dresden (106.3 MHz)
        None        :   Does not convert times from FLUKA times to real life times (i.e. all primary protons start at the same time)
        "continuous":   Completely continuous time structure. Releases 117.6 protons smoothed out over 9.4 nanoseconds
        "pulsed"    :   Semi-contiuous/pulsed, and should be the most realistic. Releses bunches of 117.6 protons per 9.4 nanoseconds

        beam_current:
        Used in the conversion from FLUKA times to cyclotron times. Unit: nA
        Default: 2 [nA]
        '''

        # Burner variables
        self.all_hits = []    # All hit histories
        self.gamma_hits = []  # All hit histories for gammas, ICODE = [219, 217, 221] minus [208, 214]
        self.neutron_hits = []    # All hit histories for neutrons, ICODE = [100, 101, 103, 106, 300]
        self.combo_hits = []  # All hit histories where multiple interactions in the same scintillator are a combination of gamma + neutron

        # Time recorder
        time_stamp = time.time()
        print(f"\n-----------ICODE FILTERING-----------")


        # Collecting all the data and storing them in more descriptive variables
        ncases = self.data[:, 0]
        rejected_icodes = np.array([225, 210, 212, 215, 102])  # Rayleigh, Møller, Bhabha, Annihilation at rest, Particle radioactive decay

        if len(ncases) > 1:
            ncase_change_idx = np.where(np.diff(ncases) != 0)[0] + 1
            ncase_groups = np.split(self.data, ncase_change_idx)

        # List to store all hit histories
        raw_all_hit_histories = []

        for current_ncase_data in ncase_groups:
            
            
            prod = current_ncase_data[:, 15:18]
            if len(current_ncase_data) > 1:
                prod_change = np.where(np.any(np.diff(prod, axis=0) != 0, axis=1))[0] + 1
                prod_groups = np.split(current_ncase_data, prod_change)
            else:
                prod_groups = [current_ncase_data]

            for grp in prod_groups:
                
                init_prod_coord = grp[0, 15:18].copy()
                raw_ncase_hit_history = []  # Will store hits for the current ncase x production coordinate

                
                # Extract icodes for iteration
                icodes = grp[:, 1]

            # --------------ICODE PRE-FILTERING--------------
            
                for index, icode in enumerate(icodes):

                    
                    if not np.array_equal(grp[index, 15:18], init_prod_coord):
                        if raw_ncase_hit_history != []:
                            raw_all_hit_histories.append(np.array(raw_ncase_hit_history))
                        init_prod_coord = grp[index, 15:18]
                        raw_ncase_hit_history = []

                    raw_hit = grp[index].copy() 

                    if icode in rejected_icodes:
                        continue
                    # --------------GAMMA ICODE FILTERING--------------

                    # Compton scattering : [7, 7] x [7, 3]
                    if icode == 219:

                        # Skip scattered photon entry
                        if raw_hit[3] == 7:
                            continue

                    # Photoelectric effect : [7, 3]
                        # No changes required
                    
                    # Pair production : [7, 4] and [7, 3]
                        # No changes required
                    
                    # Annihilation at flight (>100 keV) :  [4, 7] -> [4, 7] 
                    elif icode == 214:
                        
                        # We only need information from the first entry
                        if current_ncase_data[index - 1][1] == 214:     # NB: Will produce bug if two 214 pairs occur right after each other, i.e [214, 214, 214, 214]
                            continue

                    # Bremsstrahlung generation (electron/positron only) : [3, 3] x [3, 7] or [4, 4] x [4, 7]
                    elif icode == 208:
                        
                        # Skip photon entry, we only need the remaining energy for the electron/positron
                        if raw_hit[3] == 7:
                            continue

                    # --------------NEUTRON/HADRON ICODE FILTERING--------------
                    
                    # Elastic scattering (KE > 20 MeV)
                    elif icode == 100:

                        # "Rogue" primary protons
                        # [1, 1] + [1, -2] (p, HeavyIon)-scatter
                        # [1, 1]        
                        # [1, 1] + [1, 1] (p, p)-scatter
                        # Not sure how to deal with these, so they are skipped
                        if raw_hit[2] == 1:
                            continue

                        # Either a single [8, 8]-hit or an entry that is followed up by [8, -2] / [8, 1]
                        elif raw_hit[2] == 8 and raw_hit[3] == 8:
                            continue 
                            
                        # Skip scattered deutereon in [-3, -3] -> [-3, 1]-hit
                        elif raw_hit[2] == -3 and raw_hit[3] == -3:
                            continue
                    
                    # Inelastic collision
                    elif icode == 101:

                        # Skip entries on neutron-neutron scatters
                        if raw_hit[3] == 8:
                            continue

                        # Skip proton-deutereon scatter
                        elif raw_hit[2] == 1 and raw_hit[3] == -3:
                            continue

                    # Delta-ray generation [1, 1] -> [1, 3] or [-3, -3] -> [-3, 3]
                    elif icode == 103: 
                        
                        # Skip entries with scattered proton/deuteron (that created the electron)
                        if raw_hit[3] == 1 or raw_hit[3] == -3:
                            continue
                        
                    # De-exicitation in-flight (usually production of PG)
                    elif icode == 106:

                        # Not interested in the PG energy
                        if raw_hit[3] == 7:
                            continue

                    # Elastic "low energy" neutron scattering (KE<20 MeV)
                    elif icode == 300:
                        
                        # Skip entries about scattered neutrons or [1H + n -> 2H + gamma]-entries
                        if raw_hit[3] == 8 or raw_hit[3] == 7:
                            continue

                    # Ion splitting up into secondaries (deutereon -> proton + neutron)
                    elif icode == 99:
                        
                        # Skip neutron entry
                        if raw_hit[3] == 8:
                            continue
                
                    # At this point only desired hits should have been included
                    # Replacing FLUKA relative time with global times
                    if time_structure != None:
                        raw_hit[14] = convert_time(current_ncase_data[index][0], current_ncase_data[index][14], time_structure=time_structure, beam_current=beam_current)
                    
                    # Add the hit to the ncase history
                    raw_ncase_hit_history.append(raw_hit)

            # If there are no energy depositions in this history, skip to next ncase/production coordinate
            if raw_ncase_hit_history == []:
                continue

            # The history for this production coordinate has been built. Converting to numpy array and save it
            raw_ncase_hit_history = np.array(raw_ncase_hit_history)
            raw_all_hit_histories.append(raw_ncase_hit_history)
            
        print(f"Raw hit filtering complete. Time used: {round(time.time() - time_stamp, 2)} s")
        print(f"Total number of lines: {len(self.data)}")
        lines_kept = sum([len(i) for i in raw_all_hit_histories])
        lines_rejected = len(self.data) - lines_kept
        print(f"Number of lines kept: {sum([len(i) for i in raw_all_hit_histories])} ({round(100 * lines_kept / len(self.data), 1)}%)")
        print(f"Number of lines rejected: {len(self.data) - sum([len(i) for i in raw_all_hit_histories])} ({round(100 * lines_rejected / len(self.data), 1)}%)")


        #-----------HIT MERGING-----------
        print(f"\n-----------HIT MERGING-----------")
        time_stamp = time.time()

        # Step 1: Merge hits within the same bar within 400 ns (0.4 µs) [from the same NCASE]
        time_merged_all_hit_histories = []
        time_limit = 0.4 # µs   [400 ns signal time, based on Table 5 in Deliverable 1.1]
        overlap_num = 0

        for hit_history in raw_all_hit_histories:

            hit_regions = hit_history[:, 12]

            # Check if hits occur within the same scintillator bars
            unique_hit_regions, region_indicies, region_counts = np.unique(hit_regions, return_index=True, return_counts=True)
            sorted_order = np.argsort(region_indicies)

            for index in sorted_order:

                region = unique_hit_regions[index]
                count = region_counts[index]

                merge_hits_mask = hit_regions==region  # Mask for which hits that overlap
                hits_to_be_merged = hit_history[merge_hits_mask]
                
                # Regions/scintillators with more than one hit
                if count > 1:
                    overlap_num += 1
                    merged_hits = self._merge_hits(hits_to_be_merged, time_limit=time_limit)    # Might be one or several merged hits, depending on clustering

                    for hit in merged_hits:
                        
                        # Skip empty entries
                        if hit.ndim == 1:
                            continue

                        time_merged_all_hit_histories.append(hit)
                
                # Regions/scintillators with only one hit
                else:
                    time_merged_all_hit_histories.append(hits_to_be_merged)

                
        time_merged_all_hit_histories = np.array(time_merged_all_hit_histories, dtype=object)

        print(f"Merging complete. Time used: {round(time.time() - time_stamp, 2)} s")
        print(f"Overlaps found: {overlap_num}")

        # Saving values and removing self.data from memory
        self.data = None

        time_stamp = time.time()

        # Need to split up hits into gammas, neutrons and combos
        for hit_history in time_merged_all_hit_histories:

            gamma = False
            neutron = False
            if hit_history.ndim == 1:
                print(hit_history)
            icodes = hit_history[:, 1]
            
            for icode in icodes:
                if icode in [217, 219, 221, 103]:  # 208s and 214s are excluded. They cannot be "singular hits", aka "negative" energy deposit. 103 is counted as gamma. Delta-ray generation threshold: 100 keV
                    gamma = True
                elif icode in [100, 101, 106, 300, 99]:
                    neutron = True
                elif icode == 500:
                    gamma = True
                    neutron = True

            if gamma and not neutron:
                self.gamma_hits.append(hit_history)
            elif neutron and not gamma:
                self.neutron_hits.append(hit_history)
            elif gamma and neutron:
                self.combo_hits.append(hit_history)
        
        # Convert lists into numpy arrays
        self.gamma_hits = np.concatenate(self.gamma_hits, axis=0)
        self.neutron_hits = np.concatenate(self.neutron_hits, axis=0)
        self.combo_hits = np.concatenate(self.combo_hits, axis=0)

        # Remove all singular hits that contribute negatively, and that has not been merged ("negative" energy deposit)        
        self.gamma_hits = self.gamma_hits[~np.isin(self.gamma_hits[:, 1], [103, 208, 214])]
        self.neutron_hits = self.neutron_hits[~np.isin(self.neutron_hits[:, 1], [103, 208, 214])]
        self.combo_hits = self.combo_hits[~np.isin(self.combo_hits[:, 1], [103, 208, 214])]

        # Filter away hits with energy deposit lower than 10 keV (gammas) and 200 keV (neutrons)
        self.gamma_hits = self.gamma_hits[~(self.gamma_hits[:, 7] < 0.010)]  # Remove instances where the energy deposit is lower than 10 keV
        self.neutron_hits = self.neutron_hits[~(self.neutron_hits[:, 7] < 0.200)]  # Remove instances where the energy deposit is lower than 200 keV
        self.combo_hits = self.combo_hits[~(self.combo_hits[:, 7] < 0.200)]  # Remove instances where the energy deposit is lower than 10 keV

        # All hits are the combination of the rest (allows differential energy cutting)
        self.all_hits = np.concatenate((self.gamma_hits, self.neutron_hits, self.combo_hits))
        
        print(f"Total number of hit histories > 10/200 keV: {len(self.all_hits)}")
        print(f"Number of gamma hit histories > 10 keV: {len(self.gamma_hits)}")
        print(f"Number of neutron hit histories > 200 keV: {len(self.neutron_hits)}")
        print(f"Number of combo hit histories > 200 keV: {len(self.combo_hits)}")

        if write_hits_to_file == True:

            # Writing gamma hit file
            with open(self.folder_path[:-25] + r"gamma_hits.txt", "w") as gamma_file:
                for hit in self.gamma_hits:
                    hit_str = ""
                    for hit_value in hit:
                        hit_str += str(round(hit_value, 5)) + "  "
                    gamma_file.write(hit_str + "\n")

            gamma_file.close()
            print(self.folder_path[:-25] + r"gamma_hits.txt successfully created")

            # Writing neutron hit file
            with open(self.folder_path[:-25] + r"neutron_hits.txt", "w") as neutron_file:
                for hit in self.neutron_hits:
                    hit_str = ""
                    for hit_value in hit:
                        hit_str += str(round(hit_value, 5)) + "  "
                    neutron_file.write(hit_str + "\n")

            neutron_file.close()
            print(self.folder_path[:-25] + r"neutron_hits.txt successfully created")

            # Writing all hits file
            with open(self.folder_path[:-25] + r"all_hits.txt", "w") as all_hits_file:
                for hit in self.all_hits:
                    hit_str = ""
                    for hit_value in hit:
                        hit_str += str(round(hit_value, 5)) + "  "
                    all_hits_file.write(hit_str + "\n")
            
            all_hits_file.close()
            print(self.folder_path[:-25] + r"all_hits.txt successfully created")


    def _merge_hits(self, hit_array, time_limit=0.4):
        """
        Merges hits occuring in the same region (=scintillator)
        hit_array: Hits to be merged. Structure: np.array([Hit1, Hit2, ..., HitN])
        time_limit [µs]: Assumed signal length of an energy deposition. If two hits occur with more time seperation than this, they will not be merged
        """

        merged_hits = []

        interaction_times = hit_array[:, 14]

        # Copilot assisted solution: 
        time_differences = np.abs(interaction_times[:, None] - interaction_times[None, :])  # Absolute difference matrix
        hit_pairs = np.argwhere((time_differences < time_limit) & (time_differences >= 0))    # Pairs that are within the time limits (duplicates)

        unique_hit_pairs = hit_pairs[hit_pairs[:, 0] > hit_pairs[:, 1]] # Gets rid of the dupes: [0, 1], [1,0] -> [0, 1]

        hit_clusters = self._clusters_from_pairs(unique_hit_pairs) # Clusters the pairs: [(1, 2), (0, 1), (3, 4)] will turn into [(0, 1, 2), (3, 4)]

        for hit_cluster in hit_clusters:
            hits_2_be_merged = hit_array[hit_cluster]
            icodes = hits_2_be_merged[:, 1]

            total_energy_deposited = 0

            gamma = False
            neutron = False
            

            for index, icode in enumerate(icodes):
                if icode in [217, 219, 221, 103]:
                    # All these energies contribute positively 
                    # 103 is noted as a gamma because I assume you cannot know whether this electron comes from a gamma or 
                    total_energy_deposited += hits_2_be_merged[index, 7]
                    gamma = True

                elif icode in [100, 101, 106, 300]:
                    # All these energies contribute positively (assumption)
                    total_energy_deposited += hits_2_be_merged[index, 7]
                    neutron = True

                elif icode == 214:
                    total_energy_deposited -= hits_2_be_merged[index, 8]    # index 8 because we are interested in how much energy the positron had left before it annihilated
                    gamma = True

                elif icode == 208:
                    total_energy_deposited -= hits_2_be_merged[index, 7]
                    gamma = True
                
            if gamma and not neutron:
                merge_icode = 219   # Assuming all gamma hits to be Compton scatters
                particle_in = 7     # Gamma
                particle_out = 3    # Electron
            elif neutron and not gamma:
                merge_icode = 300   # Assuming all neutron hits to be (n, p)-scatters
                particle_in = 8     # Neutron
                particle_out = 1    # Proton
            elif gamma and neutron:
                merge_icode = 500  # Combinations does not have an ICODE. I make my own pseduo-ICODE: 500 (Neutron-gamma combo)
                particle_in = 0     # Pseudoparticle
                particle_out = 0    # Pseudoparticle

            # If total enery is below zero, set it to 0
            total_energy_deposited = max(total_energy_deposited, 0)

            # Bug catcher to find ICODEs that have not been handled
            if "merge_icode" not in locals():
                print(icodes)

            merged_hits.append(hits_2_be_merged[0]) # Use one of hits as structure


            merged_hits[-1][1] = merge_icode   # Alter the hit ICODE
            merged_hits[-1][7] = round(total_energy_deposited, 5) # Implant the merged energy deposited
            merged_hits[-1][8] = 1000.0            # Impossible to determine a singular incoming energy. Set it to a recognisable 1000 [MeV]

            merged_hits[-1][2] = particle_in    # Replacing particle_in
            merged_hits[-1][3] = particle_out    # Replacing particle_out

        """
        BACKGROUND:
        Hits that contribute to energy deposition
        219 (Compton)[Electron]: +
        221 (Photoelectric)[Electron]: +
        217 (Pair production) [Electron + positron]: +
       
        100 (Elastic collision) [Proton, HeavyIon]: +
        101 (Inelastic collision) [Proton, Alpha, HeavyIon]: +    (Chaotic)
        103 (Delta ray-generation) [Electron]: +
        106 (PG de-excitation) [HeavyIon]: +
        300 (Elastic collision, Ek_n < 20 MeV) [Proton, HeavyIon]: +

        Hits that hinders/reduces energy deposition
        208 (Bremsstrahlung) [Electron]: -
        214 (Annihilation in-flight)[Positron]: -
        """

        return np.array([merged_hits])

    def _clusters_from_pairs(self, pairs):
        """Clusters pairs that are edge-adjacent: 
        [(1, 2), (0, 1), (3, 4)] will turn into [(0, 1, 2), (3, 4)]
        Code entirely from Copilot
        """
        # Build adjacency list graph
        graph = {}
        for a, b in pairs:
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)
        
        visited = set()
        clusters = []

        # Depth-first search to find connected components
        for node in graph:
            if node not in visited:
                stack = [node]
                component = []
                visited.add(node)

                while stack:
                    u = stack.pop()
                    component.append(u)
                    for v in graph[u]:
                        if v not in visited:
                            visited.add(v)
                            stack.append(v)
                clusters.append(sorted(component))
        return clusters
    
    def event_builder(self, write_ngimager_file=False):
        """
        Will sort self.gamma_hits() and self.neutron_hits() to construct:
        1) self.gamma_events() and self.neutron_events() 

            structure: np.array([
            [[hit1], [hit2], [hit3]],
            [[hit1]],
            [[hit1], [hit2], [hit3], [hit4]]
            ])
        2) self.double_gamma_events, self.triple_gamma_events, self.double_neutron_events, self.triple_neutron_events

            structure double events: np.array([
            [[hit1], [hit2]],
            [[hit1], [hit2]],
            [[hit1], [hit2]]
            ])

            structure triple events: np.array([
            [[hit1], [hit2], [hit3]],
            [[hit1], [hit2], [hit3]],
            [[hit1], [hit2], [hit3]]
            ])

        3) Write an input file for ngimager using self.triple_gamma events and double neutron events
            This is by default set to False
            Location of the file is self.folder_path[-26]\ (one folder up from scintillator_interactions)

        4) Write gamma/neutron hits to .txt files
        """

        # 1) Construct events from hits
        # Gammas
        self.gamma_events = self._event_builder(self.gamma_hits)
        print("Event summary for gammas:")
        self._count_hits_per_event(self.gamma_events)

        # Neutrons
        self.neutron_events = self._event_builder(self.neutron_hits)
        print("Event summary for neutrons:")
        self._count_hits_per_event(self.neutron_events)

        # 2) Filter out double/triple events
        # Sorting out double and triple gamma/neutron events

        # Gammas
        self.double_gamma_events = [event[0:2] for event in self.gamma_events if len(event) >= 2]
        self.triple_gamma_events = [event[0:3] for event in self.gamma_events if len(event) >= 3]

        # Neutrons
        self.double_neutron_events = [event[0:2] for event in self.neutron_events if len(event) >= 2]
        self.triple_neutron_events = [event[0:3] for event in self.neutron_events if len(event) >= 3]

        # 3) Write .h5 file for ngimager
        if write_ngimager_file == True:
            self._write_ngimager_input()

    
    def _event_builder(self, hit_array):
        """
        Helper function for event_builder
        Inputs: hit array, i.e. self.gamma_hits or self.neutron_hits
        Output: event array, self.gamma_events or self.neutron_events
        """

        event = []  #[[hit1], [hit2], [hit3], ..., [hitN]]
        particle_events = []    # [[[hit1], [hit2], [hit3]], [[hit1], [hit2]], ...] # Final event list, i.e. self.gamma_events or self.neutron_events
        event_ID = [0, 0.0, 0.0, 0.0]   # [NCASE, prodX, prodY, prodZ], ID to sort hits into the same event

        for hit in hit_array:
                        # A change in event_ID means that there is a new event
            if event_ID != [hit[1], hit[15], hit[16], hit[17]]:

                # Add the event if it is not the beginning event
                if event_ID != [0, 0.0, 0.0, 0.0]:
                    particle_events.append(event)

                # Reset event
                event = [hit]
                event_ID = [hit[1], hit[15], hit[16], hit[17]]

            else:
                event.append(hit)

        # Add the final event
        particle_events.append(event)

        return particle_events
    
    def _count_hits_per_event(self, event_array):
        """
        Helper function for event_builder. Will summarise the number of hits in events
        Input: event array, i.e. self.gamma_events or self.neutron_events
        Output: print statements about number of hits per event and their counts, i.e. 1 hit : 50203, 2 hits : 4120, 3 hits : 120
        """

        # Collect the number of hits per event
        event_chain = []
        for event in event_array:
            event_chain.append(len(event))

        # Convert to numpy and counting how many events with 1 hit, 2 hits, 3 hits etc.
        event_chain = np.array(event_chain)
        chain_lengths, chain_lengths_counts = np.unique(event_chain, return_counts=True)

        for chain_length, chain_length_count in zip(chain_lengths, chain_lengths_counts):
            if chain_length == 1:
                print(f" {chain_length} hit : {chain_length_count}")
            else:
                print(f" {chain_length} hits : {chain_length_count}")

    def _write_ngimager_input(self):
        """
        Will write input file for ngimager code
        Based on script written by Thanh Binh Phan
        """

        event_number = 0    # Variable to be incremented

        header_lines = ["!Required final counter 1 value =       2 ; Required final counter 2 value =       3", 
                "!       #iomp    #batch  #history       #no     #name        #reg  EdepA(MeV)      xA(cm)      yA(cm)      zA(cm)      tA(ns)        #reg  EdepB(MeV)      xB(cm)      yB(cm)      zB(cm)      tB(ns)        #reg  EdepC(MeV)      xC(cm)      yC(cm)      zC(cm)      tC(ns)" 
                ,"!ncol   Z   N jcl kcl nclsts", "!In/Out kf-code     E(MeV)      weight", " "]

        with open(self.folder_path[:-25] + r"FLUKA_NOVO_events.out", "w") as ngimager_file:
            # Write header lines first
            for line in header_lines:
                ngimager_file.write(line + '\n')

            # Write event lines for gammas
            for event in self.triple_gamma_events:
                #print(event)
                event_number += 1
                event_string = self._convert_to_ngimager_event(event, event_number, "gamma")
                ngimager_file.write(event_string + "\n\n")

            # Write event lines for neutrons
            for event in self.double_neutron_events:
                event_number += 1
                event_string = self._convert_to_ngimager_event(event, event_number, "neutron")
                ngimager_file.write(event_string + "\n\n")

        ngimager_file.close()
        print(self.folder_path[:-25] + r"FLUKA_NOVO_events.out successfully created")
        
    
    def _convert_to_ngimager_event(self, event, event_number, particle):
        """
        Helper function for _write_ngimager_input
        Converts this codes event = [[[hit1], [hit2], [hit1], [hit2]]]
        to ngimager's required events = [[hit1 ; hit2], [hit1 ; hit2]] with formatting rules
        
        inputs: 
            - event to be converted
            - particle (gamma or neutron): ["gamma", "neutron"]
        output: string
        """
        assert particle in ["gamma", "neutron"], f"Particle input {particle} not accepted"
        
        if particle == "gamma":
            name = "ge"
        elif particle == "neutron":
            name = "ne"

        final_string = f"{name} 0 0 0 {event_number} 0 ;"

        hit_string = ""
        
        # Variables: Region, energy deposited (MeV), X, Y, Z, time
        # Indicies: 12, 7, 9, 10, 11, 14
        # My times are in µs, so they are multiplied by 1000 to gain ns
        for hit in event:
            hit_string = f" {int(hit[12])}  {round(hit[7], 5)} {hit[9]} {hit[10]} {hit[11]} {1000 * round(hit[14], 3)} ,"
            final_string += hit_string
        
        return final_string