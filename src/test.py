from omegaconf import OmegaConf
from src.book_agent import pdf_to_json
import os
from src.agent1 import get_text_by_title, write_experiment_introduction
from src.agent2 import data_processing_agent
from src.agent3 import write_final_report
import getpass

cfg = OmegaConf.load('config.yaml')
# os.environ["OPENAI_API_KEY"] = getpass.getpass("Please enter your OpenAI API key: ")
# os.environ["OPENAI_BASE_URL"] = getpass.getpass("Please enter your OpenAI base URL: ")

# with open('tmp/output.txt', 'w') as f:
#     f.truncate(0)

# write_experiment_introduction(cfg)

# data_processing_agent(cfg)

write_final_report(cfg)