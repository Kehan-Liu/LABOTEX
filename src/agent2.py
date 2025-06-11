import os
from src.tools import data_tool_factory, write_latex
from src.agent1 import get_text_by_title
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor, tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

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

    text = get_text_by_title(cfg)
#     text = """
# # 实验数据处理
# 给出你测量的弹簧的拉力和伸长量的数据表格，写明单位。
# 作出弹簧拉力F 和 弹簧伸长量 x 的关系图像，用最小二乘法，计算弹簧筋度系数 k。
# # 分析讨论
# 实验的误差分析
# """
    @tool
    def read_instruction(query: str) -> str:
        """
        Read the experiment instruction.
        Input is the experiment title.
        """
        return text
    tools.append(read_instruction)

    react_prompt = """
你是一个使用 LaTeX 书写实验报告的有用助手。
你需要完成一个物理实验的数据处理任务，并用 LaTeX 格式输出实验报告的 4. 实验数据处理 和 5. 分析讨论 两个部分。注意一定要使用 LaTeX 格式输出。
你可以使用以下工具：

{tools}

你需要一步一步地思考，先用`read_instruction`阅读要求，在处理过程中使用工具，最后用`write_latex`以 LaTeX 格式完成实验报告。

使用以下格式：

Question: 你需要做什么
Thought: 你应该始终思考该做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我完成了数据处理任务，该写实验报告了
Action: write_latex
Action Input: 实验报告内容，LaTeX 格式，只包括你要写的章节
Observation: 结果
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
        memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    )

    agent_executor.invoke({
        "input": cfg.prompt
    })