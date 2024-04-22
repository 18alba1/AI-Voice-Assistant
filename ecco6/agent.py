from typing import Mapping, Sequence

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from ecco6.tool.time import get_current_time_tool
from ecco6.tool.google_calendar import get_events_tool


class Ecco6Agent:
  def __init__(self, openai_api_key: str, chat_model: str = "gpt-4-turbo"):
    llm = ChatOpenAI(model=chat_model, api_key=openai_api_key)
    prompt = hub.pull("hwchase17/openai-functions-agent")
    tools = [get_current_time_tool, get_events_tool]
    agent = create_tool_calling_agent(llm, tools, prompt)
    self.agent_executor = AgentExecutor(
       agent=agent, tools=tools, verbose=True)
    
  def chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
    chat_history = []
    for message in messages[:-1]:
      if message["role"] == "user":
        chat_history.append(HumanMessage(content=message["content"]))
      else:
        chat_history.append(AIMessage(content=message["content"]))
    
    result = self.agent_executor.invoke({
      "chat_history": chat_history,
      "input": messages[-1]["content"],
    })
    return result["output"]
