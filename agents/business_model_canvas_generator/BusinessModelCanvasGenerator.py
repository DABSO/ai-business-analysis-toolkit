from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from .utils import load_prompt
from langchain_openai import ChatOpenAI



from typing import List, Optional
from pydantic import BaseModel

from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from langchain_core.messages import SystemMessage, HumanMessage

class BusinessModelType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    B2B2C = "B2B2C"
    Hybrid = "Hybrid"
    D2C = "D2C"
    B2A = "B2A"

class AgeRange(str, Enum):
    Children = "Children"
    Teenagers = "Teenagers"
    YoungAdults = "Young Adults"
    Adults = "Adults"
    Boomers = "Boomers"
    Seniors = "Seniors"

class PurchasingBehavior(str, Enum):
    Impulse = "Impulse"
    Planned = "Planned"
    Habitual = "Habitual"
    Complex = "Complex"

class USP(str, Enum):
    CostLeadership = "Cost Leadership"
    QualityLeadership = "Quality Leadership"
    ServiceOrientation = "Service Orientation"
    Sustainability = "Sustainability"
    Innovation = "Innovation"

class RevenueModelType(str, Enum):
    TransactionModel = "Transaction Model"
    SubscriptionModel = "Subscription Model"
    FreemiumModel = "Freemium Model"
    AdvertisingModel = "Advertising Model"
    Licensing = "Licensing"
    MarketplaceModel = "Marketplace Model"
    DataMonetization = "Data Monetization"
    PlatformFees = "Platform Fees"

class PricingStrategy(str, Enum):
    ValueBasedPricing = "Value-Based Pricing"
    CostPlusPricing = "Cost-Plus Pricing"
    DynamicPricing = "Dynamic Pricing"
    PremiumPricing = "Premium Pricing"
    PenetrationPricing = "Penetration Pricing"

class PresenceForm(str, Enum):
    Physical = "Physical"
    Digital = "Digital"
    Hybrid = "Hybrid"

class ServiceArea(str, Enum):
    Local = "Local"
    Regional = "Regional"
    National = "National"
    International = "International"

class GrowthStrategy(str, Enum):
    MarketPenetration = "Market Penetration"
    MarketDevelopment = "Market Development"
    ProductDevelopment = "Product Development"
    Diversification = "Diversification"

class CompetitiveStrategy(str, Enum):
    CostLeadership = "Cost Leadership"
    Differentiation = "Differentiation"
    Focus = "Focus"

class MarketPotential(str, Enum):
    Local = "Local"
    National = "National"
    Global = "Global"

class MarketingChannels(str, Enum):
    SocialMedia = "Social Media"
    SEO = "SEO"
    SEA = "SEA"
    EmailMarketing = "Email Marketing"
    InfluencerMarketing = "Influencer Marketing"
    Others = "Others"

class BrandingStrategy(str, Enum):
    Premium = "Premium"
    PriceOriented = "Price-Oriented"
    MassMarket = "Mass Market"
    Niche = "Niche"

class KeyResources(str, Enum):
    Technology = "Technology"
    HumanResources = "Human Resources"
    Capital = "Capital"
    Data = "Data"
    BrandName = "Brand Name"
    Others = "Others"

class MainActivities(str, Enum):
    Production = "Production"
    Development = "Development"
    Marketing = "Marketing"
    Logistics = "Logistics"
    Service = "Service"
    CustomerSupport = "Customer Support"
    Others = "Others"

class GeneralInformation(BaseModel):
    analysis: str = Field(description="Analysis of the business idea regarding which values should be chosen in the business model canvas section.")
    business_model_type: List[BusinessModelType] = Field(description="Classification of the business model.")
    industry: str = Field(description="The primary industry or sector (e.g., SaaS, E-commerce).")

class Demographics(BaseModel):

    age_range: AgeRange = Field(description="Target age groups. (only for B2C, B2B2C, D2C)")
    income_level: Optional[str] = Field(None, description="Income level of the target audience (e.g., Low, Middle, High).")
    lifestyle: Optional[str] = Field(None, description="Lifestyle characteristics of the audience (e.g., Urban, Tech-Savvy).")

class TargetSegment(BaseModel):
    customer_type: List[BusinessModelType] = Field(description="Primary customer segment")
    demographics: Optional[Demographics] = Field(None, description="Demographic details of the target audience.")
    purchasing_behavior: Optional[PurchasingBehavior] = Field(None, description="Buying behavior of customers.")
    geographic_segmentation: Optional[str] = Field(None, description="Geographic segmentation of the market (e.g., Local, Regional).")

class ValueProposition(BaseModel):
    usp: str = Field(description="Unique Selling Proposition.")
    customer_problem: str = Field(description="The problem the product or service solves.")
    job_to_be_done: Optional[str] = Field(None, description="The job customers are trying to accomplish.")
    customer_pains: List[str] = Field(description="Pain points experienced by the customers.")
    customer_gains: List[str] = Field(description="Benefits or gains for the customer.")

class OfferPortfolio(BaseModel):
    main_offer: List[str] = Field(description="Primary products or services offered.")
    additional_offers: Optional[List[str]] = Field(None, description="Additional products or services that complement the main offer.")

class RevenueModel(BaseModel):
    revenue_model: List[RevenueModelType] = Field(description="Revenue generation models.")
    pricing_strategy: Optional[PricingStrategy] = Field(None, description="Pricing strategy.")

class Presence(BaseModel):
    presence_form: PresenceForm = Field(description="Presence type.")
    service_area: ServiceArea = Field(description="Geographic coverage.")

class Strategy(BaseModel):
    growth_strategy: GrowthStrategy = Field(description="Growth strategy.")
    competitive_strategy: CompetitiveStrategy = Field(description="Competitive strategy.")


class Marketing(BaseModel):
    channels: List[MarketingChannels] = Field(description="Marketing channels.")
    branding_strategy: Optional[BrandingStrategy] = Field(None, description="Branding approach.")

class Resources(BaseModel):
    key_resources: List[KeyResources] = Field(description="Key resources required.")
    key_partners: Optional[List[str]] = Field(None, description="Important partners and collaborators.")

class Processes(BaseModel):
    main_activities: List[MainActivities] = Field(description="Core business activities.")
    automation_potential: Optional[bool] = Field(None, description="Whether the processes have automation potential.")

class BusinessModelSchema(BaseModel):
    general_information: GeneralInformation
    target_segments: List[TargetSegment]
    value_proposition: List[ValueProposition]
    offer_portfolio: OfferPortfolio
    revenue_model: RevenueModel
    presence: Presence
    strategy: Strategy

    marketing: Marketing
    resources: Resources
    processes: Processes


def generate_business_model_canvas(business_idea: str) -> BusinessModelSchema:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_structured_output = llm.with_structured_output(BusinessModelSchema, method="json_schema")
    prompt = load_prompt("generate_initial_business_model_canvas.txt")
    system_instructions = prompt.format(business_idea=business_idea)
    response = llm_with_structured_output.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate the business model canvas for the following business idea: " + business_idea)
    ] )

    return response