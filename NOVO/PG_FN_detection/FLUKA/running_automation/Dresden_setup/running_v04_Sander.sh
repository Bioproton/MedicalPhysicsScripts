#! /bin/bash

spawns=$1
cycles=$2
name=${PWD##*/}
#runs="NOVO1 NOVO2 NOVO3"
runs=$3

for run in $runs; do
	cd $run
	#file_name="${run}/${run_name}"	# Ex.: NOVO41\OncoRay41
	run_name="OncoRay${run##*[!0-9]}_model"	# Get run of current name. Folder needs to match with run value. Ex.: folder NOVO41 -> OncoRay41".inp"
	inp_file="${run_name}.inp"
	echo "$inp_file"

	row=$(grep -n RANDOMIZ ${inp_file} | cut -d : -f 1)
	end=$(grep -c "."  ${inp_file})
	let row=row-1
	let end=end
	let end=end-row-1
	cat  ${inp_file} | head -n ${row} > first
	cat  ${inp_file} | tail -n ${end} > last
	
	for (( i=1; i<=spawns; i++ )); do
	 	 Nrand=$((RANDOM % 900000001))	# Random number from 1 to 9e8
	     echo  "RANDOMIZ          1.$Nrand. " >> .RAND$((i)).txt
	     cat first .RAND$((i)).txt last > "${run_name}_spawn_$((i)).inp"
	     rm .RAND$((i)).txt
	done
	
	rm first last
	echo ""
	echo "INPUT $run_name has been replicated $spawns TIME(S)"
	echo ""
	
	# Compiling mgdraw_v06_OncoRay_model.f with ldpmqmd
	$FLUPRO/flutil/ldpmqmd -o "mgdrawOncoRay" mgdraw_v08_OncoRay_model.f

	# Array for storing process ids
	pids=()

	for (( i=1 ; i<="$spawns"; i++ )); do
	     $FLUPRO/flutil/rfluka -e "mgdrawOncoRay" -N0 -M"$cycles" "${run_name}_spawn_$((i))" &
	     pids+=($!)
	done

	wait
	
	# --- Kill all rfluka processes for this spot
	echo "Killing all rfluka processes for ${run_name}"
	kill "${pids[@]}" 2>/dev/null
	
	wait

	cd -
	
	# Move scintillator_region.txt files to a scintillator_region-folder, and remove other excess files (.inp, .out, .err)
	python remove_files_PTB_Sander.py "${run}"
	
	#wait

done
