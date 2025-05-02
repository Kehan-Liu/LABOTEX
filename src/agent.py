import os
import yaml
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from tools import search, data_accessor, data_processor

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "../config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

CHAT_MODEL = config["chat_model"]
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
os.environ["OPENAI_BASE_URL"] = config["openai_base_url"]
os.environ["SERPAPI_API_KEY"] = config["serpapi_key"]
OPENAI_BASE = config["openai_base_url"]

chat_model = ChatOpenAI(
    temperature=0,
    model_name=CHAT_MODEL,
    base_url=OPENAI_BASE,
)

tools = [search, data_accessor, data_processor]

react_prompt = """
You need to process some data inside the pandas dataframe called df. The data is from a physics experiment.
You have access to the following tools:

{tools}

You have to think step by step and use the tools when you need to.

Use the following format:

Question: what you need to do with the data
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I finish the task, output "Finish!"

Begin!

Task: {input}
Thought:{agent_scratchpad}
"""

prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template=react_prompt,
)

llm = ChatOpenAI(
    model=CHAT_MODEL,
)

agent = create_react_agent(
    llm,
    tools,
    prompt=prompt,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True)
)

agent_executor.invoke({
    "input": config["query"]
})