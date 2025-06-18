# ***Labotex***
***Labotex*** is an intelligent lab assistant designed to help researchers generate lab reports in LaTeX format in a simple and efficient way.
## Main Description
The model utilizes 4 agents:
1. **Book Reading Agent** `book_agent.py`: This agent is designed to convert PDF experiment instruction books into structured JSON data using visual language models (VLMs). It is able to identify section breaks, read image content and extract text in JSON format.
2. **Introduction Agent** `agent1.py`: This agent creates the introduction sections of the lab report by extracting relevant experiment information from the JSON book data. Specifically, it generates 3 LaTeX sections including "Abstract", "Experimental Principles", and "Equipment & Procedures". Also, it summarizes the data processing tasks from the experiment text.
3. **Data Processing Agent** `agent2.py`: This agent processes the experimental data and generates figures, plots, and tables by analyzing provided CSV files. Then, it creates the "Experimental Data Processing" and "Analysis & Discussion" LaTeX sections.
4. **Report Generation Agent** `agent3.py`: This agent combines all sections above to generate a complete lab report in LaTeX format. Then, it compiles it into a PDF using xelatex, and moves the final PDF to the directory `final_pdf`.

By utilizing these 4 agents, ***Labotex*** provides a Web UI through `main.py` for users to upload their experiment instruction books and CSV files, and then generates a complete lab report in LaTeX format with minimal user input.

## Using Procedure
In order to use ***Labotex***, follow these steps:
### I. Environment Setup
After cloning the repository, create a virtual environment and install the required packages:
```bash
conda create -n labotex python=3.10
conda activate labotex
pip install -r requirements.txt
```
You might need to install `poppler` in addition for PDF processing.

**Ubuntu/Debian users** can install it with:
```bash
sudo apt-get install poppler-utils
```

And **Mac users** can install it with Homebrew:
```bash
brew install poppler
```

### II. Running the Application
Navigate to the root of the repository and run:
   ```bash
   python -m src/main.py
   ```
   Then, the url for the web interface will be displayed in the terminal, you can **open it in your web browser** to access the Labotex interface.
Upon opening the web interface, you will see 2 options: *Add New Instruction Book* and *Write Reports*. You can click on either to proceed to the respective functionalities.

### III. Add New Instruction Book
Use the web interface to upload your experiment instruction book in PDF format. Here, you have to specify:
- **Book Name**: The name of the directory where the book will be stored.
- **Vision Language Model Name**: The name of the VLM to be used for processing the book. Here, we recommend **qwen2.5-vl-72b-instruct** for users who have access to **infini-ai**.
- **API Key**: The API key for the VLM service.
- **Base URL**: The base URL for the VLM service. For users using **infini-ai**, it is `https://cloud.infini-ai.com/maas/v1/`.
- Also, you have to upload the PDF file of the experiment instruction book.

If the book is successfully processed, it will be stored in the `books` directory in JSON format, and the web interface will display a message `Book Successfully Loaded!`; Unless, it will display a message `Failed to Load the Book.` and the specific error message.

### IV. Write Reports
Use the web interface to write reports by uploading the CSV files containing experimental data. Here, you have to specify:
- **Reference Book Name**: The name of the directory where the relevant book is stored.
- **Title of the Report**: The title of the lab report, which will be used to locate the relevant content in the book.
- **Chat Model Name**: The name of the chat model to be used for generating the report. Here, we recommend **deepseek-v3** for users who have access to **infini-ai**.
- **Description of Your CSV Files**: A brief description of the CSV files you are uploading, which will help the model understand the context of the data. ***You need to specify the experiment and what is in each CSV file.***
- **API Key**: The API key for the chat model service.
- **Base URL**: The base URL for the chat model service. For users using **infini-ai**, it is `https://cloud.infini-ai.com/maas/v1/`.
- Also, you have to upload the CSV files containing experimental data.

If the report is successfully generated, it will be stored in the `final_pdf` directory in PDF format, and the web interface will display a message `Report Successfully Generated!`. Also, the LaTeX source code will be stored in the `LABOTEX` directory.

### Have Fun!