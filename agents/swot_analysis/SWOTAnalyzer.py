from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from tools.serper_search import serper_search_async
from .utils import load_prompt
from typing import List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import pandas as pd




query_generator_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
report_writer_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class SWOTState(BaseModel):
    competitor_name : str = Field(..., description="The name of the competitor.")
    reviews : pd.DataFrame = Field(..., description="The reviews of the competitor.")
    strengths : List[str] = Field(..., description="The strengths of the competitor.")
    weaknesses : List[str] = Field(..., description="The weaknesses of the competitor.")
    opportunities : List[str] = Field(..., description="The opportunities of the competitor.")
    threats : List[str] = Field(..., description="The threats of the competitor.")
    report : str = Field(..., description="The report of the competitor.")


async def perform_swot_analysis(state : SWOTState):

    # decide if we should scrape trustpilot or google reviews
    prompt = load_prompt('decide_if_we_should_scrape_trustpilot_or_google_reviews_instructions.txt')
    system_instructions = prompt.format(
        competitor_name=state["competitor_name"],
        report=state["report"]
    )
    class CompetitorType(BaseModel):
        analysis : str = Field(..., description="The analysis of the competitor based on the criteria.")
        review_source : str = Field(..., description="The source of the reviews, either trustpilot or google reviews.", choices=["trustpilot", "google reviews"])
    llm_with_structured_output = report_writer_model.with_structured_output(CompetitorType, method="json_schema")
    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Analyze the report and decide if we should scrape trustpilot or google reviews.")
    ])
    reviews = []
    if output.review_source == "trustpilot":
        reviews = await scrape_trustpilot_reviews(state)
       

        # scrape trustpilot reviews to csv 
    elif output.review_source == "google reviews":
        # search for google reviews 
        query = f"google reviews {state['competitor_name']}"
        search_docs = await serper_search_async(query, tavily_topic="general", max_results=10)

        # scrape google reviews to csv 
        scrape_google_reviews(output.google_reviews_link)
    else:
        return {"swot_analysis": "Error during swot analysis generation"}
    


    # analyze wether the competitor has a trustpilot site


    # scrape trustpilot reviews to csv 


    # analyze positive reviews 

    # analyze negative reviews 



    # write swot analysis 
    return {}

async def scrape_trustpilot_reviews(state : SWOTState):
     # search for trustpilot reviews 
    query = f"trustpilot {state['competitor_name']}"
    search_docs = await serper_search_async(query, tavily_topic="general", max_results=8)

    class CheckTrustpilotSearchResultsOutput(BaseModel):
        analysis : str = Field(..., description="The analysis of the search results to determine if the site is from the competitor. based on the information in the search results.")
        has_trustpilot_site : bool = Field(..., description="Whether the competitor has a trustpilot site.")
        trustpilot_link : str = Field(..., description="The link to the trustpilot site of the competitor.")

    prompt = load_prompt('check_trustpilot_search_results_instructions.txt')
    system_instructions = prompt.format(
        competitor_name=state["competitor_name"],
        report=state["report"]
    )


    llm_with_structured_output = report_writer_model.with_structured_output(CheckTrustpilotSearchResultsOutput, method="json_schema")
    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Analyze the search results and determine if there is a trustpilot site and if it is from the competitor.")
    ])

async def scrape_google_reviews(state : SWOTState):
    # search for google reviews 
    query = f"google reviews {state['competitor_name']}"
    search_docs = await serper_search_async(query, tavily_topic="general", max_results=10)

    prompt = load_prompt('check_google_reviews_search_results_instructions.txt')
    system_instructions = prompt.format(
        competitor_name=state["competitor_name"],
        report=state["report"]
    )

    class CheckGoogleReviewsSearchResultsOutput(BaseModel):
        analysis : str = Field(..., description="The analysis of the search results to determine if the site is from the competitor. based on the information in the search results.")
        has_google_reviews_site : bool = Field(..., description="Whether the competitor has a google reviews site.")
        google_reviews_link : str = Field(..., description="The link to the google reviews site of the competitor.")


    llm_with_structured_output = report_writer_model.with_structured_output(CheckGoogleReviewsSearchResultsOutput, method="json_schema")

    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Analyze the search results and determine if there is a google reviews site and if it is from the competitor.")
    ])

    # scrape google reviews to csv 
    scrape_google_reviews(output.google_reviews_link)

def decide_source_of_reviews(state : SWOTState):
    # decide if we should scrape trustpilot or google reviews
    prompt = load_prompt('decide_if_we_should_scrape_trustpilot_or_google_reviews_instructions.txt')
    system_instructions = prompt.format(
        competitor_name=state["competitor_name"],
        report=state["report"]
    )
    pass 

def analyze_positive_reviews(state : SWOTState):
    pass 

def analyze_negative_reviews(state : SWOTState):
    pass 

def analyze_opportunities(state : SWOTState):
    pass 

def analyze_threats(state : SWOTState):
    pass

def write_swot_analysis(state : SWOTState):
    pass 



def get_swot_analysis_graph():
    graph = StateGraph(SWOTState)
    graph.add_node("decide_source_of_reviews", decide_source_of_reviews)
    graph.add_node("scrape_trustpilot_reviews", scrape_trustpilot_reviews)
    graph.add_node("scrape_google_reviews", scrape_google_reviews)
    graph.add_node("analyze_positive_reviews", analyze_positive_reviews)
    graph.add_node("analyze_negative_reviews", analyze_negative_reviews)
    graph.add_node("analyze_opportunities", analyze_opportunities)
    graph.add_node("analyze_threats", analyze_threats)
    graph.add_node("write_swot_analysis", write_swot_analysis)


    graph.add_edge(START, "decide_source_of_reviews")
    graph.add_conditional_edges(
        "decide_source_of_reviews",
        {
            "scrape_trustpilot_reviews": lambda state: state["source_of_reviews"] == "trustpilot",
            "scrape_google_reviews": lambda state: state["source_of_reviews"] == "google reviews",
        }
    )


    graph.add_edge("scrape_trustpilot_reviews", "analyze_positive_reviews")
    graph.add_edge("scrape_trustpilot_reviews", "analyze_negative_reviews")
    graph.add_edge("scrape_trustpilot_reviews", "analyze_opportunities")
    graph.add_edge("scrape_trustpilot_reviews", "analyze_threats")
    

    graph.add_edge("scrape_google_reviews", "analyze_positive_reviews")
    graph.add_edge("scrape_google_reviews", "analyze_negative_reviews")
    graph.add_edge("scrape_google_reviews", "analyze_opportunities")
    graph.add_edge("scrape_google_reviews", "analyze_threats")

    graph.add_edge("analyze_threats", "write_swot_analysis")
    graph.add_edge("analyze_opportunities", "write_swot_analysis")
    
    return graph