#!/bin/bash
# Stand-alone script for gathering label statistics (via numpy_label_statistics function)
# for the ASHS T1 extended atlas from a PET SUVR image.
# infile: a 6-column csv file, where the columns represent:
#   1. Subject label
#   2. PET session label
#   3. Full path to NIfTI with left-hemisphere ASHS masks
#   4. Full path to NIfTI with right-hemisphere ASHS masks
#   5. String for the BIDS seg-name entity naming the left-hemisphere ASHS T1 extended atlas.
#   6. String for the BIDS seg-name entity naming the right-hemisphere ASHS T1 extended atlas.
# Note that this depends on the pennpet conda environment; the penn-pet Github repo
# (https://github.com/ftdc-picsl/penn-pet/tree/main) contains a .yml file with the enviro
# specifications. Note that it uses conda-forge.

infile=${1}
scriptdir=`dirname $0`

cat ${infile} | while IFS="," read subj petsess ashs_left ashs_right parc_left parc_right; do
	wd="/project/ftdc_pipeline/data/pennpet/sub-${subj}/ses-${petsess}"
    suvr=`ls ${wd}/sub-${subj}_ses-${petsess}_*space-ashst1ext_pet.nii.gz`
    outStem="${suvr/_space-ashst1ext_pet.nii.gz}"
    ashs_label_defs="/project/ftdc_pipeline/data/pet/scripts/penn-pet/ashs_t1_extended_labels.tsv"

	cmd="bsub -J pet_ashs_lstat_${subj}_${petsess} -o ${wd}/pet_ashs_lstat_%J_log.txt -n 1 conda run -n pennpet python ${scriptdir}/pet_any_label_stats.py  -p ${parc_left} ${parc_right} -s ${subj} -t ${petsess} -l ${ashs_left} ${ashs_right} -d ${ashs_label_defs} ${ashs_label_defs} -o ${outStem} -i ${suvr}"

    echo $cmd
    ${cmd}
    
done
