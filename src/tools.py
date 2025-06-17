import os
import matplotlib.font_manager
from langchain.agents import tool, Tool
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib
import json
from matplotlib.table import Table

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

    matplotlib.use('Agg')  # Use non-interactive backend for plotting
    
    state = {"log": "", "figures": [], "tables": []}

    # data processor
    @tool
    def data_accessor(df_name: str) -> str:
        """
        View dataframe structures, only show header and first 3 rows. Input is name of a dataframe or 'all' to access all dataframes.
        Don't include quotes around the name.
        """
        print(f"Accessing dataframe: {df_name}")
        df_name = df_name.strip()
        if df_name == "all":
            all_data = "\n".join([f"{name}:\n{str(df[:3])}" for name, df in dfs.items()])
            return all_data
        elif df_name in dfs.keys():
            return str(dfs[df_name].head(3))
        else:
            return f"Invalid name. Name should be in {df_names} or 'all'."

    @tool
    def data_processor(query: str) -> str:
        """
        Process dataframe using a string of Python code.
        Each dataframe is a field in the `dfs` dictionary.
        For example: 
        `dfs['data']['log_col'] = np.log(dfs['data']['value']).round(2).
        Remember to limit the number of significant digits!
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
            return "Query executed successfully."
        except Exception as e:
            return f"Exception occurs: {str(e)}"

    def data_saver():
        processed_path = os.path.join(cfg.data_dir, "processed")
        os.makedirs(processed_path, exist_ok=True)
        for df_name in df_names:
            file_path = os.path.join(processed_path, f"{df_name}_processed.csv")
            dfs[df_name].to_csv(file_path, index=False)

    # Plot tool
    @tool()
    def plot_curve(query: str) -> str:
        """
        Plot a curve using two columns from a dataframe and save it as a PNG file.

        Parameters are in a dict format, with double quotes around the names:
        {
            "df_name": # name of the dataframe to use
            "x": # column name for the x-axis
            "y": # column name for the y-axis
            "title": # title of the plot
            "name": # name of the file (without extension)
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
            title = query_dict.get("title")
            name = query_dict.get("name")

            if df_name not in df_names:
                return f"Invalid dataframe name: {df_name}. Available dataframes are: {df_names}."

            if x not in dfs[df_name].columns or y not in dfs[df_name].columns:
                return f"Invalid column names: {x}, {y}. Please check the dataframe."
            
            plt.figure(figsize=(10, 6))
            plt.plot(dfs[df_name][x], dfs[df_name][y], marker='o')
            plt.xlabel(x)
            plt.ylabel(y, rotation=0)
            plt.title(title)
            plt.grid()

            os.makedirs('plots', exist_ok=True)
            file_path = os.path.join('plots', f"{name}.png")
            plt.savefig(file_path)
            plt.close()
            
            state['figures'].append(file_path)
            return f"Plot saved as {file_path}"
        except Exception as e:
            return f"Exception occurs: {str(e)}"
        
    @tool()
    def plot_least_squares(query: str) -> str:
        """
        Plot a least squares line using two columns from a dataframe and save it as a PNG file.

        Parameters are in a dict format, with double quotes around the names:
        {
            "df_name": # name of the dataframe to use
            "x": # column name for the x-axis
            "y": # column name for the y-axis
            "title": # title of the plot
            "name": # name of the file (without extension)
        }

        Returns:
        - Path of the saved plot image.
        - The slope and intercept of the least squares line. (you can use it to calculate other values)
        """
        try:
            query = query.strip()
            query_dict = json.loads(query)
            df_name = query_dict.get("df_name")
            x = query_dict.get("x")
            y = query_dict.get("y")
            title = query_dict.get("title")
            name = query_dict.get("name")

            if df_name not in df_names:
                return f"Invalid dataframe name: {df_name}. Available dataframes are: {df_names}."

            if x not in dfs[df_name].columns or y not in dfs[df_name].columns:
                return f"Invalid column names: {x}, {y}. Please check the dataframe."
            
            x_vals = dfs[df_name][x].values
            y_vals = dfs[df_name][y].values

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

            state['figures'].append(file_path)
            return f"Plot saved as {file_path}. Slope: {slope}, Intercept: {intercept}"
        
        except Exception as e:
            return f"Exception occurs: {str(e)}"

    # log writer
    @tool
    def write_log(content: str) -> str:
        """
        Write your log content here for experiment data processing
        """
        content = content.strip()
        state['log'] += content
        return "Log successfully written."

    def get_figures() -> str:
        return ", ".join(state['figures'])
    
    def get_log() -> str:
        print(f"Log content: {state['log']}")
        return state['log']

    def plot_tables():
        for df_name in df_names:
            plot_table(dfs[df_name], f"plots/{df_name}_table.png")
            state['tables'].append(f"plots/{df_name}_table.png")
        return ", ".join(state['tables'])

    def plot_table(df: pd.DataFrame, file_path: str):
        # Create figure with dynamic size based on DataFrame dimensions
        nrows, ncols = df.shape
        fig_height = max(4, nrows * 0.4)  # Minimum 4 inches, 0.4" per row
        fig_width = max(6, ncols * 1.2)   # Minimum 6 inches, 1.2" per column
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')
        
        # Prepare table data (include headers)
        cell_text = [df.columns.tolist()] + df.values.tolist()
        
        # Create table with auto-scaling
        table = ax.table(
            cellText=cell_text,
            loc='center',
            cellLoc='left',
            colLoc='left'
        )
        
        # Style adjustments
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)  # Scale row height
        
        # Header row styling
        for i in range(ncols):
            table[(0, i)].set_facecolor("#FFFFFF")
            table[(0, i)].set_text_props(color='black', weight='bold')
        
        # Alternate row coloring
        for i in range(1, len(cell_text)):
            color = "#f0f0f0" if i % 2 == 0 else '#ffffff'
            for j in range(ncols):
                table[(i, j)].set_facecolor(color)
        
        # Save and close
        plt.savefig(file_path, bbox_inches='tight', dpi=400)
        plt.close(fig)

    # latex writer
    # @tool
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
    
    tools = [data_accessor, data_processor, plot_curve, plot_least_squares, write_log]
    return tools, data_saver, get_figures, get_log, plot_tables, write_latex
