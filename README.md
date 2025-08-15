# Kafka Python Utility with Kerberos Authentication

**Author:** Eon (Himanshu Shekhar)  
**Created:** 2025-08-15  
**Description:** Comprehensive Python utility for Apache Kafka with Kerberos (GSSAPI) authentication  
**License:** MIT  
**Repository:** https://github.com/eonn/kafka-python-kerberos

A comprehensive Python utility for Apache Kafka that supports Kerberos (GSSAPI) authentication via keytab files. This utility provides easy-to-use interfaces for both producing and consuming messages from Kafka topics with robust error handling and flexible configuration options.

## Features

- ✅ **Kerberos Authentication**: Full support for GSSAPI authentication using keytab files
- ✅ **Configurable Brokers**: Connect to multiple Kafka brokers
- ✅ **Message Production & Consumption**: Easy-to-use APIs for both operations
- ✅ **Flexible Configuration**: Support for environment variables and config files
- ✅ **JAAS Integration**: Automatic JAAS configuration generation
- ✅ **Error Handling**: Comprehensive error handling for authentication and connection issues
- ✅ **Context Manager Support**: Automatic resource cleanup
- ✅ **Logging**: Detailed logging for debugging and monitoring
- ✅ **Type Hints**: Full type annotation support

## Prerequisites

- Python 3.7+
- Apache Kafka cluster with Kerberos authentication enabled
- Kerberos keytab file for authentication
- Network access to Kafka brokers

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Kafka-Python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies (Ubuntu/Debian):**
   ```bash
   sudo apt-get update
   sudo apt-get install libkrb5-dev libsasl2-dev libssl-dev
   ```

## Configuration

### Environment Variables (Recommended)

Copy the example environment file and update it with your configuration:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```bash
# Required Configuration
KAFKA_BOOTSTRAP_SERVERS=broker1.example.com:9092,broker2.example.com:9092
KAFKA_TOPIC=my-kafka-topic
KAFKA_KEYTAB_PATH=/path/to/your/user.keytab
KAFKA_PRINCIPAL=user@EXAMPLE.COM
KAFKA_SERVICE_NAME=kafka

# Optional Configuration
KAFKA_CONSUMER_GROUP_ID=kafka-utility-group
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_MAX_POLL_RECORDS=500
KAFKA_SESSION_TIMEOUT_MS=30000
KAFKA_HEARTBEAT_INTERVAL_MS=3000
```

### Configuration File

Alternatively, you can use a configuration file:

```bash
cp kafka_config.ini kafka_config.ini
```

Edit `kafka_config.ini` with your values:

```ini
[kafka]
bootstrap_servers = broker1.example.com:9092,broker2.example.com:9092
topic = my-kafka-topic
keytab_path = /path/to/your/user.keytab
principal = user@EXAMPLE.COM
service_name = kafka
consumer_group_id = kafka-utility-group
auto_offset_reset = earliest
max_poll_records = 500
session_timeout_ms = 30000
heartbeat_interval_ms = 3000
```

## Usage

### Basic Usage

```python
from kafka_kerberos_utility import KafkaKerberosUtility

# Initialize the utility
kafka_util = KafkaKerberosUtility()

# Produce a message
message = {"user_id": 123, "action": "login", "timestamp": "2024-01-01T12:00:00Z"}
success = kafka_util.produce_message(message, key="user_123")

# Consume messages
messages = kafka_util.consume_messages(max_messages=5, timeout_ms=5000)

# Clean up
kafka_util.close()
```

### Context Manager Usage (Recommended)

```python
from kafka_kerberos_utility import KafkaKerberosUtility

with KafkaKerberosUtility() as kafka:
    # Produce messages
    kafka.produce_message({"test": "message"}, key="test_key")
    
    # Consume messages
    messages = kafka.consume_messages(max_messages=1)
    print(f"Consumed: {messages}")
```

### Custom Message Handler

```python
def message_handler(message, record):
    print(f"Processing: {message}")
    print(f"Topic: {record.topic}, Partition: {record.partition}")

with KafkaKerberosUtility() as kafka:
    messages = kafka.consume_messages(
        message_handler=message_handler,
        max_messages=10
    )
```

### Configuration File Usage

```python
from kafka_kerberos_utility import KafkaKerberosUtility

# Use configuration file
kafka_util = KafkaKerberosUtility(config_file="kafka_config.ini")
```

## Configuration Parameters

### Required Parameters

| Parameter | Environment Variable | Description |
|-----------|---------------------|-------------|
| Bootstrap Servers | `KAFKA_BOOTSTRAP_SERVERS` | Comma-separated list of Kafka brokers |
| Topic | `KAFKA_TOPIC` | Default topic for operations |
| Keytab Path | `KAFKA_KEYTAB_PATH` | Path to Kerberos keytab file |
| Principal | `KAFKA_PRINCIPAL` | Kerberos principal (e.g., "user@REALM") |

### Optional Parameters

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| Service Name | `KAFKA_SERVICE_NAME` | `kafka` | Kerberos service name |
| Consumer Group ID | `KAFKA_CONSUMER_GROUP_ID` | `kafka-utility-group` | Consumer group identifier |
| Auto Offset Reset | `KAFKA_AUTO_OFFSET_RESET` | `earliest` | Offset reset policy |
| Max Poll Records | `KAFKA_MAX_POLL_RECORDS` | `500` | Maximum records per poll |
| Session Timeout | `KAFKA_SESSION_TIMEOUT_MS` | `30000` | Session timeout in ms |
| Heartbeat Interval | `KAFKA_HEARTBEAT_INTERVAL_MS` | `3000` | Heartbeat interval in ms |
| JAAS Config Path | `KAFKA_JAAS_CONFIG_PATH` | Auto-generated | Custom JAAS configuration |

## Error Handling

The utility provides comprehensive error handling:

```python
from kafka_kerberos_utility import KafkaKerberosUtility, KafkaKerberosError

try:
    with KafkaKerberosUtility() as kafka:
        kafka.produce_message({"test": "data"})
except KafkaKerberosError as e:
    print(f"Kafka error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Error Scenarios

1. **Authentication Errors**: Invalid keytab or principal
2. **Connection Errors**: Network issues or broker unavailability
3. **Configuration Errors**: Missing required parameters
4. **Topic Errors**: Non-existent topics or permission issues

## Kerberos Setup

### Keytab File

1. **Generate a keytab file:**
   ```bash
   ktutil
   addent -password -p user@REALM -k 1 -e aes256-cts-hmac-sha1-96
   wkt user.keytab
   quit
   ```

2. **Set proper permissions:**
   ```bash
   chmod 600 user.keytab
   ```

### JAAS Configuration

The utility automatically generates JAAS configuration, but you can provide a custom one:

```java
KafkaClient {
    com.sun.security.auth.module.Krb5LoginModule required
    useKeyTab=true
    storeKey=true
    keyTab="/path/to/user.keytab"
    principal="user@REALM";
};
```

## Examples

Run the comprehensive example script:

```bash
python example_usage.py
```

This will demonstrate:
- Basic message production and consumption
- Context manager usage
- Custom message handlers
- Error handling
- Configuration file usage
- Advanced usage patterns

## Logging

The utility provides detailed logging to help with debugging:

- **Connection events**: Producer/consumer creation and closure
- **Message events**: Production and consumption details
- **Error events**: Authentication and connection failures
- **Configuration events**: Parameter validation and setup

Logs are written to both console and `kafka_kerberos_utility.log`.

## Security Considerations

1. **Keytab Security**: Store keytab files securely with restricted permissions
2. **Network Security**: Use SSL/TLS for production environments
3. **Principal Management**: Use dedicated principals for applications
4. **Configuration Security**: Secure environment variables and config files

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify keytab file path and permissions
   - Check principal format and realm
   - Ensure Kerberos configuration is correct

2. **Connection Refused**
   - Verify broker addresses and ports
   - Check network connectivity
   - Ensure Kafka cluster is running

3. **Topic Not Found**
   - Verify topic exists
   - Check user permissions
   - Ensure topic name is correct

4. **JAAS Configuration Issues**
   - Check JAAS file syntax
   - Verify file permissions
   - Ensure Java security settings

### Debug Mode

Enable debug logging by modifying the logging level in the utility:

```python
import logging
logging.getLogger('kafka_kerberos_utility').setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue with detailed information
4. Include configuration (without sensitive data) and error messages
