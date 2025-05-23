# Meeting 1

## Structure

* 摘要
* 实验原理
* 实验仪器及实验步骤
* 实验数据处理
* 分析讨论

## Input

* 指导书
* 题目，定制化要求
* 数据（csv*2）

## Implementation

* 将指导书分成dictionary（JSON）
* 题目，仪器及步骤交给一个agent，输出摘要，实验原理，实验仪器及实验步骤 agent1
* 一个agent处理数据，表格，图片，分析讨论
* 一个agent整合所有latex片段，成为可编译文件

## Interface

* agents 统一从yaml文件读取配置 (hydra)

```py
def function_name(cfg):
    pipeling(cfg.prompt, ...)
```

* 输出的latex片段，放到tmp/output.txt (append)，最后的agent读取整个文件并整理

## Abstraction

* `pdf_to_json(cfg)` in `src/book_agent.py`: parse pdf to json
* `get_text_by_title(cfg)` in `src/agent1.py`: get the corresponding text by the title of the experiment
* `write_experiment_introduction(cfg)` in `src/agent1.py`: write the experiment introduction