
IDS=(3 7 8) 
scenes=(bistro)
current_date=08-22

for SLURM_ARRAY_TASK_ID in "${IDS[@]}"; do
    for scene in "${scenes[@]}"; do
        echo "Processing scene $scene, id $SLURM_ARRAY_TASK_ID"

        directory_name="${current_date}/${scene}"
        mkdir -p "$directory_name"
        filename="${directory_name}/${scene}_${SLURM_ARRAY_TASK_ID}.txt"
        echo "Processing scene $scene with bitrate $bitrate on date $current_date" > "$filename"

        python "/c/Users/15142/Projects/VRR/FRQM/compute_frqm.py" $SLURM_ARRAY_TASK_ID $scene > "$filename"
        wait
    done
done

# git bash
# C:/Users/15142/Projects/VRR/FRQM
# ./compute_frqm.sh