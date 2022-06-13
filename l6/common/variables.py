import logging
import sys

# DEFAULT CONFIG:
DEFAULT_IP_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 7777
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
LOGGING_LVL = logging.DEBUG
DEFAULT_LOG_NAME = 'server' if 'server.py' in sys.argv[0] else 'client'

# JIM (JSON Instant Messaging) MAIN KEYS:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# JIM OTHER KEYS:
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
