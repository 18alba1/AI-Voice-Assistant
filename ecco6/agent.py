import functools
from typing import Mapping, Sequence

import streamlit as st

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from ecco6.tool import google_calendar
from ecco6.tool import time
from ecco6.tool import location


class Ecco6Agent:
  def __init__(
      self, openai_api_key: str, google_credentials, chat_model: str = "gpt-4-turbo"):
    self.google_credentials = google_credentials
    llm = ChatOpenAI(model=chat_model, api_key=openai_api_key)
    prompt = hub.pull("hwchase17/openai-functions-agent")
    tools = self._create_tools()
    agent = create_tool_calling_agent(llm, tools, prompt)
    self.agent_executor = AgentExecutor(
       agent=agent, tools=tools, verbose=True)
    
  def _create_tools(self):
    tools = []
    if self.google_credentials is not None:
      get_events_by_date_tool = StructuredTool.from_function(
          func=functools.partial(
            google_calendar.get_events_by_date, google_credentials=self.google_credentials),
          name="get_events_by_date",
          description="Get all events of a day.",
          args_schema=google_calendar.GetEventsByDateInput,
      )
      tools.append(get_events_by_date_tool)

    get_current_time_tool = StructuredTool.from_function(
        func=time.get_current_time,
        name="get_current_time",
        description="Get the current date, time and the week day name."
    )
    tools.append(get_current_time_tool)
    
    add_event_tool = StructuredTool.from_function(
        func=functools.partial(
        google_calendar.add_event, google_credentials=self.google_credentials),
        name="add_event",
        description="Add an event to the calendar.",
        args_schema=google_calendar.AddEventInput,
    )
    tools.append(add_event_tool)

    remove_event_tool = StructuredTool.from_function(
        func=functools.partial(
            google_calendar.remove_event, google_credentials=self.google_credentials),
        name="remove_event",
        description="Remove an event from the calendar.",
        args_schema=google_calendar.RemoveEventInput,
    )
    tools.append(remove_event_tool)

    get_unread_messages_tool = StructuredTool.from_function(
          func=functools.partial(google_calendar.get_unread_messages, google_credentials=self.google_credentials),
          name="get_unread_messages",
          description="Retrieve unread messages from Gmail.",
          args_schema=google_calendar.GetUnreadMessagesInput,
    )
    tools.append(get_unread_messages_tool)
    
    send_email_tool = StructuredTool.from_function(
        func=functools.partial(google_calendar.send_email, google_credentials=self.google_credentials),
        name="send_email",
        description="Send an email via Gmail.",
        args_schema=google_calendar.SendEmailInput,
    )
    tools.append(send_email_tool)

    if "latitude" in st.session_state and "longitude" in st.session_state:
      get_current_location_tool = StructuredTool.from_function(
          func=lambda x: location.get_current_location(latitude=st.session_state.latitude, longitude=st.session_state.longitude),
          name="get_current_location",
          description="Get my current location.",
      )
      tools.append(get_current_location_tool)
    return tools
  
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
