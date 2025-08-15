# Kerberos Server Setup Guide

**Author:** Eon (Himanshu Shekhar)  
**Created:** 2025-08-15  
**Description:** Guide for setting up a local Kerberos server for Kafka authentication testing  
**License:** MIT  
**Repository:** https://github.com/eonn/kafka-python-kerberos

This document describes the Kerberos server setup that has been configured for testing the Kafka utility with Kerberos authentication.

## 🎯 Overview

A local Kerberos server has been set up with the following configuration:
- **Realm**: `default`
- **KDC Server**: `Eon (Himanshu Shekhar)-Linux:88`
- **Admin Server**: `Eon (Himanshu Shekhar)-Linux:749`
- **Test User**: `test-user@default`

## 📋 Setup Summary

### 1. Installed Packages
- `krb5-kdc`: Kerberos Key Distribution Center
- `krb5-admin-server`: Kerberos Administration Server
- `krb5-config`: Kerberos configuration utilities
- `krb5-user`: Kerberos user utilities

### 2. Created Principals
- `admin/admin@default`: Administrative principal
- `test-user@default`: Test user principal
- `kafka-user@default`: Kafka user principal (with keytab)

### 3. Generated Keytabs
- `test-user.keytab`: Keytab file for test-user principal
- `kafka-user.keytab`: Keytab file for kafka-user principal

## 🔧 Configuration Files

### Kerberos Configuration (`/etc/krb5.conf`)
```ini
[libdefaults]
        default_realm = default
        kdc_timesync = 1
        ccache_type = 4
        forwardable = true
        proxiable = true
        rdns = false

[realms]
        default = {
                kdc = Eon (Himanshu Shekhar)-Linux:88
                admin_server = Eon (Himanshu Shekhar)-Linux:749
                default_domain = Eon (Himanshu Shekhar)-Linux
        }

[domain_realm]
        .eon-linux = default
        eon-linux = default
```

### Kafka Test Configuration (`test_kafka_config.ini`)
```ini
[kafka]
bootstrap_servers = localhost:9092
topic = test-topic
keytab_path = /home/eon/projects/Kafka-Python/test-user.keytab
principal = test-user@default
service_name = kafka
consumer_group_id = kafka-test-group
auto_offset_reset = earliest
max_poll_records = 500
session_timeout_ms = 30000
heartbeat_interval_ms = 3000
```

## 🚀 Usage Instructions

### 1. Obtain Kerberos Ticket
```bash
# Using keytab (recommended for applications)
kinit -kt test-user.keytab test-user

# Using password (interactive)
kinit test-user
```

### 2. Verify Ticket
```bash
klist
```

### 3. Test Kafka Utility
```bash
# Activate virtual environment
source venv/bin/activate

# Run the test script
python test_kerberos_setup.py
```

### 4. Use with Kafka Utility
```python
from kafka_kerberos_utility import KafkaKerberosUtility

# Use the test configuration
with KafkaKerberosUtility(config_file="test_kafka_config.ini") as kafka:
    # Your Kafka operations here
    pass
```

## 🔐 Security Notes

### Keytab Files
- Location: `/home/eon/projects/Kafka-Python/`
- Permissions: `600` (read/write for owner only)
- Owner: `eon:eon`

### Principals
- **test-user@default**: Password-protected, suitable for interactive use
- **kafka-user@default**: Keytab-based, suitable for application use

## 🧪 Testing

### Automated Tests
The `test_kerberos_setup.py` script verifies:
1. ✅ Kerberos ticket availability
2. ✅ Configuration loading
3. ✅ Producer configuration generation
4. ✅ Consumer configuration generation
5. ✅ Context manager functionality

### Manual Verification
```bash
# Check service status
sudo systemctl status krb5-kdc krb5-admin-server

# List principals
sudo kadmin.local -q "listprincs"

# Test authentication
kinit -kt test-user.keytab test-user
klist
```

## 🔧 Troubleshooting

### Common Issues

1. **Service not starting**
   ```bash
   sudo systemctl restart krb5-kdc krb5-admin-server
   sudo journalctl -u krb5-kdc -f
   ```

2. **Authentication failed**
   ```bash
   # Check keytab
   ktutil -k test-user.keytab list
   
   # Recreate keytab
   sudo kadmin.local -q "ktadd -k /tmp/test-user.keytab test-user"
   ```

3. **Configuration issues**
   ```bash
   # Check configuration
   sudo cat /etc/krb5.conf
   
   # Test connectivity
   telnet localhost 88
   ```

### Log Files
- KDC logs: `/var/log/krb5kdc.log`
- Admin server logs: `/var/log/kadmind.log`
- System logs: `sudo journalctl -u krb5-kdc -f`

## 📚 Next Steps

1. **Set up Kafka broker** with Kerberos authentication
2. **Configure Kafka** for SASL/GSSAPI
3. **Test end-to-end** message production and consumption
4. **Deploy in production** with proper security measures

## 🔗 Related Files

- `kafka_kerberos_utility.py`: Main Kafka utility
- `test_kerberos_setup.py`: Kerberos setup verification
- `test_kafka_config.ini`: Test configuration
- `test-user.keytab`: Test user keytab
- `kafka-user.keytab`: Kafka user keytab

## 📞 Support

For issues with the Kerberos setup:
1. Check service status: `sudo systemctl status krb5-kdc`
2. Review logs: `sudo journalctl -u krb5-kdc -f`
3. Verify configuration: `sudo cat /etc/krb5.conf`
4. Test authentication: `kinit -kt test-user.keytab test-user`
