#!/bin/bash
# Processes PET data to create SUVR images.
# Follows BIDS PET standard and expects BIDS-format filenames. 
# Note that subject and session labels cannot contain BIDS-incompatible 
# characters like underscores or periods.
# Command-line arguments.

module unload python/3.10
module load python/3.9

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

export PYTHONPATH=/project/ftdc_misc/jtduda/quants/QuANTs/python/quants:/project/ftdc_volumetric/fw_bids/scripts/Flywheel_python_sdk
petName=$1 # Absolute path of BIDS-format, attentuation-corrected dynamic PET image
t1Name=$2 # Absolute path of N4-corrected, skull-on T1 image from ANTsCT output directory
NetworkDir=/project/ftdc_misc/jtduda/quants/QuANTs


# Record job ID.
# JSP: useful for job monitoring and debugging failed jobs.
echo "LSB job ID: ${LSB_JOBID}"
scriptdir=`dirname $0` # Location of this script

template="/project/ftdc_misc/pcook/quants/tpl-TustisonAging2019ANTs/template_description.json"
adir="/project/ftdc_misc/jtduda/quants/atlases/"

# Parse command-line arguments to get working directory, subject ID, tracer, and PET/MRI session labels.
petdir=`dirname ${petName}` # PET session input directory
bn=`basename ${petName}`
id=`echo $bn | grep -oE 'sub-[^_]*' | cut -d '-' -f 2` # Subject ID
petsess=`echo $bn | grep -oE 'ses-[^_]*' | cut -d '-' -f 2` # PET session label
trc=`echo $bn | grep -oE 'trc-[^_]*' | cut -d '-' -f 2` # PET tracer name.
outdir="/project/ftdc_pipeline/data/pet/sub-${id}/ses-${petsess}"

t1dir=`dirname ${t1Name}`
t1bn=`basename ${t1Name}`
mrisess=`echo $t1bn | grep -oE 'ses-[^_]*' | cut -d '-' -f 2` # MRI session label
wd=${petdir/sub-${id}\/ses-${petsess}} # Subjects directory

# Define session-specific filename variables.
pfx="${outdir}/sub-${id}_ses-${petsess}_trc-${trc}"

# Get label statistics for multiple atlases using QuANTs.
for metricFile in "${pfx}_desc-suvr${mrisess}_pet.nii.gz" "${pfx}_desc-IY${mrisess}_pet.nii.gz" "${pfx}_desc-RVC${mrisess}_pet.nii.gz"; do
    outFile=${metricFile/.nii.gz/_quants.csv}
    python ${scriptdir}/pet_quants.py --template=$template --atlas_dir=${NetworkDir}/atlases --atlas_images=${adir} --output=${outFile} -s ${id} -S ${petsess} ${metricFile} ${t1dir}
done

# JSP: need to at least make the template directory writeable; otherwise, if the script crashes out, it can't be deleted.
chgrp -R ftdclpc ${outdir}
chmod -R 775 ${outdir}

rm -rf ${outdir}/template
