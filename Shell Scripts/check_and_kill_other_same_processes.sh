#!/bin/bash

# Get actual name of script that is currently running without having path separators.
script_base_name=$(basename -- "$0")

# Get all process ID(s) of same script using `pgrep` command.
# If there's more than one instances running, the older instance process ID will also get returned.
pids=(`pgrep -f $script_base_name`)
pids="${pids[@]}"

# Get total count of those process ID(s).
pid_count=0
for pid_value in $pids; do
    pid_count=$((pid_count + 1))
done

# Get group ID for current executing process.
current_process_group_id=$(($(ps -o pgid= -p "$$")))

# If `pid_count` is greater than 1, it means other instance(s) are also running.
# If so, kill older processes before proceeding with this one.
if [ $pid_count -gt 1 ]; then
    # Iterate over collection of `pids`.
    for pid_value in $pids; do
        process_group_id=$(($(ps -o pgid= -p "$pid_value")))

        # Before terminating, check if group ID of selected `pid_value`
        # does not match with current process group ID itself.
        if [ $process_group_id -ne $current_process_group_id ]; then
            # Use `kill` command to kill tree of older processes.
            # Reference : https://stackoverflow.com/a/15139734
            kill -- -$(ps -o pgid= $pid_value | grep -o [0-9]*)
        fi
    done
fi

# Above commands will ensure that any other same process or related child(s) is killed and the current process will only exist in memory. Only current process in memory can execute or call the commands written below, if specified.


# WRITE CUSTOM COMMANDS HERE AND ONLY CURRENT PROCESS EXECUTES THEM.
