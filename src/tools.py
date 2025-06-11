import os
import matplotlib.font_manager
from langchain.agents import tool, Tool
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Union
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
from matplotlib.font_manager import FontProperties
import matplotlib
import json

# data processing
def data_tool_factory(cfg):
    
    csv_files = [f for f in os.listdir(cfg.data_dir) if f.endswith('.csv')]
    df_names = [f[:-4] for f in csv_files]  # Remove '.csv' extension for names
    dfs = {}
    for i, file in enumerate(csv_files):
        file_path = os.path.join(cfg.data_dir, file)
        df = pd.read_csv(file_path)
        dfs[df_names[i]] = df

    matplotlib.font_manager.fontManager.addfont("NotoSerifSC-Regular.ttf")
    matplotlib.rcParams['font.family'] = 'sans-serif'
    font_prop = FontProperties(fname="NotoSerifSC-Regular.ttf")
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    figures = []

    # data processor
    @tool
    def data_accessor(df_name: str) -> str:
        """
        Access dataframe content. Input is name of a dataframe or 'all' to access all dataframes.
        Don't include quotes around the name.
        """
        print(f"Accessing dataframe: {df_name}")
        df_name = df_name.strip()
        if df_name == "all":
            all_data = "\n".join([f"{name}:\n{df.to_string()}" for name, df in dfs.items()])
            return all_data
        elif df_name in dfs.keys():
            return dfs[df_name].to_string()
        else:
            return f"Invalid name. Name should be in {df_names} or 'all'."

    @tool
    def data_processor(query: str) -> str:
        """
        Process dataframe using a string of Python code.
        Each dataframe is a field in the `dfs` dictionary.
        For example: 
        `dfs['data']['log_col'] = np.log(dfs['data']['value'])`. 
        Don't include quotes around the code.
        """
        query = query.strip()
        print(f"Executing query: {query}")
        local_vars = {
            "dfs": dfs,
            "np": np,
            "pd": pd,
        }
        try:
            exec(query, {}, local_vars)
        except Exception as e:
            return f"Exception occurs: {str(e)}"

    # @tool
    # def data_saver(name: str) -> str:
    #     """
    #     Save dataframe to CSV. Input: 'single_data', 'multi_data', or 'all'.
    #     Don't include quotes around the name.
    #     """
    #     name = name.strip()
    #     if name == "single_data":
    #         single_data.to_csv(processed_single_data_path, header=True, index=False)
    #         return "Single data saved"
    #     elif name == "multi_data":
    #         multi_data.to_csv(processed_multi_data_path, header=True, index=True)
    #         return "Multi data saved"
    #     elif name == "all":
    #         single_data.to_csv(processed_single_data_path, header=True, index=False)
    #         multi_data.to_csv(processed_multi_data_path, header=True, index=True)
    #         return "All data saved"
    #     else:
    #         return "Invalid name. Please use 'single', 'multi' or 'all'."

    # Plot tool
    @tool()
    def plot_curve(query: str) -> str:
        """
        Plot a curve using two columns from a dataframe and save it as a PNG file.
        Don't include quotes around names.

        Parameters:
        - df_name: name of the dataframe to use
        - x: column name for the x-axis
        - y: column name for the y-axis
        - index: list of row indices
        - title: title of the plot
        - name: name of the file (without extension)

        Parameters are in a dict format, with no quotes around the names:
        {
            "df_name":
            "x":
            "y":
            "index":
            "title":
            "name":
        }

        Returns:
        - Path of the saved plot image.
        """
        try:
            query = query.strip()
            query_dict = json.loads(query)
            df_name = query_dict.get("df_name")
            x = query_dict.get("x")
            y = query_dict.get("y")
            index = query_dict.get("index")
            title = query_dict.get("title")
            name = query_dict.get("name")

            if df_name not in df_names:
                return f"Invalid dataframe name: {df_name}. Available dataframes are: {df_names}."

            if x not in dfs[df_name].columns or y not in dfs[df_name].columns:
                return f"Invalid column names: {x}, {y}. Please check the dataframe."
            if isinstance(index, list):
                subset = dfs[df_name].loc[index]
            elif isinstance(index, tuple) and len(index) == 2:
                subset = dfs[df_name].iloc[index[0]:index[1]]
            else:
                return "Invalid index. Please provide a list of indices or a tuple of start and end indices."
            
            plt.figure(figsize=(10, 6))
            plt.plot(subset[x], subset[y], marker='o')
            plt.xlabel(x)
            plt.ylabel(y, rotation=0)
            plt.title(title)
            plt.grid()

            os.makedirs('plots', exist_ok=True)
            file_path = os.path.join('plots', f"{name}.png")
            plt.savefig(file_path)
            plt.close()
            
            figures.append(file_path)
            return f"Plot saved as {file_path}"
        except Exception as e:
            return f"Exception occurs: {str(e)}"
        
    @tool()
    def plot_least_squares(query: str) -> str:
        """
        Plot a least squares line using two columns from the 'multi_data' dataframe and save it as a PNG file.
        Don't include quotes around names.

        Parameters:
        - df_name: name of the dataframe to use
        - x: column name for the x-axis
        - y: column name for the y-axis
        - index: list of row indices
        - title: title of the plot
        - name: name of the file (without extension)

        Parameters are in a dict format, with no quotes around the names:
        {
            "df_name":
            "x":
            "y":
            "index":
            "title":
            "name":
        }

        Returns:
        - The slope and intercept of the least squares line. (you can use it to calculate other values)
        """
        try:
            query = query.strip()
            query_dict = json.loads(query)
            df_name = query_dict.get("df_name")
            x = query_dict.get("x")
            y = query_dict.get("y")
            index = query_dict.get("index")
            title = query_dict.get("title")
            name = query_dict.get("name")

            if df_name not in df_names:
                return f"Invalid dataframe name: {df_name}. Available dataframes are: {df_names}."

            if x not in dfs[df_name].columns or y not in dfs[df_name].columns:
                return f"Invalid column names: {x}, {y}. Please check the dataframe."
            if isinstance(index, list):
                subset = dfs[df_name].loc[index]
            elif isinstance(index, tuple) and len(index) == 2:
                subset = dfs[df_name].iloc[index[0]:index[1]]
            else:
                return "Invalid index. Please provide a list of indices or a tuple of start and end indices."
            
            x_vals = subset[x].values
            y_vals = subset[y].values

            slope, intercept = np.polyfit(x_vals, y_vals, deg=1)
            x_min, x_max = x_vals.min(), x_vals.max()
            x_range = x_max - x_min
            x_line = np.linspace(x_min - 0.1 * x_range, x_max + 0.1 * x_range, 100)
            y_line = slope * x_line + intercept

            plt.figure(figsize=(10, 6))
            plt.plot(x_vals, y_vals, 'o')
            plt.plot(x_line, y_line, 'r-')
            plt.xlabel(x)
            plt.ylabel(y, rotation=0)
            plt.title(title)
            plt.grid()

            os.makedirs('plots', exist_ok=True)
            file_path = os.path.join('plots', f"{name}.png")
            plt.savefig(file_path)
            plt.close()

            figures.append(file_path)
            return f"Plot saved as {file_path}. Slope: {slope}, Intercept: {intercept}"
        
        except Exception as e:
            return f"Exception occurs: {str(e)}"
        
    @tool
    def get_figures() -> str:
        """
        Get the list of figures saved.
        """
        if not figures:
            return "No figures saved."
        return "\n".join(figures)
    
    tools = [data_accessor, data_processor, plot_curve, plot_least_squares, get_figures]
    return tools

# latex writer
@tool
def write_latex(content: str) -> str:
    """
    Write you LaTeX code here for the experiment report, including tables of raw data and figures.
    Only include part of the code corresponding to the sections you need to write.
    Don't use quotes around the code.
    Format:

    \section{实验数据处理}
    your code
    \section{分析讨论}
    your code
    """
    os.makedirs("tmp", exist_ok=True)
    with open("tmp/output.txt", "a") as f:
        f.write(content + "\n")
    return "Content successfully written! Your job is done."