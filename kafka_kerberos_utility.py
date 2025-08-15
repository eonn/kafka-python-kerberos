#!/usr/bin/env python3
"""
Kafka Utility with Kerberos Authentication

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Comprehensive Kafka utility with Kerberos (GSSAPI) authentication support
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This module provides a comprehensive Kafka utility that supports:

This module provides a comprehensive Kafka utility that supports:
- Connection to configurable Kafka brokers
- Message production and consumption
- Kerberos (GSSAPI) authentication via keytab files
- Configuration via environment variables or config files
- Comprehensive error handling

Required Environment Variables:
- KAFKA_BOOTSTRAP_SERVERS: Comma-separated list of Kafka brokers (e.g., "broker1:9092,broker2:9092")
- KAFKA_TOPIC: Default topic for operations
- KAFKA_KEYTAB_PATH: Path to the Kerberos keytab file
- KAFKA_PRINCIPAL: Kerberos principal (e.g., "user@REALM")
- KAFKA_SERVICE_NAME: Kerberos service name (default: "kafka")
- KAFKA_JAAS_CONFIG_PATH: Path to JAAS configuration file (optional)

Optional Environment Variables:
- KAFKA_CONSUMER_GROUP_ID: Consumer group ID (default: "kafka-utility-group")
- KAFKA_AUTO_OFFSET_RESET: Auto offset reset policy (default: "earliest")
- KAFKA_MAX_POLL_RECORDS: Maximum records per poll (default: 500)
- KAFKA_SESSION_TIMEOUT_MS: Session timeout in milliseconds (default: 30000)
- KAFKA_HEARTBEAT_INTERVAL_MS: Heartbeat interval in milliseconds (default: 3000)
"""

import os
import sys
import json
import logging
import configparser
from typing import Dict, List, Optional, Any, Callable
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv():
        pass
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, SaslAuthenticationFailedError, KafkaConnectionError
try:
    import gssapi
    GSSAPI_AVAILABLE = True
except ImportError:
    GSSAPI_AVAILABLE = False
    gssapi = None


class KafkaKerberosError(Exception):
    """Custom exception for Kafka Kerberos authentication errors."""
    pass


class KafkaKerberosUtility:
    """
    Kafka utility class with Kerberos authentication support.
    
    This class provides methods to produce and consume messages from Kafka
    using Kerberos (GSSAPI) authentication via keytab files.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Kafka utility with Kerberos authentication.
        
        Args:
            config_file: Optional path to configuration file
        """
        # Load environment variables
        if DOTENV_AVAILABLE:
            load_dotenv()
        else:
            self.logger.warning("python-dotenv not available. Environment variables must be set manually.")
        
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize producers and consumers cache
        self._producers: Dict[str, KafkaProducer] = {}
        self._consumers: Dict[str, KafkaConsumer] = {}
        
        # Validate configuration
        self._validate_config()
        
        # Setup Kerberos authentication
        self._setup_kerberos()
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables and optional config file.
        
        Args:
            config_file: Optional path to configuration file
            
        Returns:
            Dictionary containing configuration parameters
        """
        config = {}
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'kafka' in parser:
                config.update(parser['kafka'])
        
        # Environment variables take precedence over config file
        env_config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            'topic': os.getenv('KAFKA_TOPIC'),
            'keytab_path': os.getenv('KAFKA_KEYTAB_PATH'),
            'principal': os.getenv('KAFKA_PRINCIPAL'),
            'service_name': os.getenv('KAFKA_SERVICE_NAME'),
            'jaas_config_path': os.getenv('KAFKA_JAAS_CONFIG_PATH'),
            'consumer_group_id': os.getenv('KAFKA_CONSUMER_GROUP_ID'),
            'auto_offset_reset': os.getenv('KAFKA_AUTO_OFFSET_RESET'),
            'max_poll_records': os.getenv('KAFKA_MAX_POLL_RECORDS'),
            'session_timeout_ms': os.getenv('KAFKA_SESSION_TIMEOUT_MS'),
            'heartbeat_interval_ms': os.getenv('KAFKA_HEARTBEAT_INTERVAL_MS'),
        }
        
        # Only update with non-None environment values
        for key, value in env_config.items():
            if value is not None:
                config[key] = value
        
        # Set defaults for missing values
        config.setdefault('service_name', 'kafka')
        config.setdefault('consumer_group_id', 'kafka-utility-group')
        config.setdefault('auto_offset_reset', 'earliest')
        config.setdefault('max_poll_records', '500')
        config.setdefault('session_timeout_ms', '30000')
        config.setdefault('heartbeat_interval_ms', '3000')
        
        # Convert numeric values
        if 'max_poll_records' in config:
            config['max_poll_records'] = int(config['max_poll_records'])
        if 'session_timeout_ms' in config:
            config['session_timeout_ms'] = int(config['session_timeout_ms'])
        if 'heartbeat_interval_ms' in config:
            config['heartbeat_interval_ms'] = int(config['heartbeat_interval_ms'])
        
        return config
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('kafka_kerberos_utility.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _validate_config(self):
        """Validate required configuration parameters."""
        required_params = ['bootstrap_servers', 'topic', 'keytab_path', 'principal']
        missing_params = [param for param in required_params if not self.config.get(param)]
        
        if missing_params:
            raise KafkaKerberosError(
                f"Missing required configuration parameters: {', '.join(missing_params)}. "
                "Please set the corresponding environment variables or provide them in the config file."
            )
        
        # Validate keytab file exists
        if not os.path.exists(self.config['keytab_path']):
            raise KafkaKerberosError(
                f"Keytab file not found: {self.config['keytab_path']}"
            )
        
        # Validate bootstrap servers format
        if not self.config['bootstrap_servers']:
            raise KafkaKerberosError("Bootstrap servers cannot be empty")
    
    def _setup_kerberos(self):
        """Setup Kerberos authentication environment."""
        try:
            # Check if GSSAPI is available
            if not GSSAPI_AVAILABLE:
                self.logger.warning(
                    "GSSAPI module not available. Kerberos authentication may not work properly. "
                    "Install gssapi with: pip install gssapi (requires system dependencies)"
                )
            
            # Set Kerberos environment variables
            os.environ['KRB5_CONFIG'] = '/etc/krb5.conf'  # Default Kerberos config
            os.environ['KRB5CCNAME'] = f'FILE:/tmp/krb5cc_{os.getuid()}'
            
            # Create JAAS configuration if not provided
            if not self.config.get('jaas_config_path'):
                self._create_jaas_config()
            else:
                os.environ['JAVA_OPTS'] = f'-Djava.security.auth.login.config={self.config["jaas_config_path"]}'
            
            self.logger.info("Kerberos authentication environment configured successfully")
            
        except Exception as e:
            raise KafkaKerberosError(f"Failed to setup Kerberos authentication: {str(e)}")
    
    def _create_jaas_config(self):
        """Create JAAS configuration file for Kerberos authentication."""
        jaas_config_content = f"""
KafkaClient {{
    com.sun.security.auth.module.Krb5LoginModule required
    useKeyTab=true
    storeKey=true
    keyTab="{self.config['keytab_path']}"
    principal="{self.config['principal']}";
}};
"""
        
        jaas_config_path = '/tmp/kafka_jaas.conf'
        try:
            with open(jaas_config_path, 'w') as f:
                f.write(jaas_config_content)
            
            os.environ['JAVA_OPTS'] = f'-Djava.security.auth.login.config={jaas_config_path}'
            self.config['jaas_config_path'] = jaas_config_path
            
            self.logger.info(f"Created JAAS configuration at: {jaas_config_path}")
            
        except Exception as e:
            raise KafkaKerberosError(f"Failed to create JAAS configuration: {str(e)}")
    
    def _get_producer_config(self) -> Dict[str, Any]:
        """
        Get Kafka producer configuration with Kerberos authentication.
        
        Returns:
            Dictionary containing producer configuration
        """
        return {
            'bootstrap_servers': self.config['bootstrap_servers'].split(','),
            'security_protocol': 'SASL_PLAINTEXT',
            'sasl_mechanism': 'GSSAPI',
            'sasl_kerberos_service_name': self.config['service_name'],
            'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
            'key_serializer': lambda k: k.encode('utf-8') if k else None,
            'acks': 'all',
            'retries': 3,
            'max_in_flight_requests_per_connection': 1,
        }
    
    def _get_consumer_config(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Kafka consumer configuration with Kerberos authentication.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            Dictionary containing consumer configuration
        """
        return {
            'bootstrap_servers': self.config['bootstrap_servers'].split(','),
            'security_protocol': 'SASL_PLAINTEXT',
            'sasl_mechanism': 'GSSAPI',
            'sasl_kerberos_service_name': self.config['service_name'],
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
            KafkaKerberosError: If producer creation fails
        """
        topic = topic or self.config['topic']
        
        if topic not in self._producers:
            try:
                producer_config = self._get_producer_config()
                self._producers[topic] = KafkaProducer(**producer_config)
                self.logger.info(f"Created producer for topic: {topic}")
            except Exception as e:
                raise KafkaKerberosError(f"Failed to create producer for topic {topic}: {str(e)}")
        
        return self._producers[topic]
    
    def get_consumer(self, topic: Optional[str] = None) -> KafkaConsumer:
        """
        Get or create a Kafka consumer for the specified topic.
        
        Args:
            topic: Optional topic name (uses default if not provided)
            
        Returns:
            KafkaConsumer instance
            
        Raises:
            KafkaKerberosError: If consumer creation fails
        """
        topic = topic or self.config['topic']
        
        if topic not in self._consumers:
            try:
                consumer_config = self._get_consumer_config(topic)
                consumer = KafkaConsumer(topic, **consumer_config)
                self._consumers[topic] = consumer
                self.logger.info(f"Created consumer for topic: {topic}")
            except Exception as e:
                raise KafkaKerberosError(f"Failed to create consumer for topic {topic}: {str(e)}")
        
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
            KafkaKerberosError: If message production fails
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
            raise KafkaKerberosError(f"Message production failed: {str(e)}")
    
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
            KafkaKerberosError: If message consumption fails
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
            raise KafkaKerberosError(f"Message consumption failed: {str(e)}")
    
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


def main():
    """Example usage of the Kafka Kerberos Utility."""
    try:
        # Initialize the utility
        kafka_util = KafkaKerberosUtility()
        
        # Example: Produce a message
        message = {"user_id": 123, "action": "login", "timestamp": "2024-01-01T12:00:00Z"}
        success = kafka_util.produce_message(message, key="user_123")
        print(f"Message production: {'Success' if success else 'Failed'}")
        
        # Example: Consume messages
        messages = kafka_util.consume_messages(max_messages=5, timeout_ms=5000)
        print(f"Consumed {len(messages)} messages")
        
        # Example: Use with context manager
        with KafkaKerberosUtility() as kafka:
            kafka.produce_message({"test": "message"}, key="test_key")
            consumed = kafka.consume_messages(max_messages=1)
            print(f"Consumed message: {consumed}")
    
    except KafkaKerberosError as e:
        print(f"Kafka Kerberos Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
