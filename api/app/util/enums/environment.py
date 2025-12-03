from enum import Enum

class Api_Environment(str, Enum):
    DEV="dev"
    TEST="test"
    STAGING="staging"
    PRODUCTION="prod"

api_environments = Api_Environment
