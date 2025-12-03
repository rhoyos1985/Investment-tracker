from enum import Enum

class DatabaseQuery(str, Enum):
    HEALTH_SELECT="SELECT 1"
