#! /bin/bash

spawns=$1
cycles=$2
spots=$3

name=${PWD##*/}
Ninp=$1
ext='.inp'
fullname=$name$ext


for (( j=1 ; j<="$spots"; j++ )); do
	echo "$fullname"

	row=$(grep -n RANDOMIZ ${fullname} | cut -d : -f 1)
	end=$(grep -c "."  ${fullname})
	let row=row-1
	let end=end
	let end=end-row-1
	cat  ${fullname} | head -n ${row} > first
	cat  ${fullname} | tail -n ${end} > last
	
	for (( i=1; i<="$Ninp"; i++ )); do
	 Nrand="$i"
	     echo  "RANDOMIZ          1.      $Nrand. " >> .RAND$((i+99)).txt
	     cat first .RAND$((i+99)).txt last > "${name}_spot_${j}_spawn_$((i + 99)).inp"
	     rm .RAND$((i+99)).txt
	done
	
	rm first last
	echo ""
	echo "INPUT $name has been replicated $Ninp TIME(S)"
	echo ""
	
	# Compiling source_i.f and mgdraw_v06_patient_detection.f with ldpmqmd
	$FLUPRO/flutil/ldpmqmd -o "${name}_spot_${j}" source_${j}.f ../mgdraw_v06_patient_detection.f

	# Array for storing process ids
	pids=()

	for (( i=1 ; i<="$spawns"; i++ )); do
	     $FLUPRO/flutil/rfluka -e "${name}_spot_${j}" -N0 -M"$cycles" "${name}_spot_${j}_spawn_$((i + 99))" &
	     pids+=($!)
	done

	wait

	
	# Move scintillator_region.txt files to a scintillator_region-folder, and remove other excess files (.inp, .out, .err)
	python remove_files_v01_Sander.py "${j}"
	
	# --- Kill all rfluka processes for this spot
	echo "Killing all rfluka processes for spot $j"
	kill "${pids[@]}" 2>/dev/null
	
	wait

done

