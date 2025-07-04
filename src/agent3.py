import os
import subprocess
from openai import OpenAI


def get_compilable_latex(draft, chat_model, user_title):
    """
    Integrate the sections in output.txt into a compilable LaTeX source code.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")    
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "你是一位会书写 LaTeX 实验报告的有用助手。"},
            {"role": "user", "content": (
                f"请将以下 LaTeX 草稿修正为可编译的完整LaTeX源代码：\n{draft}\n"
                f"""要求：
                1、只输出 LaTeX 源代码，不要输出其他影响编译的内容，也不要输出 latex```；
                2、在geometry环境中设定margin=1in，并调用`amsmath`和`amssymb`以及其他必要的宏包；
                3、确保图片在正确位置，使用`float`环境和`[H]`选项，所有图片单独一行，不要并列放置；
                4、使用 ctexart 文档类；
                5、实验报告题目为：{user_title}；
                6、如果草稿中有markdown而非LaTeX的语法，请将其转换为LaTeX；
                7、删除草稿中`（见 plot/figure_name.png）`这样注释性的语句；
                8、确保代码可以编译成PDF。"""
            )}
        ],
        temperature=0
    )
    return response.choices[0].message.content


def write_final_report(cfg):
    """
    Write the final LaTeX report and compile it to PDF.
    """
    chat_model = cfg.chat_model
    user_title = cfg.title
    with open('tmp/output.txt', 'r', encoding='utf-8') as f:
        draft_latex = f.read()
    compilable_latex = get_compilable_latex(draft_latex, chat_model, user_title)
    with open(f'{user_title}.tex', 'w', encoding='utf-8') as f:
        f.write(compilable_latex)
    compile_cmd = f"xelatex -output-directory=. {user_title}.tex"
    subprocess.run(compile_cmd, shell=True, check=True)
    subprocess.run(compile_cmd, shell=True, check=True)
    os.makedirs('final_pdf', exist_ok=True)
    move_cmd = f"mv {user_title}.pdf final_pdf/"
    subprocess.run(move_cmd, shell=True, check=True)
    clear = f"rm -f {user_title}.aux {user_title}.log"
    subprocess.run(clear, shell=True, check=True)
