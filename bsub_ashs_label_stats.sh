#!/bin/bash
# Just run QuANTs on already pre-processed PET dadta.
# infile: a two-column csv file, no header row, with the full paths to the
# unprocessed PET file and the T1 BrainSegmentation0N4 image from the ANTsCT
# output directory.

conda activate pennpet

infile=${1}
scriptdir=`dirname $0`

cat ${infile} | while IFS="," read subj petsess ashs_left ashs_right parc_left parc_right; do
    suvr=`ls ${wd}/sub-${subj}_ses-${petsess}_*space-ashst1ext_pet.nii.gz`
	wd=`dirname ${suvr}`
    outStem="${suvr/_space-ashst1ext_pet.nii.gz}"
    ashs_label_defs="/project/ftdc_pipeline/data/pet/scripts/penn-pet/ashs_t1_extended_labels.tsv"

	cmd="bsub -J pet_ashs_lstat_${subj}_${petsess} -o ${wd}/pet_ashs_lstat_%J_log.txt -n 1 python ${scriptdir}/pet_any_label_stats.py  -p ${parc_left} ${parc_right} -s ${subj} -t ${petsess} -l ${ashs_left} ${ashs_right} -d ${ashs_label_defs} ${ashs_label_defs} -o ${outStem} -i ${suvr}"

    echo $cmd
	#$cmd

done
