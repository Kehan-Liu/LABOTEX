import os
from src.tools import data_tool_factory
from src.agent1 import summarize_text
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor, tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

def data_processing_agent(cfg):
    CHAT_MODEL = cfg.chat_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    chat_model = ChatOpenAI(
        temperature=0,
        model_name=CHAT_MODEL,
        base_url=base_url,
    )
    tools, data_saver, get_figures, get_log, plot_tables, write_latex = data_tool_factory(cfg)
    

    text = summarize_text(cfg)
#     text = """
# # 实验数据处理
# 给出你测量的弹簧的拉力和伸长量的数据表格，写明单位。
# 作出弹簧拉力F 和 弹簧伸长量 x 的关系图像，用最小二乘法，计算弹簧筋度系数 k。
# # 分析讨论
# 实验的误差分析
# """
    react_prompt = """
你需要完成一个物理实验的数据处理任务，全部完成后用`write_log`工具按实验顺序分部分记录实验处理中的重要信息。
你可以使用以下工具：

{tools}

你需要一步一步地思考，在处理过程中使用工具，确保完成了全部内容，最后用`write_log`写记录。

严格使用以下格式，不要用加粗或Markdown语法

Question: 你要执行的任务
Thought: 思考你要做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我完成了所有数据处理任务，现在写实验处理记录
Action: write_log
Action Input: 按实验次序全面地记录实验处理中的重要信息（计算结果、图表名称等）
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
        max_iterations=50,
        handle_parsing_errors=True,
    )

    agent_executor.invoke({
        "input": text + "\n全部数据处理任务完成后，使用`write_log`工具记录信息\n" + cfg.prompt
    })

    data_saver()

    figures = get_figures()
    log = get_log()
    tables = plot_tables()

    writer_prompt = f"""
你是一个物理实验报告写作助手，需要根据实验要求和实验数据，按照 LaTeX 格式，写作实验报告的 实验数据处理 和 分析讨论 两部分。要求：包含文字说明、图像和原始表格（已转换为图像，直接插入），按照实验任务的顺序有条理的书写。

数据处理部分的任务为：
{text}

实验数据处理过程中的重要信息如下：
{log}

原始数据表格图片路径如下：
{tables}

对表格名称的解释：{cfg.prompt}

所有实验图像的路径为：
{figures}

你的输出应该是 LaTeX 代码，格式如下：
\\section{{实验数据处理}}
各部分数据处理的文字说明、图像和原始数据表格，按数据处理任务顺序写作

\\section{{分析讨论}}
分析讨论的文字说明
"""
    messages = [HumanMessage(content=writer_prompt)]
    response = chat_model.invoke(messages)
    latex_code = response.content.strip()
    write_latex(latex_code)
