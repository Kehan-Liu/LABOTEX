import os
import json
from openai import OpenAI
import ijson


def load_experiments_json(json_path):
    """
    Load the whole json file of the experiment book.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_titles_from_json(json_path):
    """
    Efficiently extract all 'title' fields from the JSON file.
    """
    try:
        titles = []
        with open(json_path, "r", encoding="utf-8") as f:
            for item in ijson.items(f, "item"):
                if "title" in item:
                    titles.append(item["title"])
        return titles
    except ImportError:
        # Fallback to loading the whole file if ijson is not available
        experiments = load_experiments_json(json_path)
        return [item.get("title", "") for item in experiments if "title" in item]

def find_best_title_match(user_title, titles : str, chat_model, client):    
    """Find the title that best matches the query (user_title)."""
    query = user_title
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "你是一个可以从 python list 中找到与用户输入的实验题目最匹配的实验题目的有用助手。"},
            {"role": "user", "content": f"用户输入的实验题目为：{query}，以下是以 python list 形式呈现的一系列实验题目：{titles}。请从中找出与用户输入的实验题目最匹配的实验题目，并原封不动地输出 python list 中该题目。要求不要输出代表字符串的单引号或双引号。"},
        ],
        temperature=0.0
    )
    return response.choices[0].message.content


def get_text_by_title(cfg):
    """Retrieve the 'text' corresponding to the user title."""
    chat_model = cfg.chat_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    dir_name = cfg.dir_name
    chat_model = cfg.chat_model
    client = OpenAI(api_key=api_key, base_url=base_url)
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}/{dir_name}.json"))
    user_title = cfg.title
    titles = get_titles_from_json(json_path)
    title = find_best_title_match(user_title, str(titles), chat_model, client)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            for item in ijson.items(f, "item"):
                if item.get("title", "").lower() == title.lower():
                    return item.get("text", "")
            # Fallback: try substring match
            f.seek(0)
            for item in ijson.items(f, "item"):
                if title.lower() in item.get("title", "").lower():
                    return item.get("text", "")
        return ""
    except ImportError:
        # Fallback to loading the whole file if ijson is not available
        experiments = load_experiments_json()
        for item in experiments:
            if item.get("title", "").lower() == title.lower():
                return item.get("text", "")
        for item in experiments:
            if title.lower() in item.get("title", "").lower():
                return item.get("text", "")
        return ""

def write_experiment_introduction(cfg):
    """Ask the LLM to write an experiment introduction using the provided text."""
    chat_model = cfg.chat_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    dir_name = cfg.dir_name
    chat_model = cfg.chat_model
    client = OpenAI(api_key=api_key, base_url=base_url)
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}/{dir_name}.json"))
    user_title = cfg.title
    titles = get_titles_from_json(json_path)
    title = find_best_title_match(user_title, str(titles), chat_model, client)
    text = get_text_by_title(cfg)
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "你是一位会书写 LaTeX 实验报告的有用助手。"},
            {"role": "user", "content": (
                f"请根据提供的实验指导书相应内容，用 LaTeX 格式书写一篇关于实验{title}的实验报告中的 1、摘要，2、实验原理，3、实验仪器及实验步骤 三个部分。\n"
                "格式：仅包含 LaTeX 代码中的这三个 section ，不包括 \\documentclass、\\begin{document}、\\end{document}、\\usepackage{} 等部分。\n"
                "要求：1、摘要部分描述实验通过什么方法与仪器，测量了什么，得到了什么；"
                "2、实验原理部分包含对实验涉及物理原理的解释及公式推导（参考指导书）；"
                "3、实验仪器及实验步骤部分包含详细的实验仪器清单以及简要的实验步骤（参考指导书）。\n"
                f"以下是实验指导书的内容：{text}。"
            )},
        ],
        temperature=0.1
    )
    code = response.choices[0].message.content
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tmp/output.txt"))
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(code + "\n")
    return response.choices[0].message.content


def summarize_text(cfg):
    """
    Ask the LLM to summarize the provided text.
    """
    chat_model = cfg.chat_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    text = get_text_by_title(cfg)
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "你是一位善于概括与提取信息的有用助手。"},
            {"role": "user", "content": (
                f"请根据提供的实验指导书内容，提取出在实验数据处理部分要完成的任务，尽量简洁，舍去其中的误差分析计算部分，对要绘制的图，指明要线性拟合还是作曲线"
                f"以下是实验指导书的内容：{text}。"
            )},
        ],
        temperature=0.0
    )
    return response.choices[0].message.content

