import os
import yaml
import json
from openai import OpenAI
from pdf2image import convert_from_path
import io
from PIL import Image
import base64

# dir_name = "book1" # where the PDF file is located
# vl_model_name = "qwen2.5-vl-72b-instruct"
# model_name = "deepseek-v3"

# Load OpenAI API key and base URL from config.yaml
# config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.yaml"))
# with open(config_path, "r") as f:
#     config = yaml.safe_load(f)
# api_key = config.get("openai_api_key")
# base_url = config.get("openai_base_url")

# Find the PDF file in the target directory
# books_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}"))
# pdf_filename = next((f for f in os.listdir(books_dir) if f.lower().endswith(".pdf")), None)
# if not pdf_filename:
#     raise FileNotFoundError(f"No PDF file found in {books_dir}")
# pdf_path = os.path.join(books_dir, pdf_filename)
# json_path = os.path.join(books_dir, f"{dir_name}.json")

# client = OpenAI(api_key=api_key, base_url=base_url)

def judge_new_section(base64_image, vl_model_name, client):
    response = client.chat.completions.create(
        model=vl_model_name,
        messages=[
            {"role": "system", "content": "你是一个能够判断这一页是否是新章节起始页的有用助手。"},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "这一页是一个新章节的起始页吗？答案只能是 'True' 或 'False'。新章节的起始页一般包含标题，还可能有引言等内容。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
    )
    return response.choices[0].message.content

def extract_title(base64_image, vl_model_name, client):
    response = client.chat.completions.create(
        model=vl_model_name,
        messages=[
            {"role": "system", "content": "你是一个能够提取标题的有用助手。"},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "提取这一页的标题，一般是一个物理实验的名称，答案只能是一个字符串。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
    )
    return response.choices[0].message.content

def pdf_to_json(cfg):
    # first load the config from the cfg object
    dir_name = cfg.dir_name
    vl_model_name = cfg.vl_model
    api_key = cfg.openai_api_key
    base_url = cfg.openai_base_url
    books_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}"))
    pdf_filename = next((f for f in os.listdir(books_dir) if f.lower().endswith(".pdf")), None)
    if not pdf_filename:
        raise FileNotFoundError(f"No PDF file found in {books_dir}")
    pdf_path = os.path.join(books_dir, pdf_filename)
    json_path = os.path.join(books_dir, f"{dir_name}.json")
    client = OpenAI(api_key=api_key, base_url=base_url)

    if os.path.exists(json_path):
        os.remove(json_path)
    title = None
    content = ""
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        # Encode image directly from memory
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        response = client.chat.completions.create(
            model=vl_model_name,
            messages=[
                {"role": "system", "content": "你是一个能够将图像转为文本得有用助手。"},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "将图像转化为文本，将数学公式保留为 markdown 格式，及 $...$ 。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
        )
        text = response.choices[0].message.content

        if judge_new_section(base64_image, vl_model_name, client) == "True":            
            if os.path.exists(json_path):
                with open(json_path, "r") as jf:
                    data = json.load(jf)
            else:
                data = []
            if title == None:
                title = extract_title(base64_image, vl_model_name, client)
                content = text
            else:
                data.append({"title": title, "text": content})
                with open(json_path, "w") as jf:
                    json.dump(data, jf, ensure_ascii=False, indent=2)
                title = extract_title(base64_image, vl_model_name, client)
                content = text
        else:
            content += text

        




