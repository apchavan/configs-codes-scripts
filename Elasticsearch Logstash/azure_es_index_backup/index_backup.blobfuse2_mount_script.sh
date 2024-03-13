#!/bin/bash

# Use below command to ensure this script is executable:
#   sudo chmod +x /PATH/TO/index_backup.blobfuse2_mount_script.sh

# Below entry is added in '/etc/fstab' file:
#   /PATH/TO/index_backup.blobfuse2_mount_script.sh    /PATH/TO/MOUNT_DIRECTORY_LOCATION    fuse    defaults,nofail,_netdev,--config-file=/PATH/TO/index_backup.blobfuse2_config.yaml    0    0

# This shell script is responsible to mount Azure Blob container to local system.

rm -rf /PATH/TO/CACHE_DIRECTORY/* && blobfuse2 mount /PATH/TO/MOUNT_DIRECTORY_LOCATION --config-file=/PATH/TO/index_backup.blobfuse2_config.yaml
