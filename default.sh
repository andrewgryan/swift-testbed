#!/bin/bash
set -x
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

ssh xcfl00 ls /critical/opfc/suites-oper/global/share/data/*/glm_um/umglaa_pa054.done > done.files
DATES=$(cat done.files | cut -d '/' -f 8)
for DATE in ${DATES} ; do
    DONE_FILE=${WORK_DIR}/../${DATE}.done
    if [[ -e ${DONE_FILE} ]] ; then
        continue
    fi
    mkdir -p ${WORK_DIR}/${DATE}
    cd ${WORK_DIR}/${DATE}
    rsync -av \
        xcfl00:/critical/opfc/suites-oper/global/share/data/${DATE}/glm_um/umglaa_pa0[0-4][0-9] \
        xcfl00:/critical/opfc/suites-oper/global/share/data/${DATE}/glm_um/umglaa_pa05[14] \
       .

    for IN_FILE in $(ls umglaa_pa*[0-9]) ; do

    # Merge/subset cubes
    IN_FILES=${IN_FILE} \
    OUT_FILE=${IN_FILE}.nc \
    COMPRESSION_LEVEL=4 \
    VAR_LIST_PATH=~/roses/forest/app/testbed/file/var_list_small.conf \
    model_data.py
    #    --pressures=30,70,100,150,200,250,300,400,500,600,700,850,925,950,1000

    # Cutout Africa domain
    if [[ -e ${IN_FILE}.nc ]] ; then
        ~/roses/forest/app/gpm_imerg/bin/subset.py \
            --north 38 \
            --south='-36' \
            --east 60 \
            --west='-25' \
            ${IN_FILE}.nc global_africa_${DATE}_${IN_FILE}.nc
    fi
    done

    touch ${DONE_FILE}
done
