from aiokafka import AIOKafkaProducer, AIOKafkaConsumer # type: ignore

import os
from confluent_kafka import avro, SerializingProducer # type: ignore
from confluent_kafka.serialization import StringSerializer # type: ignore
from google.protobuf.json_format import MessageToDict # type: ignore
import requests # type: ignore


# Schema Registry config
SCHEMA_REGISTRY_URL = "http://localhost:8081"
KAFKA_BROKER_URL = "localhost:19092"
TOPIC_NAME = "userService"

def register_schema(schema_name, schema_str):
  headers = {'Content-Type': 'application/vnd.schemaregistry.v1+json'}
  data = {"schema": schema_str}
  response = requests.post(
      f"{SCHEMA_REGISTRY_URL}/subjects/{schema_name}/versions",
      headers=headers, json=data
  )
  response.raise_for_status()
  return response.json()

async def produce_message():
  producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
  await producer.start()
  try:
    # Produce message
    yield producer
  finally:
    # Wait for all pending messages to be delivered or expire.
    await producer.stop()


async def consume_messages(topic, bootstrap_servers):
  # Create a consumer instance.
  consumer = AIOKafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    group_id="user-service-consumer-group",
    auto_offset_reset='earliest'
  )

  # Start the consumer.
  await consumer.start()
  try:
    # Continuously listen for messages.
    async for message in consumer:
      print(f"Received message: {message.value.decode()} on topic {message.topic}")
      # Here you can add code to process each message.
      # Example: parse the message, store it in a database, etc.
  finally:
    # Ensure to close the consumer when done.
    await consumer.stop()

