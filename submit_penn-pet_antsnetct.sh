#!/bin/bash
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
	#wd=/project/wolk_4/SCAN/bids/derivatives/pennpet/${subj}/${petsess}
	if [[ ! -d ${wd} ]]; then mkdir -p ${wd}; fi
	logstem=/project/ftdc_pipeline/data/pet/logs/${subj}_${petsess}
	cmd="bsub -J pennpet_${subj}_${petsess} -o ${logstem}_%J_log.txt -n 1 ${scriptdir}/penn-pet_antsnetct.sh ${f} ${t1} ${wd}"
	echo $cmd
	$cmd
done

