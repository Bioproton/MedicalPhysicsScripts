from scipy.stats import gaussian_kde
import numpy as np

def create_KDE(bin_edges_energy_dep, energy_dep_array, save_kde = False, path_to_save = None):

    kde = gaussian_kde(energy_dep_array)

    bin_centers = 0.5 * (bin_edges_energy_dep[1:] + bin_edges_energy_dep[:-1])

    x_kde = bin_centers
    y_kde = kde.evaluate(x_kde)

    y_kde_counts = (bin_edges_energy_dep[1] - bin_edges_energy_dep[0]) * len(energy_dep_array) * y_kde

    if save_kde:
        np.savez(path_to_save, x=x_kde, y=y_kde_counts)

    return y_kde_counts, x_kde

