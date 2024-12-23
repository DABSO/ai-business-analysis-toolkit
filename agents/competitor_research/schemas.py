from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    name : Optional[str] = Field(..., description="The name of the product if mentioned.")
    price : Optional[float] = Field(..., description="The price of the product if mentioned.")
    billing_model : Optional[str] = Field(..., description="The billing model of the product if mentioned.")
    billing_period : Optional[str] = Field(..., description="The billing period of the product if mentioned.")
    features : list[str] = Field(..., description="The mentioned features of the product.")
    value_propositions : list[str] = Field(..., description="The mentioned value propositions of the product.")
    source_url : str = Field(..., description="The url of the source that contains the product information.")

class ProductList(BaseModel):
    analysis : str = Field(..., description="a field for analysing the search results critically to ensure that the actual products with the correct values are being extracted")
    products : list[Product] = Field(..., description="The list of products.")




class Competitor(TypedDict):
    name : str|None
    employees : int|None
    revenue_in_millions : float|None
    revenue_previous_year : float|None
    relevant_products : list[str]
    products : list[Product]
    official_website_domain : str|None
    product_sources : list[str]
    stat_sources : list[str]
    report : str
    competitor_relevance_score : int




class CompetitorOutput(BaseModel):
    summary : str = Field(..., description="A summary of the sources about the competitor in markdown format.")
    employees : Optional[int] = Field(..., description="The number of employees of the competitor.")
    official_website_domain : Optional[str] = Field(..., description="The domain of the official website of the competitor.")
    revenue_current_year_in_millions : Optional[float] = Field(..., description="The revenue of the competitor in the current year in millions.")
    revenue_previous_year_in_millions : Optional[float] = Field(..., description="The revenue of the competitor in the previous year in millions.")




class CompetitorState(TypedDict):
    competitor_name : str
    official_website_domain : str
    business_idea : str
    employees : int
    type : str 
    revenue_current_year_in_millions : float
    revenue_previous_year_in_millions : float
    queries : list[str]
    report : str
    stat_source_content : list[str|dict]
    stat_sources : list[str]
    product_source_content : list[str|dict]
    product_sources : list[str]
    
    report_sections_from_research : str
    products : list[Product]
    competitors : list[Competitor]
    num_stat_queries: int
    num_product_queries: int
    num_stat_results: int
    num_product_results: int

    num_stat_tokens_per_source: int
    num_product_tokens_per_source: int

class CompetitorStateOutput(TypedDict):
    competitors : list[Competitor]
    



class CompetitorNameList(BaseModel):
    competitors : List[str] = Field(..., description="The list of competitor names.")

class CompetitorReport(BaseModel):
    report : str = Field(..., description="The report about the competitor in markdown format.")
    value_propositions_similarity_score : int = Field(..., description="The similarity score between 1 and 10 of the value propositions of the competitor to the business idea.")
    features_similarity_score : int = Field(..., description="The similarity score between 1(not similar) and 10(very similar) of the features of the competitor to the business idea. ")
    goal_similarity_score : int = Field(..., description="The similarity score between 1(not similar) and 10(very similar) of the goal of the competitors solutions to the business idea.")

from typing import Annotated
import operator

class CompetitionState(TypedDict):

    competitors : Annotated[list, operator.add]
    competitor_names : list[str]
    executive_summary : str
    business_idea : str
    competition_search_results : list[str]
    num_competition_queries: int
    num_stat_queries: int
    num_product_queries: int

    num_competition_results: int
    num_stat_results: int
    num_product_results: int

    num_competition_tokens_per_source: int
    num_stat_tokens_per_source: int
    num_product_tokens_per_source: int

class CompetitionStateInput(TypedDict):
    business_idea : str
    num_competition_queries: int = 3
    num_stat_queries: int = 2
    num_product_queries: int = 2
    num_competition_results: int = 10
    num_stat_results: int = 3
    num_product_results: int = 2

    num_competition_tokens_per_source: int = 1000
    num_stat_tokens_per_source: int = 1000
    num_product_tokens_per_source: int = 1000

class CompetitionStateOutput(TypedDict):
    executive_summary : str
    competitors : list[Competitor]

class QueryGeneratorOutput(BaseModel):
    reasoning : str = Field(..., description="The reasoning behind the queries.")
    queries : list[str] = Field(..., description="The list of queries.")