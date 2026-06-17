#! /bin/bash
spawns=$1
cycles=$2
spots=1
#arg1=$4
#arg2=3
#arg3=$5
#arg4=$6

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
	     echo  "RANDOMIZ          1.      $Nrand. " >> .RAND$i.txt
	     cat first .RAND$i.txt last > "${name}_spawn_${i}.inp"
	     rm .RAND$i.txt
	done
	
	rm first last
	echo ""
	echo "INPUT $name has been replicated $Ninp TIME(S)"
	echo ""
	
	$FLUPRO/flutil/ldpmqmd -o "exe_${name}" source.f fluscw_IFT.f mgdraw_v08.f
	# array for storing process ids
	pids=()
	for (( i=1 ; i<="$spawns"; i++ )); do
	     $FLUPRO/flutil/rfluka -e "exe_${name}" -N0 -M"$cycles" "${name}_spawn_${i}" &
	     pids+=($!)
	done
	wait
	
	python remove_files_v01.py
	
#	bash merge_v02.sh "${j}" "$arg1" "$arg2" "$arg3" "$arg4" 
	
	# --- Kill all rfluka processes for this spot
	echo "Killing all rfluka processes for spot $j"
	kill "${pids[@]}" 2>/dev/null
	
	wait

done

