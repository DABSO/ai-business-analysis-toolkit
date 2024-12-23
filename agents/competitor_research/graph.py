
from .utils import load_prompt
from .schemas import CompetitorState, CompetitorStateOutput, CompetitionState, CompetitionStateInput, CompetitionStateOutput, CompetitorOutput, CompetitorNameList, ProductList, QueryGeneratorOutput, CompetitorReport
from langgraph.graph import START, END, StateGraph

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_core.runnables import RunnableConfig


from langgraph.constants import Send
from tools.tavily_search import  get_unique_urls
from tools.serper_search import serper_search_async, deduplicate_and_format_sources, get_unique_urls
import datetime

query_generator_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
report_writer_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def search_for_competitors(state : CompetitionState, config: RunnableConfig):
    print("search_for_competitors", state)

    print("num_competition_tokens_per_source", state["num_stat_tokens_per_source"])
    # load prompt
    query_generator_instructions = load_prompt('query_writer_instructions.txt')
    print("query_generator_instructions", query_generator_instructions[:100], "...")


    # get llm to search for competitors 
    structured_llm = query_generator_model.with_structured_output(QueryGeneratorOutput, method="json_schema")


    system_instructions_query = query_generator_instructions.format(
        business_idea=state["business_idea"],
        num_queries=state["num_competition_queries"]
    )

    # generate queries 
    output = structured_llm.invoke([
        SystemMessage(content=system_instructions_query),
        HumanMessage(content="Generate search queries that will help with researching competitors for the inputted service description.")
    ])
    

    queries = output.queries

    

    print("queries", queries)
    # execute queries 
    search_docs = await serper_search_async(queries, tavily_topic="general", max_results=state["num_competition_results"], include_images=False)
    print("--------------------------------")



    return {"competition_search_results": search_docs}


async def analyze_competitor_search_results(state : CompetitionState):
    print("analyze_competitor_search_results")
    # load prompt 
    analyze_competitor_search_results_prompt = load_prompt('analyze_competitor_search_results_instructions.txt')

    print("analyze_competitor_search_results_prompt", analyze_competitor_search_results_prompt[:100], "...")

    # format prompt 
    system_instructions_query = analyze_competitor_search_results_prompt.format(
        business_idea=state["business_idea"]
    )

    # get llm to analyze the search results 
    model_with_structured_output = report_writer_model.with_structured_output(CompetitorNameList, method="json_schema")

        # deduplicate and format sources 
    # group sources 
    sources_per_group = 10
    source_groups = [state["competition_search_results"][i:i+sources_per_group] for i in range(0, len(state["competition_search_results"]), sources_per_group)]

    competitors = set()
    for source_group in source_groups:
        sources = deduplicate_and_format_sources(source_group, max_tokens_per_source=state["num_competition_tokens_per_source"], include_raw_content=False)
    
        output = model_with_structured_output.invoke([
            SystemMessage(content=system_instructions_query),
            HumanMessage(content=[
                *sources,
                {
                    "type": "text",
                    "text": "Analyze the search results and return a list of potential competitor names."
                }
            ])
        ])

        competitors.update(output.competitors)
    
    competitors = list(competitors)
    print(competitors)
    print("--------------------------------")



    return {"competitor_names": competitors}


def initialize_competitor_research(state : CompetitionState):
    competitors = state["competitor_names"]

    print("stat_tokens_per_source", state["num_stat_tokens_per_source"])
    print("product_tokens_per_source", state["num_product_tokens_per_source"])
    return [
        Send("analyze_competitor", {
            "competitor_name": competitor, 
            "business_idea": state["business_idea"],
            "num_stat_queries": state["num_stat_queries"],
            "num_product_queries": state["num_product_queries"],
            "num_stat_results": state["num_stat_results"],
            "num_product_results": state["num_product_results"],
            "num_stat_tokens_per_source": state["num_stat_tokens_per_source"],
            "num_product_tokens_per_source": state["num_product_tokens_per_source"]
        })
        for competitor in competitors
    ] 

async def search_for_competitor_stats(state : CompetitorState):
    print("search_for_competitor_stats", state)
    # get prompt
    # format prompt 

    search_for_competitor_stats_prompt = load_prompt('search_for_competitor_stats_instructions.txt')
    

    system_instructions = search_for_competitor_stats_prompt.format(
        competitor_name=state["competitor_name"],

        num_queries=state["num_stat_queries"],
        current_date=datetime.datetime.now().strftime("%Y-%m-%d")
    )

    llm_with_structured_output = report_writer_model.with_structured_output(QueryGeneratorOutput, method="json_schema")

    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries that will help with researching competitors for the inputted service description.")
    ])

    queries = output.queries
    print(queries)
    print("--------------------------------")
    # execute queries 
    search_docs = await serper_search_async(queries, tavily_topic="general", max_results=state["num_stat_results"])

    # deduplicate and format sources 
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=state["num_stat_tokens_per_source"], include_raw_content=False)

    return {"stat_source_content": source_str, "stat_sources": get_unique_urls(search_docs) }


async def analyze_competitor_stats_search_results(state : CompetitorState):
    # get prompt
    print("analyze_competitor_stats_search_results")
    analyze_competitor_stats_search_results_prompt = load_prompt('analyze_competitor_stats_search_results_instructions.txt')

    # format prompt 
    system_instructions = analyze_competitor_stats_search_results_prompt.format(
        competitor_name=state["competitor_name"],
        
        current_date=datetime.datetime.now().strftime("%Y-%m-%d")
    )

    # get llm to analyze the search results 
    model_with_structured_output = report_writer_model.with_structured_output(CompetitorOutput, method="json_schema")

    output = model_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content=[
            *state["stat_source_content"],
            {
                "type": "text",
                "text": "Analyze the search results and extract the relevant information about the competitor."
            }
        ])
    ])

    name = state["competitor_name"]
    summary = output.summary
    employees = output.employees
    revenue_in_millions = output.revenue_current_year_in_millions
    revenue_previous_year = output.revenue_previous_year_in_millions
    official_website_domain = output.official_website_domain
    
    print(name)
    print(summary)
    print(employees)
    print(revenue_in_millions)
    print(revenue_previous_year)
    print(official_website_domain)

    print("--------------------------------")

    return { "employees": employees, "revenue_current_year_in_millions": revenue_in_millions, "revenue_previous_year_in_millions": revenue_previous_year, "official_website_domain": official_website_domain}
    

    

async def search_for_competitor_products(state : CompetitorState):
    print("search_for_competitor_products")
    # load prompt 
    search_for_competitor_products_prompt = load_prompt('search_for_competitor_products_instructions.txt')
    #
    system_instructions = search_for_competitor_products_prompt.format(
        competitor_name=state["competitor_name"],
        business_idea=state["business_idea"],
        num_queries=state["num_product_queries"]
    )

    # get llm to search for competitor products 
    llm_with_structured_output = report_writer_model.with_structured_output(QueryGeneratorOutput, method="json_schema")

    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries that will help with researching competitors for the inputted business idea.")
    ])

    queries = output.queries
    print(queries)
    print("----")

    # execute queries 
    search_docs = await serper_search_async(queries, tavily_topic="general", max_results=state["num_product_results"])

    # deduplicate and format sources 
    source_str = deduplicate_and_format_sources(search_docs, max_tokens_per_source=state["num_product_tokens_per_source"], include_raw_content=False)
    print("length of source_str", len(source_str))
    return {"product_source_content": source_str, "product_sources": get_unique_urls(search_docs)}

async def analyze_competitor_products_search_results(state : CompetitorState):
    print("analyze_competitor_products_search_results", len(state["product_source_content"]))
    print("<product_source_content>", state["product_source_content"], "</product_source_content>")

    # load prompt 
    analyze_competitor_products_search_results_prompt = load_prompt('analyze_competitor_products_search_results_instructions.txt')
# analyze the sources 
    llm_with_structured_output = report_writer_model.with_structured_output(ProductList, method="json_schema")
    # format prompt 
    system_instructions = analyze_competitor_products_search_results_prompt.format(
      
        competitor_name=state["competitor_name"],
        business_idea=state["business_idea"]
    )

    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content=[
            *state["product_source_content"],
            {
                "type": "text",
                "text": "Analyze the search results and extract the relevant information about the competitor."
            }
        ])
    ])

    print(output)

    products = output.products

    print("--------------------------------")

    return {"products": [products]}











def write_competitor_report(state: CompetitorState):
    print("write_competitor_report")

    # write report 
    write_competitor_report_prompt = load_prompt('write_competitor_report_instructions.txt')

    # format prompt 
    system_instructions = write_competitor_report_prompt.format(
        business_idea=state["business_idea"],
        name=state["competitor_name"],
        employees=state["employees"],
        revenue_current_year_in_millions=state["revenue_current_year_in_millions"],
        revenue_previous_year_in_millions=state["revenue_previous_year_in_millions"],
        products=state["products"]   

        
    )

    # get llm to write the report 
    llm_with_structured_output = report_writer_model.with_structured_output(CompetitorReport, method="json_schema")
    output = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content=[
            *state["product_source_content"],
            {
                "type": "text",
                "text": "Write a report about the competitor in markdown."
            }
        ])
    ])

    report = output.report

    # Create competitor dict BEFORE using it
    competitor = {
        "name": state["competitor_name"],
        "employees": state["employees"],
        "revenue_current_year_in_millions": state["revenue_current_year_in_millions"],
        "revenue_previous_year_in_millions": state["revenue_previous_year_in_millions"],
        "products": state["products"],
        "official_website_domain": state["official_website_domain"],
        "product_sources": state["product_sources"],
        "stat_sources": state["stat_sources"],
        "report": report  # Add report here instead of trying to add it to undefined variable
    }
    
    print("--------------------------------")
    return {"competitors": [competitor]}

def aggregate_competitors(state : CompetitionState):

    return {}

def get_competitor_research_graph():
    builder = StateGraph(
        CompetitorState, 
        output=CompetitorStateOutput, 
    )

    builder.add_node("search_for_competitor_stats", search_for_competitor_stats)
    builder.add_node("analyze_competitor_stats_search_results", analyze_competitor_stats_search_results)
    builder.add_node("search_for_competitor_products", search_for_competitor_products)
    builder.add_node("analyze_competitor_products_search_results", analyze_competitor_products_search_results)
    builder.add_node("write_competitor_report", write_competitor_report)
    

    builder.add_edge(START, "search_for_competitor_stats")
    builder.add_edge("search_for_competitor_stats", "analyze_competitor_stats_search_results")
    builder.add_edge("analyze_competitor_stats_search_results", "search_for_competitor_products")
    builder.add_edge("search_for_competitor_products","analyze_competitor_products_search_results")
    builder.add_edge("analyze_competitor_products_search_results","write_competitor_report")
    builder.add_edge("write_competitor_report", END)

    return builder.compile()

def get_competition_research_graph():
    builder = StateGraph(
        CompetitionState, 
        input=CompetitionStateInput, 
        output=CompetitionStateOutput, 
    )



    builder.add_node("search_for_competitors", search_for_competitors)
    builder.add_node("analyze_competitor_search_results", analyze_competitor_search_results)
    builder.add_node("analyze_competitor", get_competitor_research_graph())
    builder.add_node("aggregate_competitors", aggregate_competitors)
    

    builder.add_edge(START, "search_for_competitors")
    builder.add_edge("search_for_competitors", "analyze_competitor_search_results")
    builder.add_conditional_edges("analyze_competitor_search_results", initialize_competitor_research  ,["analyze_competitor"])
    builder.add_edge("analyze_competitor", "aggregate_competitors")
    builder.add_edge("aggregate_competitors", END)

    

    return builder.compile()
