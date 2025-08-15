#!/usr/bin/env python3
"""
End-to-end test for Kafka message production and consumption

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: End-to-end testing for Kafka utility with Kerberos
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script tests the complete flow of producing and consuming messages
using the Kafka utility with both simple and Kerberos configurations.
"""

import time
import json
from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError
from simple_kafka_utility import SimpleKafkaUtility, SimpleKafkaError


def test_simple_kafka():
    """Test Kafka without Kerberos authentication."""
    print("🧪 Testing Simple Kafka (No Kerberos)")
    print("=" * 50)
    
    try:
        # Create a simple configuration without Kerberos
        config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test-topic',
            'consumer_group_id': 'kafka-test-group',
            'auto_offset_reset': 'earliest',
            'max_poll_records': 500,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 3000,
        }
        
        # Test the utility
        with SimpleKafkaUtility(config) as kafka:
            
            # Produce test messages
            print("📤 Producing test messages...")
            test_messages = [
                {"id": 1, "message": "Hello Kafka!", "timestamp": time.time()},
                {"id": 2, "message": "Testing message production", "timestamp": time.time()},
                {"id": 3, "message": "End-to-end test", "timestamp": time.time()},
            ]
            
            for i, message in enumerate(test_messages):
                success = kafka.produce_message(message, key=f"test_key_{i}")
                if success:
                    print(f"✅ Message {i+1} produced successfully")
                else:
                    print(f"❌ Failed to produce message {i+1}")
            
            # Wait a moment for messages to be available
            print("\n⏳ Waiting for messages to be available...")
            time.sleep(2)
            
            # Consume messages
            print("📥 Consuming messages...")
            messages = kafka.consume_messages(max_messages=5, timeout_ms=10000)
            
            print(f"✅ Consumed {len(messages)} messages:")
            for i, msg in enumerate(messages):
                print(f"   Message {i+1}: {msg}")
            
            return len(messages) > 0
            
    except SimpleKafkaError as e:
        print(f"❌ Simple Kafka Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in simple Kafka test: {e}")
        return False


def test_kerberos_kafka():
    """Test Kafka with Kerberos authentication."""
    print("\n🔐 Testing Kafka with Kerberos")
    print("=" * 50)
    
    try:
        # Use the Kerberos configuration
        with KafkaKerberosUtility(config_file="test_kafka_config.ini") as kafka:
            # Produce test messages
            print("📤 Producing test messages with Kerberos...")
            test_messages = [
                {"id": 1, "message": "Hello Kafka with Kerberos!", "timestamp": time.time()},
                {"id": 2, "message": "Testing Kerberos authentication", "timestamp": time.time()},
                {"id": 3, "message": "Secure end-to-end test", "timestamp": time.time()},
            ]
            
            for i, message in enumerate(test_messages):
                try:
                    success = kafka.produce_message(message, key=f"kerberos_key_{i}")
                    if success:
                        print(f"✅ Message {i+1} produced successfully with Kerberos")
                    else:
                        print(f"❌ Failed to produce message {i+1} with Kerberos")
                except Exception as e:
                    print(f"⚠️  Kerberos production failed (expected if Kafka doesn't support Kerberos): {e}")
                    return False
            
            # Wait a moment for messages to be available
            print("\n⏳ Waiting for messages to be available...")
            time.sleep(2)
            
            # Consume messages
            print("📥 Consuming messages with Kerberos...")
            try:
                messages = kafka.consume_messages(max_messages=5, timeout_ms=10000)
                print(f"✅ Consumed {len(messages)} messages with Kerberos:")
                for i, msg in enumerate(messages):
                    print(f"   Message {i+1}: {msg}")
                return len(messages) > 0
            except Exception as e:
                print(f"⚠️  Kerberos consumption failed (expected if Kafka doesn't support Kerberos): {e}")
                return False
            
    except Exception as e:
        print(f"❌ Error in Kerberos Kafka test: {e}")
        return False


def main():
    """Run all end-to-end tests."""
    print("🚀 Kafka End-to-End Testing")
    print("=" * 60)
    
    # Test simple Kafka first
    simple_success = test_simple_kafka()
    
    # Test Kerberos Kafka
    kerberos_success = test_kerberos_kafka()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Simple Kafka (No Kerberos): {'✅ PASSED' if simple_success else '❌ FAILED'}")
    print(f"Kafka with Kerberos: {'✅ PASSED' if kerberos_success else '❌ FAILED'}")
    
    if simple_success:
        print("\n🎉 Basic Kafka functionality is working!")
        print("   You can now use the Kafka utility for message production and consumption.")
    
    if kerberos_success:
        print("\n🔐 Kerberos authentication is working!")
        print("   Your Kafka utility supports secure Kerberos authentication.")
    
    if not simple_success and not kerberos_success:
        print("\n❌ Both tests failed.")
        print("   Please check your Kafka setup and try again.")


if __name__ == "__main__":
    main()
