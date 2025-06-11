import os
from src.tools import data_tool_factory, write_latex
from src.agent1 import summarize_text
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor, tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

def data_processing_agent(cfg):
    CHAT_MODEL = cfg.chat_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    chat_model = ChatOpenAI(
        temperature=0,
        model_name=CHAT_MODEL,
        base_url=base_url,
    )
    tools = data_tool_factory(cfg)
    tools.append(write_latex)

    text = summarize_text(cfg)
#     text = """
# # 实验数据处理
# 给出你测量的弹簧的拉力和伸长量的数据表格，写明单位。
# 作出弹簧拉力F 和 弹簧伸长量 x 的关系图像，用最小二乘法，计算弹簧筋度系数 k。
# # 分析讨论
# 实验的误差分析
# """
    react_prompt = """
你需要完成一个物理实验的数据处理任务，并用 LaTeX 格式输出实验报告的 4. 实验数据处理 和 5. 分析讨论 两个部分。注意一定要使用 LaTeX 格式输出。
你可以使用以下工具：

{tools}

你需要一步一步地思考，在处理过程中使用工具，确保完成了全部内容，最后用`write_latex`把结果写进文件中。

严格使用以下格式，不要用加粗或Markdown语法

Question: 你要执行的任务
Thought: 思考你要做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我完成了数据处理任务，现在写实验报告
Action: write_latex
Action Input: 实验报告内容，LaTeX 格式，只包括实验数据处理和分析讨论两部分
Observation: 成功与否
Thought: 我完成了任务
Final Answer: Finish!

开始！

Task: {input}
Thought: {agent_scratchpad}
"""
    prompt = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template=react_prompt,
    )
    agent = create_react_agent(
        llm=chat_model,
        tools=tools,
        prompt=prompt,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        ),
    )

    agent_executor.invoke({
        "input": text + cfg.prompt
    })