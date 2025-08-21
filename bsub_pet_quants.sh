#!/bin/bash
# Just run QuANTs on already pre-processed PET dadta.
# infile: a two-column csv file, no header row, with the full paths to the
# unprocessed PET file and the T1 BrainSegmentation0N4 image from the ANTsCT
# output directory.

infile=${1}
scriptdir=`dirname $0`

cat ${infile} | while IFS="," read f t1; do
	fbase=`basename ${f}`
	fp=(${fbase//_/\ })
	subj=${fp[0]}
	petsess=${fp[1]}
	wd=/project/ftdc_pipeline/data/pet/${subj}/${petsess}
	if [[ ! -d ${wd} ]]; then mkdir -p ${wd}; fi
	cmd="bsub -J pet_quants_${subj}_${petsess} -o ${wd}/pet_quants_%J_log.txt -n 1 ${scriptdir}/run_pet_quants.sh ${f} ${t1}"
        echo $cmd
	$cmd
done

