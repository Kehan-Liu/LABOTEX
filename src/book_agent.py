import os
import json
from openai import OpenAI
from pdf2image import convert_from_path
import io
import base64


def judge_new_section(base64_image, vl_model_name, client):
    """
    judge whether the given image is a new section start page.
    """
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
    """
    Used for the start page of a new section. Extract the title of the new section from the page.
    """
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
    """
    load the experiment book pdf into json file.
    """
    # first load the config from the cfg object.
    dir_name = cfg.dir_name
    vl_model_name = cfg.vl_model
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    books_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../books/{dir_name}"))
    pdf_filename = next((f for f in os.listdir(books_dir) if f.lower().endswith(".pdf")), None)
    if not pdf_filename:
        raise FileNotFoundError(f"No PDF file found in {books_dir}")
    pdf_path = os.path.join(books_dir, pdf_filename)
    json_path = os.path.join(books_dir, f"{dir_name}.json")
    client = OpenAI(api_key=api_key, base_url=base_url)
    # Remove the existing json.
    if os.path.exists(json_path):
        os.remove(json_path)
    # Used to record the title and content fields of the json file.
    title = None
    content = ""
    # Extract text from each page of the PDF file.
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

        




