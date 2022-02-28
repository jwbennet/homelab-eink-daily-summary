from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List, Optional

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Meeting:
    start_time: str
    end_time: str
    summary: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Task:
    complete: bool
    summary: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Weather:
    time: str
    condition: str
    temperature: int
    precipitation: int

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Summary:
    schedule: Optional[List[Meeting]]
    tasks: Optional[List[Task]]
    weather: Optional[List[Weather]]
