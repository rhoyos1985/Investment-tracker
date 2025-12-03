from enum import Enum

class MessageErrorValidator(str, Enum):
    int_parsing="This value could not be parsed as an integer."
    is_required="This field is required."
    missing="There are missing values."
