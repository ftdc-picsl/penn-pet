#!/bin/bash
# Stand-alone script for running label statistics (via numpy_label_statistics function)
# on PET SUVR image.
# infile: a single-column csv file, giving the full path to the SUVR image. The script
# will look inside the SUVR image directory to find the symlinked antsnetct biascorr image
# and associated antsnetct files.
# Note that this depends on the pennpet conda environment; the penn-pet Github repo
# (https://github.com/ftdc-picsl/penn-pet/tree/main) contains a .yml file with the enviro
# specifications. Note that it uses conda-forge.

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
