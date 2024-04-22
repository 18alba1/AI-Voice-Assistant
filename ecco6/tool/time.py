import datetime

from langchain.tools import StructuredTool


def get_current_time() -> str:
    return datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


get_current_time_tool = StructuredTool.from_function(
    func=get_current_time,
    name="get_current_time",
    description="Get the current time."
)