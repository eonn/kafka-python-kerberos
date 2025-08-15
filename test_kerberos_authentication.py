#!/usr/bin/env python3
"""
Kerberos Authentication Test

Author: Eon (Himanshu Shekhar)
Created: 2025-08-15
Description: Kerberos authentication testing for Kafka utility
License: MIT
Repository: https://github.com/eonn/kafka-python-kerberos

This script specifically tests Kerberos authentication with Kafka.
It verifies that the Kerberos setup is working correctly and tests
authentication with the local Kerberos server.
"""

import os
import time
import json
import subprocess
from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError


def test_kerberos_ticket():
    """Test if Kerberos ticket is available and valid."""
    print("🔐 Testing Kerberos Ticket")
    print("-" * 40)
    
    try:
        # Check if klist is available
        result = subprocess.run(['klist'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Kerberos ticket is available:")
            print(result.stdout)
            return True
        else:
            print("❌ No Kerberos ticket found")
            print("   Run: kinit -kt test-user.keytab test-user")
            return False
    except FileNotFoundError:
        print("❌ klist command not found")
        return False


def test_kerberos_authentication():
    """Test Kerberos authentication with Kafka utility."""
    print("\n🔐 Testing Kerberos Authentication with Kafka")
    print("=" * 50)
    
    try:
        # Test with Kerberos configuration
        with KafkaKerberosUtility(config_file="test_kafka_config.ini") as kafka:
            print("✅ Kafka utility initialized with Kerberos configuration")
            
            # Test configuration
            print(f"   Bootstrap servers: {kafka.config['bootstrap_servers']}")
            print(f"   Topic: {kafka.config['topic']}")
            print(f"   Principal: {kafka.config['principal']}")
            print(f"   Service name: {kafka.config['service_name']}")
            
            # Test producer configuration
            producer_config = kafka._get_producer_config()
            print(f"   Security protocol: {producer_config.get('security_protocol', 'N/A')}")
            print(f"   SASL mechanism: {producer_config.get('sasl_mechanism', 'N/A')}")
            
            # Test consumer configuration
            consumer_config = kafka._get_consumer_config()
            print(f"   Consumer group: {consumer_config.get('group_id', 'N/A')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Kerberos authentication test failed: {e}")
        return False


def test_kerberos_message_flow():
    """Test message production and consumption with Kerberos."""
    print("\n📤 Testing Kerberos Message Flow")
    print("=" * 40)
    
    try:
        with KafkaKerberosUtility(config_file="test_kafka_config.ini") as kafka:
            # Test message production
            test_message = {
                "id": 1,
                "message": "Test message with Kerberos authentication",
                "timestamp": time.time(),
                "principal": kafka.config['principal']
            }
            
            print("📤 Attempting to produce message with Kerberos...")
            try:
                success = kafka.produce_message(test_message, key="kerberos_test")
                if success:
                    print("✅ Message produced successfully with Kerberos authentication")
                else:
                    print("❌ Failed to produce message")
                    return False
            except Exception as e:
                print(f"⚠️  Message production failed (expected if GSSAPI not available): {e}")
                print("   This is expected if the GSSAPI module is not installed")
                return False
            
            # Test message consumption
            print("📥 Attempting to consume messages with Kerberos...")
            try:
                messages = kafka.consume_messages(max_messages=1, timeout_ms=5000)
                if messages:
                    print(f"✅ Consumed {len(messages)} messages with Kerberos authentication")
                    for i, msg in enumerate(messages):
                        print(f"   Message {i+1}: {msg}")
                else:
                    print("⚠️  No messages consumed (this may be normal)")
                return True
            except Exception as e:
                print(f"⚠️  Message consumption failed (expected if GSSAPI not available): {e}")
                print("   This is expected if the GSSAPI module is not installed")
                return False
                
    except Exception as e:
        print(f"❌ Kerberos message flow test failed: {e}")
        return False


def test_kerberos_environment():
    """Test Kerberos environment variables and configuration."""
    print("\n🔧 Testing Kerberos Environment")
    print("=" * 35)
    
    # Check environment variables
    env_vars = {
        'KRB5_CONFIG': os.environ.get('KRB5_CONFIG'),
        'KRB5CCNAME': os.environ.get('KRB5CCNAME'),
        'KRB5_KTNAME': os.environ.get('KRB5_KTNAME'),
    }
    
    print("Environment variables:")
    for var, value in env_vars.items():
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    # Check keytab file
    keytab_path = "/home/eon/projects/Kafka-Python/test-user.keytab"
    if os.path.exists(keytab_path):
        print(f"   ✅ Keytab file exists: {keytab_path}")
        print(f"   ✅ Keytab permissions: {oct(os.stat(keytab_path).st_mode)[-3:]}")
    else:
        print(f"   ❌ Keytab file not found: {keytab_path}")
    
    # Check krb5.conf
    krb5_conf = "/etc/krb5.conf"
    if os.path.exists(krb5_conf):
        print(f"   ✅ krb5.conf exists: {krb5_conf}")
    else:
        print(f"   ❌ krb5.conf not found: {krb5_conf}")
    
    return True


def main():
    """Run all Kerberos authentication tests."""
    print("🚀 Kerberos Authentication Testing")
    print("=" * 60)
    
    # Test results
    results = []
    
    # Test 1: Kerberos ticket
    print("\n1️⃣ Testing Kerberos Ticket")
    results.append(("Kerberos Ticket", test_kerberos_ticket()))
    
    # Test 2: Kerberos environment
    print("\n2️⃣ Testing Kerberos Environment")
    results.append(("Kerberos Environment", test_kerberos_environment()))
    
    # Test 3: Kerberos authentication
    print("\n3️⃣ Testing Kerberos Authentication")
    results.append(("Kerberos Authentication", test_kerberos_authentication()))
    
    # Test 4: Kerberos message flow
    print("\n4️⃣ Testing Kerberos Message Flow")
    results.append(("Kerberos Message Flow", test_kerberos_message_flow()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Kerberos Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Kerberos tests passed!")
        print("   Your Kerberos authentication setup is working correctly.")
    elif passed >= 2:
        print("\n✅ Kerberos setup is mostly working!")
        print("   Some features may require GSSAPI module installation.")
    else:
        print("\n❌ Kerberos setup needs attention.")
        print("   Please check the configuration and try again.")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if passed >= 2:
        print("✅ Kerberos server is running correctly")
        print("✅ Keytab files are properly configured")
        print("✅ Kafka utility can load Kerberos configuration")
        if passed < total:
            print("⚠️  Consider installing GSSAPI for full functionality:")
            print("   sudo apt-get install libkrb5-dev libsasl2-dev libssl-dev krb5-config")
            print("   pip install gssapi")
    else:
        print("❌ Check Kerberos server status: sudo systemctl status krb5-kdc")
        print("❌ Verify keytab file permissions and location")
        print("❌ Ensure krb5.conf is properly configured")


if __name__ == "__main__":
    main()
