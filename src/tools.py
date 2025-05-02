import os
from langchain.agents import tool
from langchain_community.utilities import SerpAPIWrapper
import numpy as np
import pandas as pd

# search engine
@tool
def search(query: str) -> str:
    """
    Use this tool to access the search engine.
    The input is the query you want to search for.
    """
    search = SerpAPIWrapper()
    return search.run(query)

# data processing
@tool
def data_accessor() -> str:
    """
    Use this tool to access the dataframe.
    """
    df = pd.read_csv('data.csv', header=0, index_col=0)
    return df.to_string()

@tool
def data_processor(query: str) -> str:
    """
    Use this tool to process the dataframe.
    The input is a line of python code that will be executed on the dataframe.
    For example, you can use:
    df['column_name2'] = np.log(df['column_name1'])
    to create a new column in the dataframe.
    Do not type "" or '' around the code.
    The output will be the modified dataframe.
    If the input is not a valid python code, it will return an error message.
    """
    df = pd.read_csv('data.csv', header=0, index_col=0)
    print(f"Executing query: {query}")
    try:
        exec(query)
        df.to_csv('data.csv', header=True, index=True)
        return df.to_string()
    except Exception as e:
        return str(e)