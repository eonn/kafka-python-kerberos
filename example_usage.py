#!/usr/bin/env python3
"""
Example usage of the Kafka Kerberos Utility

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Example usage patterns for the Kafka Kerberos utility
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script demonstrates various usage patterns of the Kafka utility.

This script demonstrates various usage patterns including:
- Basic message production and consumption
- Using custom message handlers
- Error handling
- Configuration from different sources
- Context manager usage
"""

import json
import time
from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError


def message_handler(message, record):
    """
    Custom message handler for processing consumed messages.
    
    Args:
        message: The deserialized message content
        record: The Kafka record object containing metadata
    """
    print(f"Processing message: {message}")
    print(f"  Topic: {record.topic}")
    print(f"  Partition: {record.partition}")
    print(f"  Offset: {record.offset}")
    print(f"  Key: {record.key}")
    print("---")


def example_basic_usage():
    """Example of basic message production and consumption."""
    print("=== Basic Usage Example ===")
    
    try:
        # Initialize the utility
        kafka_util = KafkaKerberosUtility()
        
        # Produce a simple message
        message = {
            "user_id": 12345,
            "action": "login",
            "timestamp": time.time(),
            "ip_address": "192.168.1.100"
        }
        
        success = kafka_util.produce_message(message, key="user_12345")
        print(f"Message production: {'Success' if success else 'Failed'}")
        
        # Consume messages
        messages = kafka_util.consume_messages(max_messages=1, timeout_ms=5000)
        print(f"Consumed {len(messages)} messages")
        
        # Clean up
        kafka_util.close()
        
    except KafkaKerberosError as e:
        print(f"Kafka error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_context_manager():
    """Example using the context manager for automatic cleanup."""
    print("\n=== Context Manager Example ===")
    
    try:
        with KafkaKerberosUtility() as kafka:
            # Produce multiple messages
            for i in range(3):
                message = {
                    "batch_id": i,
                    "data": f"test_message_{i}",
                    "timestamp": time.time()
                }
                kafka.produce_message(message, key=f"batch_{i}")
                print(f"Produced message {i}")
            
            # Consume messages with custom handler
            messages = kafka.consume_messages(
                max_messages=3,
                message_handler=message_handler,
                timeout_ms=5000
            )
            print(f"Total messages consumed: {len(messages)}")
            
    except KafkaKerberosError as e:
        print(f"Kafka error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_config_file_usage():
    """Example using configuration from a file."""
    print("\n=== Config File Example ===")
    
    try:
        # Initialize with config file
        kafka_util = KafkaKerberosUtility(config_file="kafka_config.ini")
        
        # Produce a message
        message = {
            "source": "config_file_example",
            "message": "Hello from config file!",
            "timestamp": time.time()
        }
        
        success = kafka_util.produce_message(message, key="config_test")
        print(f"Message production: {'Success' if success else 'Failed'}")
        
        # Clean up
        kafka_util.close()
        
    except KafkaKerberosError as e:
        print(f"Kafka error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_error_handling():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    try:
        # This will fail if configuration is not set up properly
        kafka_util = KafkaKerberosUtility()
        
        # Try to produce to a non-existent topic (if different from default)
        try:
            kafka_util.produce_message({"test": "message"}, topic="non-existent-topic")
        except KafkaKerberosError as e:
            print(f"Expected error when producing to non-existent topic: {e}")
        
        kafka_util.close()
        
    except KafkaKerberosError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_advanced_usage():
    """Example of advanced usage patterns."""
    print("\n=== Advanced Usage Example ===")
    
    try:
        with KafkaKerberosUtility() as kafka:
            # Get producer and consumer instances directly
            producer = kafka.get_producer()
            consumer = kafka.get_consumer()
            
            # Produce messages using the producer directly
            for i in range(2):
                future = producer.send(
                    kafka.config['topic'],
                    value={"direct_producer": f"message_{i}"},
                    key=f"direct_{i}"
                )
                record_metadata = future.get(timeout=10)
                print(f"Direct producer message sent to {record_metadata.topic} "
                      f"partition {record_metadata.partition} offset {record_metadata.offset}")
            
            # Consume messages using the consumer directly
            message_count = 0
            for message in consumer:
                print(f"Direct consumer received: {message.value}")
                message_count += 1
                if message_count >= 2:
                    break
            
    except KafkaKerberosError as e:
        print(f"Kafka error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    """Run all examples."""
    print("Kafka Kerberos Utility Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_context_manager()
    example_config_file_usage()
    example_error_handling()
    example_advanced_usage()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
