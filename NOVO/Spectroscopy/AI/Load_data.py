import os
import numpy as np
from helper_functions import read_composition

'''
Function to load spectroscopy data. Possible datatypes are:
- real data
- bootstrapped data
- synthetic data

'''
    

def load_real_data(data_path, include_proton_counts = False, primaries = 1e8, include_raw_data = False, foldername_kde = "/tki_kde_bin_centers", norm = "log", w_gradient = False):
    X_path = data_path + foldername_kde
    y_path = data_path + "/labels"

    X_files = os.listdir(X_path)
    y_files = os.listdir(y_path)
    
    X_files.sort()
    y_files.sort()

    X_array = np.zeros((len(X_files),350))
    y_array = np.zeros((len(y_files), 3))

    if include_raw_data:
        X_path_rawdata = data_path + "/tki_histogram"
        X_files_rawdata = os.listdir(X_path_rawdata)
        X_files_rawdata.sort()
        X_array_rawdata = np.zeros((len(X_files_rawdata),350))

    # Needs to be filled in when there are different numbers of primaries
    if include_proton_counts:
        proton_counts = np.zeros_like(X_array)
    
    if w_gradient:
        X_array_grad = np.zeros_like(X_array)

    for i in range(len(X_files)):
        X_file = X_files[i]
        X_arr = np.load(X_path + "/" + X_file)["y"][:350] 
        if include_proton_counts:
            proton_counts[i] = np.log10([int(primaries)] * 350)
        if norm == "log":
            X_array[i] = np.log(X_arr + 1) # normalize
        
        if norm == "log+zscore":
            X_array[i] = np.log(X_arr + 1) # normalize
            X_array[i] = (X_arr - X_arr.mean()) / X_arr.std()

        if w_gradient:
            energy = np.load(X_path + "/" + X_file)["x"][:350] 
            X_array_grad[i] = np.gradient(X_array[i], energy)

        if include_raw_data:
            X_file_rawdata = X_files_rawdata[i]
            X_arr_rawdata = np.load(X_path_rawdata + "/" + X_file_rawdata)
            X_arr_rawdata = X_arr_rawdata["hist"][:350]
            if norm == "log":
                X_array_rawdata[i] = np.log(X_arr_rawdata + 1) # normalize
            if norm == "log+zscore":
                X_array_rawdata[i] = np.log(X_arr_rawdata + 1) # normalize
                X_array_rawdata[i] = (X_arr_rawdata - X_arr_rawdata.mean()) / X_arr_rawdata.std()

        y_file = y_files[i]
        composition = read_composition(y_path + "/" + y_file)
        y_array[i] = [composition["Oxygen"], composition["Carbon"], composition["Nitrogen"]]

    if include_raw_data:
        X_array = np.stack([X_array, X_array_rawdata], axis = 2)
    if w_gradient:
        X_array = np.stack([X_array, X_array_grad], axis = 2)

    if include_proton_counts:
        return X_array, y_array, proton_counts
    else:
        return X_array, y_array
    
def load_synthetic_data(synthetic_data_path, include_proton_counts = False, primaries = 1e9):
    
    synthetic_files = os.listdir(synthetic_data_path)
    synthetic_files.sort()

    X_array_syn= np.zeros((len(synthetic_files),350))
    y_array_syn= np.zeros((len(synthetic_files),3))

    if include_proton_counts:
        proton_counts_syn = np.zeros_like(X_array_syn)

    for i in range(len(synthetic_files)):
        synthetic_file = synthetic_files[i]
        X_arr_syn = np.load(synthetic_data_path + "/" + synthetic_file)["y"][:350] # only look up to 7 MeV
        if include_proton_counts:
            proton_counts_syn[i] = np.log10([int(primaries)] * 350)
        X_array_syn[i] = np.log(X_arr_syn + 1) # normalize

        label = np.load(synthetic_data_path + "/" + synthetic_file)["label"] # format O, N, C
        y_array_syn[i] = np.array([label[0], label[2], label[1]]) # format O, C, N 

    if include_proton_counts:
        return X_array_syn, y_array_syn, proton_counts_syn
    else:
        return X_array_syn, y_array_syn


# Denne må testes ordentlig med rådata og proton counts
def load_bootstrapped_data(data_path, include_raw_data = False, proton_multiplicity_num = 9, num_bootstrapped_hist = 10):

    bootstrapped_path_kde = data_path + "/bootstrapped_kde"
    y_path = data_path + "labels"

    bootstrapped_kde = os.listdir(bootstrapped_path_kde)
    bootstrapped_kde.sort()

    X_array_bootstrapped = np.zeros((num_bootstrapped,350))
    y_array_bootstrapped = np.zeros((num_bootstrapped,3))

    protonmulti_array = []
    l = 0

    num_bootstrapped = num_bootstrapped_hist * len(bootstrapped_hist) * proton_multiplicity_num

    if include_raw_data:
        bootstrapped_path_hist = data_path + "/bootstrapped_hist"
        bootstrapped_hist = os.listdir(bootstrapped_path_hist)
        bootstrapped_hist.sort()
        X_array_bootstrapped_hist = np.zeros((num_bootstrapped,350))
        m = 0


    # denne må sjekkes
    for i in range(len(bootstrapped_kde)):
        composition = bootstrapped_kde[i]
        protonmultis = os.listdir(bootstrapped_path_kde + "/" + composition)
        protonmultis.sort()

        y_file = y_path + "/" + composition + ".txt"
        composition_label = read_composition(y_file)

        for j in range(len(protonmultis)):
            protonmulti = protonmultis[j]
            proton_multi_file = bootstrapped_path_kde + "/" + composition + "/" + protonmulti + "/" + composition + ".npz"
            X_array_boot = np.load(proton_multi_file)["bootstrapped_histograms"][:,:350]

            for k in range(X_array_boot.shape[0]):
                X_array_bootstrapped[l] = np.log(X_array_boot[k]+1)
                y_array_bootstrapped[l] = [composition_label["Oxygen"], composition_label["Carbon"], composition_label["Nitrogen"]]
                protonmulti_array.append(int(float(protonmulti)))
                l+=1
            
            # Denne må sjekkes
            if include_raw_data:
                proton_multi_file_hist = bootstrapped_path_hist + "/" + composition + "/" + protonmulti + "/" + composition + ".npz"
                X_array_boot_hist = np.load(proton_multi_file_hist)["bootstrapped_histograms"][:,:350]

                for k in range(X_array_boot.shape[0]):
                    X_array_bootstrapped_hist[m] = np.log(X_array_boot_hist[k]+1)
                    m+=1

    if include_raw_data:
        X_array_bootstrapped = np.stack([X_array_bootstrapped, X_array_bootstrapped_hist], axis = 2)
    
    protonmulti_array = np.array(protonmulti_array)

    return X_array_bootstrapped, y_array_bootstrapped, protonmulti_array
    

def load_real_data_6_element_phantom(data_path, include_neutron_data = False, foldername_kde = "/tki_kde_bin_centers", norm = "log", w_gradient = False, X_length = 499, X_length_nøy = 499):
    X_path = data_path + foldername_kde
    y_path = data_path + "/labels"

    X_files = os.listdir(X_path)
    y_files = os.listdir(y_path)
    
    X_files.sort()
    y_files.sort()

    X_array = np.zeros((len(X_files),X_length))
    y_array = np.zeros((len(y_files), 7))

    if include_neutron_data:
        X_path_neutron = data_path + "/tki_kde_nøy"
        X_files_neutron = os.listdir(X_path_neutron)
        X_files_neutron.sort()
        X_array_neutron = np.zeros((len(X_files_neutron),X_length_nøy))

    
    if w_gradient:
        X_array_grad = np.zeros_like(X_array)

    for i in range(len(X_files)):
        X_file = X_files[i]
        X_arr = np.load(X_path + "/" + X_file)["y"][:X_length] 
        
        if norm == "log":
            X_array[i] = np.log(X_arr + 1) # normalize
        
        if norm == "log+zscore":
            X_array[i] = np.log(X_arr + 1) # normalize
            X_array[i] = (X_arr - X_arr.mean()) / X_arr.std()

        if w_gradient:
            energy = np.load(X_path + "/" + X_file)["x"][:X_length] 
            X_array_grad[i] = np.gradient(X_array[i], energy)

        if include_neutron_data:
            X_file_neutron = X_files_neutron[i]
            X_arr_neutron = np.load(X_path_neutron + "/" + X_file_neutron)
            X_arr_neutron = X_arr_neutron["y"][:X_length_nøy]
            if norm == "log":
                X_array_neutron[i] = np.log(X_arr_neutron + 1) # normalize
            if norm == "log+zscore":
                X_array_neutron[i] = np.log(X_arr_neutron + 1) # normalize
                X_array_neutron[i] = (X_arr_neutron - X_arr_neutron.mean()) / X_arr_neutron.std()

        y_file = y_files[i]
        composition = read_composition(y_path + "/" + y_file)
        y_array[i] = [composition["Oxygen"], composition["Carbon"], composition["Nitrogen"], composition["Hydrogen"], composition["Calcium"], composition["Phosphorus"],composition["Density"]]

    if include_neutron_data:
        return X_array, X_array_neutron, y_array
        X_array = np.stack([X_array, X_array_neutron], axis = 2)
    if w_gradient:
        X_array = np.stack([X_array, X_array_neutron], axis = 2)
    else:
        return X_array, y_array

