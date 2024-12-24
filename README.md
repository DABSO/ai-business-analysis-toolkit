# Business Analysis Toolkit

A collection of AI-powered business analysis tools demonstrating advanced Python development with LangGraph and LangChain. This toolkit helps automate common business development tasks through agentic workflows.

## 🚀 Features

### Competitor Research Generator
- Automated competitor identification and analysis
- Product and pricing analysis
- Comprehensive competitor profiling
- Revenue and employee data extraction
- Markdown and PDF report generation

### Market Research Generator
- Market trends analysis
- Customer segmentation
- Technology landscape assessment
- Legal compliance checking
- Structured report generation with data visualization

### SWOT Analysis Generator
- Automated SWOT matrix generation
- Industry-specific analysis
- Data-backed insights
- Visual report output

## 🛠 Technology Stack

- Python 3.8+
- LangGraph for workflow orchestration
- LangChain for LLM integration
- Streamlit for web interface
- ChromaDB for vector storage
- PyPuppeteer for web scraping

## 📋 Prerequisites

1. Python 3.8 or higher
2. Chromium browser
3. OpenAI API key
4. Serper API key 
5. ScraperAPI key 

## 🔧 Installation
1. Clone the repository:
```bash
git clone https://github.com/dabso/ai-business-analysis-toolkit.git
cd business-analysis-toolkit
```


2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Configure Chromium:

```bash
python -c "import os; os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1000027'; from pyppeteer import chromium_downloader; chromium_downloader.download_chromium()"
```


4. Set up environment variables:
```bash
cp .env.example .env
```
Edit .env with your API keys and configuration

## 🚦 Getting Started
There are multiple Streamlit Interfaces to interact with the apps
### Competition Research 
1. Start the Streamlit interface:
```bash
streamlit run competition_research_generator.py
```
2. Enter your business idea in the text area
3. Configure analysis parameters in the Advanced Settings panel
4. Click "Generate Report" to start the analysis
5. View and export results in various formats

### Business landscape Evaluation
1. Start the Streamlit interface: 
```bash
streamlit run business_landscape_research_generator.py
```
2. Enter your business idea in the text area
3. Click "Generate Report" to start the analysis
4. View Results

## 📁 Project Structure
├── agents/
│ ├── competitor_research/ # Competitor analysis workflows
│ ├── research/ # General research capabilities
│ └── business_landscape_research/ # Market analysis Research
├── utils/ 
├── tools/ 




