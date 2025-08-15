#!/usr/bin/env python3
"""
Simple Kafka Utility without Kerberos Authentication

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Basic Kafka utility for testing without Kerberos authentication
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This module provides a basic Kafka utility for testing without Kerberos authentication.

This module provides a basic Kafka utility for testing without Kerberos authentication.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError


class SimpleKafkaError(Exception):
    """Custom exception for Simple Kafka utility errors."""
    pass


class SimpleKafkaUtility:
    """
    Simple Kafka utility class without Kerberos authentication.
    
    This class provides methods to produce and consume messages from Kafka
    using basic authentication (no Kerberos).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the simple Kafka utility.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Setup logging
        self._setup_logging()
        
        # Initialize producers and consumers cache
        self._producers: Dict[str, KafkaProducer] = {}
        self._consumers: Dict[str, KafkaConsumer] = {}
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('simple_kafka_utility.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_producer_config(self) -> Dict[str, Any]:
        """
        Get Kafka producer configuration.
        
        Returns:
            Dictionary containing producer configuration
        """
        return {
            'bootstrap_servers': self.config['bootstrap_servers'].split(','),
            'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
            'key_serializer': lambda k: k.encode('utf-8') if k else None,
            'acks': 'all',
            'retries': 3,
            'max_in_flight_requests_per_connection': 1,
        }
    
    def _get_consumer_config(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Kafka consumer configuration.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            Dictionary containing consumer configuration
        """
        return {
            'bootstrap_servers': self.config['bootstrap_servers'].split(','),
            'group_id': self.config['consumer_group_id'],
            'auto_offset_reset': self.config['auto_offset_reset'],
            'enable_auto_commit': True,
            'auto_commit_interval_ms': 1000,
            'max_poll_records': self.config['max_poll_records'],
            'session_timeout_ms': self.config['session_timeout_ms'],
            'heartbeat_interval_ms': self.config['heartbeat_interval_ms'],
            'value_deserializer': lambda v: json.loads(v.decode('utf-8')) if v else None,
            'key_deserializer': lambda k: k.decode('utf-8') if k else None,
        }
    
    def get_producer(self, topic: Optional[str] = None) -> KafkaProducer:
        """
        Get or create a Kafka producer for the specified topic.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            KafkaProducer instance
            
        Raises:
            SimpleKafkaError: If producer creation fails
        """
        topic = topic or self.config['topic']
        
        if topic not in self._producers:
            try:
                producer_config = self._get_producer_config()
                self._producers[topic] = KafkaProducer(**producer_config)
                self.logger.info(f"Created producer for topic: {topic}")
            except Exception as e:
                raise SimpleKafkaError(f"Failed to create producer for topic {topic}: {str(e)}")
        
        return self._producers[topic]
    
    def get_consumer(self, topic: Optional[str] = None) -> KafkaConsumer:
        """
        Get or create a Kafka consumer for the specified topic.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            KafkaConsumer instance
            
        Raises:
            SimpleKafkaError: If consumer creation fails
        """
        topic = topic or self.config['topic']
        
        if topic not in self._consumers:
            try:
                consumer_config = self._get_consumer_config(topic)
                consumer = KafkaConsumer(topic, **consumer_config)
                self._consumers[topic] = consumer
                self.logger.info(f"Created consumer for topic: {topic}")
            except Exception as e:
                raise SimpleKafkaError(f"Failed to create consumer for topic {topic}: {str(e)}")
        
        return self._consumers[topic]
    
    def produce_message(self, message: Any, key: Optional[str] = None, 
                       topic: Optional[str] = None) -> bool:
        """
        Produce a message to Kafka.
        
        Args:
            message: Message to produce (will be JSON serialized)
            key: Optional message key
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            True if message was sent successfully, False otherwise
            
        Raises:
            SimpleKafkaError: If message production fails
        """
        topic = topic or self.config['topic']
        
        try:
            producer = self.get_producer(topic)
            
            future = producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            
            self.logger.info(
                f"Message sent successfully to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} offset {record_metadata.offset}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to produce message to topic {topic}: {str(e)}")
            raise SimpleKafkaError(f"Message production failed: {str(e)}")
    
    def consume_messages(self, topic: Optional[str] = None, 
                        message_handler: Optional[Callable] = None,
                        max_messages: Optional[int] = None,
                        timeout_ms: int = 1000) -> List[Any]:
        """
        Consume messages from Kafka.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            message_handler: Optional callback function to process each message
            max_messages: Optional maximum number of messages to consume
            timeout_ms: Timeout for polling messages in milliseconds
            
        Returns:
            List of consumed messages
            
        Raises:
            SimpleKafkaError: If message consumption fails
        """
        topic = topic or self.config['topic']
        messages = []
        
        try:
            consumer = self.get_consumer(topic)
            
            message_count = 0
            while True:
                if max_messages and message_count >= max_messages:
                    break
                
                message_batch = consumer.poll(timeout_ms=timeout_ms)
                
                for tp, records in message_batch.items():
                    for record in records:
                        message = record.value
                        messages.append(message)
                        message_count += 1
                        
                        self.logger.info(
                            f"Received message from topic {record.topic} "
                            f"partition {record.partition} offset {record.offset}: {message}"
                        )
                        
                        if message_handler:
                            try:
                                message_handler(message, record)
                            except Exception as e:
                                self.logger.error(f"Message handler error: {str(e)}")
                        
                        if max_messages and message_count >= max_messages:
                            break
                
                if not message_batch:
                    break
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to consume messages from topic {topic}: {str(e)}")
            raise SimpleKafkaError(f"Message consumption failed: {str(e)}")
    
    def close(self):
        """Close all producers and consumers."""
        try:
            # Close producers
            for topic, producer in self._producers.items():
                producer.close()
                self.logger.info(f"Closed producer for topic: {topic}")
            
            # Close consumers
            for topic, consumer in self._consumers.items():
                consumer.close()
                self.logger.info(f"Closed consumer for topic: {topic}")
            
            self._producers.clear()
            self._consumers.clear()
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
