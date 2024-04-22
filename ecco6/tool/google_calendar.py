from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool


class GetEventsInput(BaseModel):
    date: str = Field(description="The date in RFC3339 format.")

def get_events(date: str) -> str:
    """Test version, will update later"""
    return "13:00 Study\n15:00 Go to gym\n20:00 Have dinner"


get_events_tool = StructuredTool.from_function(
    func=get_events,
    name="get_events_tool",
    description="Get all events of a day.",
    args_schema=GetEventsInput,
)

