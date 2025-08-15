#!/usr/bin/env python3
"""
Test script for Kafka Kerberos Utility

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Unit tests for the Kafka Kerberos utility
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script tests the utility's configuration loading and validation
without requiring actual Kafka connectivity.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to the path to import the utility
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError


class TestKafkaKerberosUtility(unittest.TestCase):
    """Test cases for KafkaKerberosUtility class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.keytab_path = os.path.join(self.temp_dir, "test.keytab")
        self.config_path = os.path.join(self.temp_dir, "test_config.ini")
        
        # Create a dummy keytab file
        with open(self.keytab_path, 'w') as f:
            f.write("dummy keytab content")
        
        # Create a test config file
        config_content = f"""[kafka]
bootstrap_servers = localhost:9092
topic = test-topic
keytab_path = {self.keytab_path}
principal = test@EXAMPLE.COM
service_name = kafka
consumer_group_id = test-group
auto_offset_reset = earliest
max_poll_records = 500
session_timeout_ms = 30000
heartbeat_interval_ms = 3000
"""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_loading_from_file(self):
        """Test configuration loading from file."""
        with patch.dict(os.environ, {}, clear=True):
            utility = KafkaKerberosUtility(config_file=self.config_path)
            
            self.assertEqual(utility.config['bootstrap_servers'], 'localhost:9092')
            self.assertEqual(utility.config['topic'], 'test-topic')
            self.assertEqual(utility.config['keytab_path'], self.keytab_path)
            self.assertEqual(utility.config['principal'], 'test@EXAMPLE.COM')
            self.assertEqual(utility.config['service_name'], 'kafka')
            self.assertEqual(utility.config['consumer_group_id'], 'test-group')
    
    def test_config_loading_from_env(self):
        """Test configuration loading from environment variables."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'broker1:9092,broker2:9092',
            'KAFKA_TOPIC': 'env-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'env@EXAMPLE.COM',
            'KAFKA_SERVICE_NAME': 'env-kafka',
            'KAFKA_CONSUMER_GROUP_ID': 'env-group'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            utility = KafkaKerberosUtility()
            
            self.assertEqual(utility.config['bootstrap_servers'], 'broker1:9092,broker2:9092')
            self.assertEqual(utility.config['topic'], 'env-topic')
            self.assertEqual(utility.config['keytab_path'], self.keytab_path)
            self.assertEqual(utility.config['principal'], 'env@EXAMPLE.COM')
            self.assertEqual(utility.config['service_name'], 'env-kafka')
            self.assertEqual(utility.config['consumer_group_id'], 'env-group')
    
    def test_env_overrides_file(self):
        """Test that environment variables override config file values."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'env-broker:9092',
            'KAFKA_TOPIC': 'env-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'env@EXAMPLE.COM'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            utility = KafkaKerberosUtility(config_file=self.config_path)
            
            # Environment variables should override config file
            self.assertEqual(utility.config['bootstrap_servers'], 'env-broker:9092')
            self.assertEqual(utility.config['topic'], 'env-topic')
            self.assertEqual(utility.config['principal'], 'env@EXAMPLE.COM')
            
            # Values not in env should come from config file
            self.assertEqual(utility.config['service_name'], 'kafka')
            # Note: consumer_group_id has a default value in environment, so it won't be overridden
    
    def test_missing_required_params(self):
        """Test error handling for missing required parameters."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(KafkaKerberosError) as context:
                KafkaKerberosUtility()
            
            error_msg = str(context.exception)
            self.assertIn("Missing required configuration parameters", error_msg)
    
    def test_missing_keytab_file(self):
        """Test error handling for missing keytab file."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'localhost:9092',
            'KAFKA_TOPIC': 'test-topic',
            'KAFKA_KEYTAB_PATH': '/nonexistent/keytab',
            'KAFKA_PRINCIPAL': 'test@EXAMPLE.COM'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with self.assertRaises(KafkaKerberosError) as context:
                KafkaKerberosUtility()
            
            error_msg = str(context.exception)
            self.assertIn("Keytab file not found", error_msg)
    
    def test_empty_bootstrap_servers(self):
        """Test error handling for empty bootstrap servers."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': '',
            'KAFKA_TOPIC': 'test-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'test@EXAMPLE.COM'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with self.assertRaises(KafkaKerberosError) as context:
                KafkaKerberosUtility()
            
            error_msg = str(context.exception)
            self.assertIn("Missing required configuration parameters", error_msg)
    
    @patch('kafka_kerberos_utility.KafkaProducer')
    def test_producer_config(self, mock_producer_class):
        """Test producer configuration generation."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'broker1:9092,broker2:9092',
            'KAFKA_TOPIC': 'test-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'test@EXAMPLE.COM',
            'KAFKA_SERVICE_NAME': 'test-kafka'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            utility = KafkaKerberosUtility()
            producer_config = utility._get_producer_config()
            
            self.assertEqual(producer_config['bootstrap_servers'], ['broker1:9092', 'broker2:9092'])
            self.assertEqual(producer_config['security_protocol'], 'SASL_PLAINTEXT')
            self.assertEqual(producer_config['sasl_mechanism'], 'GSSAPI')
            self.assertEqual(producer_config['sasl_kerberos_service_name'], 'test-kafka')
            self.assertIn('value_serializer', producer_config)
            self.assertIn('key_serializer', producer_config)
    
    @patch('kafka_kerberos_utility.KafkaConsumer')
    def test_consumer_config(self, mock_consumer_class):
        """Test consumer configuration generation."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'broker1:9092,broker2:9092',
            'KAFKA_TOPIC': 'test-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'test@EXAMPLE.COM',
            'KAFKA_CONSUMER_GROUP_ID': 'test-group',
            'KAFKA_AUTO_OFFSET_RESET': 'latest',
            'KAFKA_MAX_POLL_RECORDS': '1000'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            utility = KafkaKerberosUtility()
            consumer_config = utility._get_consumer_config()
            
            self.assertEqual(consumer_config['bootstrap_servers'], ['broker1:9092', 'broker2:9092'])
            self.assertEqual(consumer_config['security_protocol'], 'SASL_PLAINTEXT')
            self.assertEqual(consumer_config['sasl_mechanism'], 'GSSAPI')
            self.assertEqual(consumer_config['group_id'], 'test-group')
            self.assertEqual(consumer_config['auto_offset_reset'], 'latest')
            self.assertEqual(consumer_config['max_poll_records'], 1000)
            self.assertIn('value_deserializer', consumer_config)
            self.assertIn('key_deserializer', consumer_config)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        env_vars = {
            'KAFKA_BOOTSTRAP_SERVERS': 'localhost:9092',
            'KAFKA_TOPIC': 'test-topic',
            'KAFKA_KEYTAB_PATH': self.keytab_path,
            'KAFKA_PRINCIPAL': 'test@EXAMPLE.COM'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with KafkaKerberosUtility() as utility:
                self.assertIsInstance(utility, KafkaKerberosUtility)
                # The close method should be called automatically


def run_tests():
    """Run all tests."""
    print("Running Kafka Kerberos Utility Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKafkaKerberosUtility)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
