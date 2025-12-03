from datetime import datetime
from typing import Optional
    
class ApiDateTime():
    format: str
    def __init__(self, format: Optional[str] = None):
        self.format = format if format else "%Y-%m-%d %H:%M:%S"

    def get_datetime_now(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime(self.format)
        return formatted_datetime

api_datetime = ApiDateTime()
