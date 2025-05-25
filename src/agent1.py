import os
import json
from pdfminer.high_level import extract_text
import requests
from openai import OpenAI
import yaml
import ijson

# query = "晶体学"

# dir_name = "book1" # where the PDF file is located
# model_name = "deepseek-v3" 

# # Load OpenAI API key and base URL from config.yaml
# config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.yaml"))
# with open(config_path, "r") as f:
#     config = yaml.safe_load(f)
# api_key = config.get("openai_api_key")
# base_url = config.get("openai_base_url")
# json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}/{dir_name}.json"))

# client = OpenAI(api_key=api_key, base_url=base_url)

def load_experiments_json(json_path):
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
        experiments = load_experiments_json(dir_name)
        return [item.get("title", "") for item in experiments if "title" in item]

def find_best_title_match(user_title, titles : str, chat_model, client):
    query = user_title
    """Find the title that best matches the query."""
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
    # print(title.lower()) # test 多了单引号
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            for item in ijson.items(f, "item"):
                # print(item.get("title", "").lower()) # test
                if item.get("title", "").lower() == title.lower():
                    # print("1") # test
                    return item.get("text", "")
            # Fallback: try substring match
            f.seek(0)
            for item in ijson.items(f, "item"):
                if title.lower() in item.get("title", "").lower():
                    # print("2") # test
                    return item.get("text", "")
        # print("3") # test
        return ""
    except ImportError:
        # Fallback to loading the whole file if ijson is not available
        experiments = load_experiments_json()
        for item in experiments:
            if item.get("title", "").lower() == title.lower():
                # print("4") # test
                return item.get("text", "")
        for item in experiments:
            if title.lower() in item.get("title", "").lower():
                # print("5")
                return item.get("text", "")
        # print("6") # test
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

# titles = get_titles_from_json() # titles is a python list.
# title = find_best_title_match(query, str(titles))
# text = get_text_by_title(title)
# code = write_experiment_introduction(title, text)
# output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tmp/output.txt"))
# with open(output_path, "a", encoding="utf-8") as f:
#     f.write(code + "\n")

