import gradio as gr
from src.book_agent import pdf_to_json
from src.agent1 import write_experiment_introduction
from src.agent2 import data_processing_agent
from src.agent3 import write_final_report
import os
import shutil

class CFG:
    def __init__(self, title, dir_name, chat_model, vl_model, prompt):
        self.title = title
        self.dir_name = dir_name
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        self.chat_model = chat_model
        self.vl_model = vl_model
        self.prompt = prompt

def page_one_action(dir_name, vl_model, api_key, base_url, file_input):
    cfg = CFG(
        title="none",
        dir_name=dir_name,
        chat_model="none",
        vl_model=vl_model,
        prompt="none"
    )
    # Create the target directory if it doesn't exist
    base_books_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "books"))
    target_dir = os.path.join(base_books_dir, dir_name)
    os.makedirs(target_dir, exist_ok=True)

    # Move the uploaded file to the target directory
    if file_input is not None:
        # file_input is a tempfile.NamedTemporaryFile or similar
        filename = os.path.basename(file_input.name)
        dest_path = os.path.join(target_dir, filename)
        shutil.move(file_input.name, dest_path)

    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = base_url

    try:
        pdf_to_json(cfg)
        return "Book Successfully Loaded!"
    except Exception as e:
        return "Failed to Load the Book."


def page_two_action(title, dir_name, chat_model, prompt, api_key, base_url,file_input):
    cfg = CFG(
        title=title,
        dir_name=dir_name,
        chat_model=chat_model,
        vl_model="none",
        prompt=prompt
    )
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = base_url

    os.makedirs(cfg.data_dir, exist_ok=True)
    # Delete all files in cfg.data_dir if any exist
    for filename in os.listdir(cfg.data_dir):
        file_path = os.path.join(cfg.data_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    if file_input is not None:
        for file in file_input:
            filename = os.path.basename(file.name)
            dest_path = os.path.join(cfg.data_dir, filename)
            shutil.move(file.name, dest_path)

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tmp"))
    os.makedirs(tmp_dir, exist_ok=True)
    # Delete all files and folders in tmp_dir if any exist
    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    write_experiment_introduction(cfg)

    data_processing_agent(cfg)

    write_final_report(cfg)

    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "final_pdf", f"{title}.pdf"))

    plots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plots"))
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tmp"))
    if os.path.isdir(plots_dir):
        shutil.rmtree(plots_dir)
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    return "Report Successfully Written!", pdf_path

def run_page_two_action(title, dir_name, chat_model, prompt, api_key, base_url, file_input):
    msg, pdf_path = page_two_action(title, dir_name, chat_model, prompt, api_key, base_url, file_input)
    return msg, pdf_path

def get_pdf_path(pdf_path):
        return pdf_path

with gr.Blocks() as demo:
    gr.Markdown("## Choose What to Do")
    btn1 = gr.Button("Add New Instruction Books", link="/page-one")
    btn2 = gr.Button("Write Reports", link="/page-two")
    # use dummy placeholders so buttons don't error out
    dummy = gr.Textbox(visible=False)

with demo.route("Add New Instruction Books", "/page-one"):
    inp1 = gr.Textbox(label="Book Name", placeholder="single English word without space")
    inp2 = gr.Textbox(label="Vision Language Model Name")
    inp3 = gr.Textbox(label="API Key", type="password")
    inp4 = gr.Textbox(label="Base URL")
    file_input = gr.File(label="Drag Your PDF Here", file_types=[".pdf"])    
    submit_btn = gr.Button("Start to Load")
    out1 = gr.Textbox(label="Output", visible=True)
    submit_btn.click(
        fn=page_one_action,
        inputs=[inp1, inp2, inp3, inp4, file_input],
        outputs=out1
    )
   
with demo.route("Write Reports", "/page-two"):
    inp1 = gr.Textbox(label="Reference Book Name")
    inp2 = gr.Textbox(label="Title of the Report")
    inp3 = gr.Textbox(label="Chat Model Name")
    inp4 = gr.Textbox(label="Description of Your CSV Files")
    inp5 = gr.Textbox(label="API Key", type="password")
    inp6 = gr.Textbox(label="Base URL")
    file_input = gr.File(label="Drag Your CSV Files Here", file_types=[".csv"], file_count="multiple")
    generate_btn = gr.Button("Generate PDF")
    out1 = gr.Textbox(label="Output", visible=True)
    pdf_path_box = gr.Textbox(label="PDF Path", visible=False)
    download_btn = gr.DownloadButton("Download PDF", visible=True)

    generate_btn.click(
        fn=run_page_two_action,
        inputs=[inp2, inp1, inp3, inp4, inp5, inp6, file_input],
        outputs=[out1, pdf_path_box]
    )    

    download_btn.click(
        fn=get_pdf_path,
        inputs=[pdf_path_box],
        outputs=[download_btn]
    )
    

if __name__ == "__main__":
    demo.launch()