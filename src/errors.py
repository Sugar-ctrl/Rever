from enum import Enum

class ErrorDurationType(Enum):
    START = 1
    RUN = 2

class ReverError(Exception):
    def __init__(self, *args: object, error_duration: ErrorDurationType=ErrorDurationType.RUN) -> None:
        super().__init__(*args)
        self.error_duration = error_duration

    def __str__(self) -> str:
        result:str = f'ReverError - {self.__class__.__name__} cause during {self.error_duration.name}'
        if self.args:
            result += f': {self.args[0]}'
        return result + self.format_message()
    
    def format_message(self) -> str:
        return ''
    
class ReverSyntaxError(ReverError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args, error_duration=ErrorDurationType.START)

class ReverUnicodeError(ReverError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args, error_duration=ErrorDurationType.START)
