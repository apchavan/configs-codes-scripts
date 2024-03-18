#!/bin/bash

# Helper shell script to load latest CSV files into index of Elasticsearch.

# Use below command to ensure this script is executable:
#   sudo chmod +x /PATH/TO/sample_index_name.logstash_run.sh

# This shell script can be added as a root cron-job to run automatically having entry like :
#   00 20 * * * /PATH/TO/sample_index_name.logstash_run.sh

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

# Run `logstash` to load all converted CSV data in index.
sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash/ -f /PATH/TO/sample_index_name.logstash.conf --path.data /PATH/TO/LOGSTASH_CACHE/sample_index_name/data --path.logs /PATH/TO/LOGSTASH_CACHE/sample_index_name/logs

# Finally delete the cache directories or files created during the process.
rm -rf /PATH/TO/BLOBFUSE2_FILE_CACHE_DIRECTORY/*
