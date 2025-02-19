from typing import Annotated, List, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator

from pydantic import BaseModel, Field
from typing import List, Optional


class Chart(BaseModel):
    id: str = Field(..., description="A unique identifier for the chart, used as a placeholder in the generated text.")
    title: str = Field(..., description="The title of the chart.")
    type: str = Field(..., description="The type of the chart, e.g., 'line', 'bar', 'scatter', 'histogram'.")
    x_data: List[float] = Field(..., description="The data for the x-axis.")
    y_data: List[float] = Field(..., description="The data for the y-axis.")
    x_label: str = Field(..., description="The label for the x-axis.")
    y_label: str = Field(..., description="The label for the y-axis.")
    color: Optional[str] = Field("blue", description="The color of the chart elements, e.g., 'blue', 'red'.")
    bins: Optional[int] = Field(None, description="The number of bins for histograms. Required if the chart type is 'histogram'.")

class Text(BaseModel):
    text : str = Field(..., description="The text of the section formatted in markdown.")


class SectionContent(BaseModel):
    subsections : List[Chart | Text] = Field(..., description="The subsections of the section.")

class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    research: bool = Field(
        description="Whether to perform web research for this section of the report."
    )
    content: str = Field(
        description="The content of the section."
    )   

class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the report.",
    )

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )

class ReportStateInput(TypedDict):
    topic: str  # Report topic

class ReportStateOutput(TypedDict):
    final_report: str  # Final report


class ReportState(TypedDict):
    topic: str  # Report topic    
    sections: list[Section]  # List of report sections 
    completed_sections: Annotated[list, operator.add]  # Send() API key
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    final_report: str  # Final report

class SectionState(TypedDict):
    section: Section  # Report section   
    search_queries: list[SearchQuery]  # List of search queries
    source_str: str  # String of formatted source content from web search
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    completed_sections: list[Section]  # Final key we duplicate in outer state for Send() API

class SectionOutputState(TypedDict):
    completed_sections: list[Section]  # Final key we duplicate in outer state for Send() API