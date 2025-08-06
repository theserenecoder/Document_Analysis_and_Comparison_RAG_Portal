from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict
class Metadata(BaseModel):
    Summary: List[str] = Field(default_factory=list, description='Summary of the document')
    Title: str
    Author: str
    DateCreated: str
    LastModifiedDate: str
    
    
class ChangeFormat(BaseModel):
    Page: str
    changes: str
    
class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass