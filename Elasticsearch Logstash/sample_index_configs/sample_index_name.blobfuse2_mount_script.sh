#!/bin/bash

# Helper script to mount Azure Blob storage container to local directory.

# Use below command to make this script is executable :
#   sudo chmod +x /PATH/TO/sample_index_name.blobfuse2_mount_script.sh

# Below entry should added in '/etc/fstab' file to enable auto-mounting whenever OS reboots:
#   /PATH/TO/sample_index_name.blobfuse2_mount_script.sh    /PATH/TO/MOUNT_DIRECTORY_LOCATION    fuse    defaults,nofail,_netdev,--config-file=/PATH/TO/sample_index_name.blobfuse2_config.yaml    0    0

# Reference 1 : https://github.com/Azure/azure-storage-fuse/issues/921
# Reference 2 : https://learn.microsoft.com/en-us/azure/storage/blobs/blobfuse2-what-is

# First delete contents in cache directory to avoid mounting failures, then `blobfuse2` to mount Azure Blob storage container.
rm -rf /PATH/TO/BLOBFUSE2_FILE_CACHE_DIRECTORY/* && blobfuse2 mount /PATH/TO/MOUNT_DIRECTORY_LOCATION --config-file=/PATH/TO/sample_index_name.blobfuse2_config.yaml
