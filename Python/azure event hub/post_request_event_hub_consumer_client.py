# Helper script that can listen to the POST request events submitted to the Azure Event Hub and update the required Elasticsearch backend data by extracting values contained in the event itself.

# This should be executed as root user otherwise can't be able to read files path due to permission issues.

# Reference 1 : https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-python-get-started-send
# Reference 2 : https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py

import asyncio
import json
import requests
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

EVENTHUB_CONNECTION_STR: str = "EVENTHUB_CONNECTION_ENDPOINT_URL"
CONSUMER_GROUP: str = (
    "$Default"  # TODO: Change this if set to some other consumer group name.
)
EVENTHUB_NAME: str = "AZURE_EVENTHUB_NAME"
BLOB_STORAGE_CONNECTION_STR: str = "BLOB_STORAGE_CONNECTION_STRING_TO"
BLOB_CONTAINER_NAME: str = "CONTAINER_NAME_IN_BLOB_STORAGE"
ES_INDEX_NAME: str = "ELASTICSEARCH_INDEX_NAME"


async def on_event(partition_context, event):
    event_body_str: str = event.body_as_str("UTF-8")
    print(f"event_body_str ({type(event_body_str)}) => {event_body_str}")
    event_body_dict: dict = json.loads(event_body_str)
    print(f"event_body_dict ({type(event_body_dict)}) => {event_body_dict}")

    print("Received event from partition: {}.".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)

    # URL for updating the document using document ID.
    unique_id_str: str = event_body_dict["UNIQUE_ID_COLUMN"]
    url_str: str = f"http://ELASTICSEARCH_HOST_IP_ADDRESS:9200/{ES_INDEX_NAME}/_update/{unique_id_str}"

    # Data structure required by Elasticsearch index for columns values to update.
    data_dict: dict = {
        "doc": {},
    }

    # Fill in the columns to be updated with values in `data_dict`.
    for key, value in event_body_dict.items():
        column_name_str: str = key

        # Skip processing "UNIQUE_ID" column since it never get updated.
        if column_name_str == "UNIQUE_ID_COLUMN":
            continue

        # Depending on name of column, perform type-casting to match the data-type configured in Elasticsearch index.
        if column_name_str == "NUMERIC_FLOAT_COLUMN_1":
            # Type cast value to `float`.
            data_dict["doc"][column_name_str] = float(value)
        elif column_name_str == "NUMERIC_INT_COLUMN_2":
            # Type cast value to `int`.
            data_dict["doc"][column_name_str] = int(float(value))
        else:
            # Keep non-numeric types as it is.
            data_dict["doc"][column_name_str] = value

    # Send POST request to update document using `url_str` endpoint.
    response_obj = requests.post(
        url=url_str,
        json=data_dict,
    )
    print(f"- POST response : \n{response_obj.text}")
    print("-" * 100)


async def receive(client):
    """
    Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
    a checkpoint store, the client will load-balance partition assignment with other EventHubConsumerClient instances
    which also try to receive events from all partitions and use the same storage resource.
    """
    await client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )


async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        BLOB_STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME
    )
    client = EventHubConsumerClient.from_connection_string(
        EVENTHUB_CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing.
    )
    async with client:
        await receive(client)


if __name__ == "__main__":
    asyncio.run(main())
