import asyncio
import operator
import os
from typing import Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI   
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph

from .utils import format_sections


from .schemas import (
    ReportState,
    ReportStateInput,
    ReportStateOutput,
    SectionState,
    SectionOutputState,
    Section,
    Queries,
    Sections
)
from .config import Configuration, DEFAULT_REPORT_STRUCTURE


from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
from tools.tavily_search import tavily_search_async, deduplicate_and_format_sources

# ------------------------------------------------------------
# LLMs 

report_planner_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
report_writer_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ------------------------------------------------------------
# Search



# ------------------------------------------------------------
# Utility function for loading prompts

def load_prompt(file_name: str) -> str:
    """Load prompt text from a file."""
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', file_name)
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()

# Load all prompts
report_planner_query_writer_instructions = load_prompt('report_planner_query_writer_instructions.txt')
report_planner_instructions = load_prompt('report_planner_instructions.txt')
query_writer_instructions = load_prompt('query_writer_instructions.txt')
section_writer_instructions = load_prompt('section_writer_instructions.txt')
final_section_writer_instructions = load_prompt('final_section_writer_instructions.txt')

# ------------------------------------------------------------
# Prompts are now loaded from external .txt files

# ------------------------------------------------------------
# Define Utility functions (assumed to be in utils.py)

# Skipped for brevity

# ------------------------------------------------------------
# Define Graph Nodes and Workflow

def log_function_call(func_name: str, **kwargs):
    """Helper to log function calls with parameters"""
    params_str = ', '.join(f'{k}={v}' for k, v in kwargs.items())
    logger.info(f"Executing {func_name} with params: {params_str}")



async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """Generate the report plan"""
    log_function_call("generate_report_plan", topic=state['topic'], config=config)
    
    # Inputs
    topic = state["topic"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries
    tavily_topic = configurable.tavily_topic
    tavily_days = configurable.tavily_days

    # Convert JSON object to string if necessary
    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    # Generate search query
    structured_llm = report_planner_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic, 
        report_organization=report_structure, 
        number_of_queries=number_of_queries
    )

    # Generate queries  
    results = structured_llm.invoke([
        SystemMessage(content=system_instructions_query),
        HumanMessage(content="Generate search queries that will help with planning the sections of the report.")
    ])

    # Web search
    query_list = [query.search_query for query in results.queries]

    # Search web 
    search_docs = await tavily_search_async(query_list, tavily_topic, tavily_days)

    # Deduplicate and format sources
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=1000, include_raw_content=False)

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(
        topic=topic, 
        report_organization=report_structure, 
        context=source_str
    )

    # Generate sections 
    structured_llm = report_planner_model.with_structured_output(Sections)
    report_sections = structured_llm.invoke([
        SystemMessage(content=system_instructions_sections),
        HumanMessage(content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields.")
    ])

    return {"sections": report_sections.sections}

def generate_queries(state: SectionState, config: RunnableConfig):
    """Generate search queries for a report section"""
    log_function_call(
        "generate_queries", 
        section_name=state['section'].name,
        section_description=state['section'].description,
        config=config
    )
    
    # Get state 
    section = state["section"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Generate queries 
    structured_llm = report_writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(
        section_topic=section.description, 
        number_of_queries=number_of_queries
    )

    # Generate queries  
    queries = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate goal oriented search queries on the provided topic.")
    ])

    return {"search_queries": queries.queries}

async def search_web(state: SectionState, config: RunnableConfig):
    """Search the web for each query"""
    log_function_call(
        "search_web", 
        queries=[q.search_query for q in state['search_queries']],
        config=config
    )
    
    # Get state 
    search_queries = state["search_queries"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    tavily_topic = configurable.tavily_topic
    tavily_days = configurable.tavily_days

    # Web search
    query_list = [query.search_query for query in search_queries]
    search_docs = await tavily_search_async(query_list, tavily_topic, tavily_days)

    # Deduplicate and format sources
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=5000, include_raw_content=True)

    return {"source_str": source_str}

def write_section(state: SectionState):
    """Write a section of the report"""
    log_function_call(
        "write_section",
        section_name=state['section'].name,
        has_source_str=bool(state['source_str'])
    )
    
    # Get state 
    section = state["section"]
    source_str = state["source_str"]

    # Format system instructions
    system_instructions = section_writer_instructions.format(
        section_topic=section.description, 
        context=source_str
    )

    # Generate section  
    section_content = report_planner_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    
    # Write content to the section object  
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def write_final_sections(state: SectionState):
    """Write final sections of the report"""
    log_function_call(
        "write_final_sections",
        section_name=state['section'].name,
        has_research_content=bool(state['report_sections_from_research'])
    )
    
    # Get state 
    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]

    # Format system instructions
    system_instructions = final_section_writer_instructions.format(
        section_topic=section.description, 
        context=completed_report_sections
    )

    # Generate section  
    section_content = report_planner_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    
    # Write content to section 
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def gather_completed_sections(state: ReportState):
    """Gather completed sections"""
    completed = [s.name for s in state["completed_sections"]]
    logger.info(f"Gathering completed sections: {completed}")
    
    # List of completed sections
    completed_sections = state["completed_sections"]

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"report_sections_from_research": completed_report_sections}

def initiate_section_writing(state: ReportState):
    """Map step for web research sections"""
    research_sections = [s for s in state["sections"] if s.research]
    logger.info(f"Initiating section writing for research sections: {[s.name for s in research_sections]}")
    
    # Kick off section writing in parallel via Send() API for any sections that require research
    return [
        Send("build_section_with_web_research", {"section": s}) 
        for s in research_sections
    ]

def initiate_final_section_writing(state: ReportState):
    """Initiate writing of final sections"""
    non_research_sections = [s for s in state["sections"] if not s.research]
    logger.info(f"Initiating final section writing for: {[s.name for s in non_research_sections]}")
    
    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send("write_final_sections", {"section": s, "report_sections_from_research": state["report_sections_from_research"]}) 
        for s in non_research_sections
    ]

def compile_final_report(state: ReportState):
    """Compile the final report"""
    log_function_call(
        "compile_final_report",
        num_sections=len(state['sections']),
        num_completed=len(state['completed_sections'])
    )
    
    # Get sections
    sections = state["sections"]
    completed_sections = {s.name: s.content for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section.content = completed_sections.get(section.name, section.content)

    # Compile final report
    all_sections = "\n\n".join([s.content for s in sections])

    return {"final_report": all_sections}

# ------------------------------------------------------------
# Build Section Graph
# instantiate the StateGraph
section_builder = StateGraph(SectionState, output=SectionOutputState)

# Add nodes
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

# Add edges for flow control

section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")
section_builder.add_edge("write_section", END)

# ------------------------------------------------------------
# Build Main Report Graph

from .schemas import ReportStateInput, ReportStateOutput

def build_report_graph():
    """Build the main report state graph"""
    builder = StateGraph(
        ReportState, 
        input=ReportStateInput, 
        output=ReportStateOutput, 
        config_schema=Configuration
    )


    builder.add_node("generate_report_plan", generate_report_plan)
    builder.add_node("build_section_with_web_research", section_builder.compile())
    builder.add_node("gather_completed_sections", gather_completed_sections)
    builder.add_node("write_final_sections", write_final_sections)
    builder.add_node("compile_final_report", compile_final_report)
    
    builder.add_edge(START, "generate_report_plan")
    builder.add_conditional_edges("generate_report_plan", initiate_section_writing, ["build_section_with_web_research"])
    builder.add_edge("build_section_with_web_research", "gather_completed_sections")
    builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
    builder.add_edge("write_final_sections", "compile_final_report")
    builder.add_edge("compile_final_report", END)
    
    return builder.compile()

graph = build_report_graph()

try:
    png = graph.get_graph().draw_mermaid_png()
    with open("report_graph.png", "wb") as f:
        f.write(png)
except Exception as e:
    logger.warning(f"Unable to generate graph image: {e}")