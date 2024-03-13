#!/bin/bash

# Use below command to ensure this script is executable:
#   sudo chmod +x /PATH/TO/index_backup.run.sh

# This shell script is responsible to remove existing & create new backup of all Elasticsearch indices in Azure Blob Storage container.

# This shell script is configured to run as cron job, once everyday:
#   30 18 * * * /PATH/TO/index_backup.run.sh >/dev/null 2>&1

# Reference 1 : https://www.elastic.co/guide/en/elasticsearch/reference/current/repository-azure.html
# Reference 2 : https://www.elastic.co/guide/en/cloud/current/ec-azure-snapshotting.html
# Reference 3 : https://opster.com/guides/elasticsearch/how-tos/elasticsearch-snapshot/
# Reference 4 : https://opster.com/guides/elasticsearch/glossary/elasticsearch-repositories/
# Reference 5 : https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshots-register-repository.html

# Remove all existing snapshots from this cluster.
rm -rf /PATH/TO/MOUNTED_EXISTING_SNAPSHOTS_DIRECTORY

# Delete existing Azure Blob container's repository.
curl -X DELETE "http://<HOST_ADDRESS>:9200/_snapshot/index_backup_repo?pretty"

# Create verified repository for Azure Blob container's, called `index_backup_repo`,
# to store snapshot backup of all indices.
curl -X PUT "http://<HOST_ADDRESS>:9200/_snapshot/index_backup_repo?verify=true&pretty" -H 'Content-Type: application/json' -d'
{
  "type": "azure",
  "indices": "ES_INDEX_NAME_1,ES_INDEX_NAME_2,ES_INDEX_NAME_3,ES_INDEX_NAME_4,ES_INDEX_NAME_5",
  "ignore_unavailable": true,
  "settings": {
    "client": "secondary",
    "container": "AZURE_CONTAINER_NAME",
    "base_path": "MOUNTED_EXISTING_SNAPSHOTS_DIRECTORY"

  }
}
'

# Start taking snapshot backup using `index_backup_repo` repository, using name `all_index_backup`.
# Reference : https://www.elastic.co/guide/en/elasticsearch/reference/current/create-snapshot-api.html
curl -X PUT "http://<HOST_ADDRESS>:9200/_snapshot/index_backup_repo/all_index_backup?wait_for_completion=true&pretty"


# Print list all repositories.
# curl -X GET "http://<HOST_ADDRESS>:9200/_snapshot/_all?pretty"

# Print status of all repositories.
# curl -X GET "http://<HOST_ADDRESS>:9200/_snapshot/_status?pretty"

# Restore snapshot backup.
# curl -X POST "http://<HOST_ADDRESS>:9200/_snapshot/index_backup_repo/all_index_backup/_restore?wait_for_completion=true&pretty"
