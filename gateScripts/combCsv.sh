#!/bin/bash
#Kristian Smeland Ytre-Hauge 2025
#First we need the full filename for the first file. we write only the header to the file.
#Secondly we add all the files without the header
#header is written from first file to combined.out
#give first filename
#&& tail -n+2 - q is unclear
#append all files to combined file
head -n 1 Proton_100MeVu_2um_hits_k_50nms_1e8_35_1.csv > combined100.csv && tail -n+2 -q *100MeV* >> combined100.csv

