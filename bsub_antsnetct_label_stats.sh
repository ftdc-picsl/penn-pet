#!/bin/bash
# Just run QuANTs on already pre-processed PET dadta.
# infile: a two-column csv file, no header row, with the full paths to the
# unprocessed PET file and the T1 BrainSegmentation0N4 image from the ANTsCT
# output directory.

infile=${1}
scriptdir=`dirname $0`

cat ${infile} | while IFS="," read suvr; do
	wd=`dirname ${suvr}`
	t1=`readlink ${wd}/*desc-biascorr_T1w.nii.gz 2>/dev/null | grep -v space`
    bn=`basename ${suvr}`
    fp=(${bn//_/\ })
    subj=${fp[0]/sub-}
    petsess=${fp[1]/ses-}
    
	cmd="bsub -J pet_antsnetct_lstat_${subj}_${petsess} -o ${wd}/pet_antsnetct_lstat_%J_log.txt -n 1 conda run -n pennpet python ${scriptdir}/pet_antsnetct_label_stats.py -i ${suvr} -a ${t1}"

    echo $cmd
    ${cmd}
    
done
