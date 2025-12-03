from typing import Dict, Any, Unpack
from pydantic import BaseModel, ConfigDict
from app.util.functions.api_datetime import api_datetime
from app.util.dtos.extra_logger_information import ExtraInformationLogger


class LoggerMapper(ExtraInformationLogger):
    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        return super().__init_subclass__(**kwargs)

    def serializable_data(self, model: BaseModel):
        try:
            if hasattr(model, 'model_dump'):
                data = model.model_dump()
            else:
                data = model.dict()
            
            return data
        except Exception as e:
            return {
                "pydantic_serialization_error": str(e),
                "model_class": model.__class__.__name__
            }

    def to_log_format(self) -> Dict[str, Any]:
        serialized_data = self.serializable_data(self.extra_data)if self.extra_data else None
        
        log_entry = {
            "timestamp": api_datetime.get_datetime_now(),
            "data": serialized_data,
            "data_type": type(self.extra_data).__name__ if self.extra_data else "None"
        }
        
        return log_entry
