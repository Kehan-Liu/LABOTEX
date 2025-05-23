from omegaconf import OmegaConf
from book_agent import pdf_to_json
from agent1 import get_text_by_title, write_experiment_introduction

cfg = OmegaConf.load('../config.yaml')

write_experiment_introduction(cfg)

