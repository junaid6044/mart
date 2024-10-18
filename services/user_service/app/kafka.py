from aiokafka import AIOKafkaProducer, AIOKafkaConsumer # type: ignore

async def get_kafka_producer():
  producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
  await producer.start()
  try:
    yield producer
  finally:
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

