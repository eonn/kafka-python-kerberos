#!/usr/bin/env python3
"""
Test script to verify Kafka utility with local Kerberos setup

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Kerberos setup verification for Kafka utility
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script tests the Kafka utility configuration and Kerberos authentication
without requiring an actual Kafka broker.
"""

import os
import sys
from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError


def test_kerberos_configuration():
    """Test the Kafka utility configuration with local Kerberos setup."""
    print("🧪 Testing Kafka Utility with Local Kerberos Setup")
    print("=" * 60)
    
    try:
        # Test configuration loading
        print("1. Testing configuration loading...")
        kafka_util = KafkaKerberosUtility(config_file="test_kafka_config.ini")
        
        print("✅ Configuration loaded successfully")
        print(f"   Bootstrap servers: {kafka_util.config['bootstrap_servers']}")
        print(f"   Topic: {kafka_util.config['topic']}")
        print(f"   Principal: {kafka_util.config['principal']}")
        print(f"   Keytab path: {kafka_util.config['keytab_path']}")
        print(f"   Service name: {kafka_util.config['service_name']}")
        
        # Test producer configuration
        print("\n2. Testing producer configuration...")
        producer_config = kafka_util._get_producer_config()
        print("✅ Producer configuration generated successfully")
        print(f"   Security protocol: {producer_config['security_protocol']}")
        print(f"   SASL mechanism: {producer_config['sasl_mechanism']}")
        print(f"   Service name: {producer_config['sasl_kerberos_service_name']}")
        
        # Test consumer configuration
        print("\n3. Testing consumer configuration...")
        consumer_config = kafka_util._get_consumer_config()
        print("✅ Consumer configuration generated successfully")
        print(f"   Security protocol: {consumer_config['security_protocol']}")
        print(f"   SASL mechanism: {consumer_config['sasl_mechanism']}")
        print(f"   Service name: {consumer_config['sasl_kerberos_service_name']}")
        print(f"   Group ID: {consumer_config['group_id']}")
        
        # Test context manager
        print("\n4. Testing context manager...")
        with KafkaKerberosUtility(config_file="test_kafka_config.ini") as kafka:
            print("✅ Context manager works correctly")
            print(f"   Configuration loaded: {len(kafka.config) > 0}")
        
        print("\n🎉 All tests passed! Kerberos setup is working correctly.")
        print("\n📋 Next steps:")
        print("1. Set up a Kafka broker (e.g., using Docker)")
        print("2. Configure the broker for Kerberos authentication")
        print("3. Test actual message production and consumption")
        
        return True
        
    except KafkaKerberosError as e:
        print(f"❌ Kafka Kerberos Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_kerberos_ticket():
    """Test if Kerberos ticket is available."""
    print("\n🔐 Testing Kerberos Ticket")
    print("-" * 30)
    
    try:
        # Check if klist command is available
        import subprocess
        result = subprocess.run(['klist'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Kerberos ticket is available:")
            print(result.stdout)
        else:
            print("⚠️  No Kerberos ticket found")
            print("   Run: kinit -kt test-user.keytab test-user")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking Kerberos ticket: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Kafka Kerberos Setup Verification")
    print("=" * 60)
    
    # Test Kerberos ticket first
    ticket_ok = test_kerberos_ticket()
    
    if not ticket_ok:
        print("\n⚠️  Please obtain a Kerberos ticket first:")
        print("   kinit -kt test-user.keytab test-user")
        return
    
    # Test Kafka utility configuration
    config_ok = test_kerberos_configuration()
    
    if config_ok:
        print("\n✅ Kerberos setup is complete and working!")
        print("   You can now use the Kafka utility with Kerberos authentication.")
    else:
        print("\n❌ There were issues with the Kerberos setup.")
        print("   Please check the configuration and try again.")


if __name__ == "__main__":
    main()
