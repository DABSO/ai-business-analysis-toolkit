from langgraph.graph import StateGraph, START, END
from agents.research.WebResearcher import graph as webResearcher
from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class MarketResearchState(TypedDict):
    """
    Type definition for the state object used throughout the market research agent workflow.
    Contains all reports generated during the research phases.
    """
    business_idea : str
    trend_research_report : str
    competitor_research_report : str
    customer_analysis_report : str
    technology_analysis_report : str
    technology_trends_report : str
    legal_compliance_report : str
   


class FinalReport(BaseModel):
    """
    Pydantic model representing the structured LLM output of the final consolidated report.
    Contains the formatted markdown output of all research findings.
    """
    final_report : str = Field(description="The final report formatted as markdown")


async def generate_market_trends_report(state : MarketResearchState):
    """
    Generates a comprehensive market analysis report focusing on market volume,
    growth rates, target segments, and current market trends.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated market analysis report that gets added to the state
    """
    business_idea = state["business_idea"]
    market_analysis_topic = f"Erstellen Sie eine umfassende Marktanalyse für das Produkt oder die Dienstleistung: {business_idea}. Ziel ist es, Marktvolumen, Wachstumsraten, Zielsegmente und aktuelle Markttrends zu identifizieren, die für eine potenzielle Markteinführung relevant sind. Die Analyse sollte relevante geografische Märkte, bestehende Marktführer, und mögliche Markteintrittsbarrieren berücksichtigen."
    market_analysis_structure = f"""# Marktanalyse Report-Struktur

## Marktvolumen & Wachstumsraten
- Globale und regionale Marktgröße (absolut in Umsatz und Einheiten).
- Historische und prognostizierte Wachstumsraten (3-5 Jahre).
- **KPIs:** 
  - Marktgröße (in $ oder Einheiten).
  - Wachstumsrate (jährlich, %).

## Zielsegmente
- Identifikation der Zielsegmente basierend auf geografischen, demografischen oder branchenspezifischen Kriterien.
- **KPIs:** 
  - Anzahl identifizierter Segmente.
  - Umsatzpotenziale je Segment.

## Markteintrittsbarrieren
- Regulatorische, wirtschaftliche oder technologische Hindernisse.
- **KPIs:** 
  - Anzahl der Hindernisse.
  - Qualitative Bewertung der Eintrittshürden.

## Executive Summary
- Kurze Zusammenfassung der wichtigsten Erkenntnisse (Marktgröße, Trends, Barrieren).
"""
    
    market_analysis_report = await webResearcher.ainvoke({
        "topic": market_analysis_topic,
        "report_structure": market_analysis_structure
    })
    return {"market_analysis_report": market_analysis_report["final_report"]}

async def generate_competitor_analysis_report(state : MarketResearchState):
    """
    Analyzes main competitors for the business idea, including market shares,
    business models, strengths, weaknesses, and differentiation strategies.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated competitor analysis report that gets added to the state
    """
    # 2. Konkurrentenanalyse
    business_idea = state["business_idea"]
    competitor_analysis_topic = f"Analysieren Sie die Hauptkonkurrenten für die geplante Business-Idee: {business_idea}. Ziel ist es, deren Marktanteile, Geschäftsmodelle, Stärken, Schwächen und Differenzierungsstrategien zu verstehen, um Wettbewerbsvorteile zu identifizieren."
    competitor_analysis_structure = f"""# Konkurrentenanalyse Report-Struktur

## Marktführer-Identifikation
- Liste der Top-5-10 Wettbewerber mit Marktanteilsinformationen.
- **KPIs:** 
  - Marktanteile (%) je Wettbewerber.
  - Geografische Präsenz.

## Produktvergleich
- Überblick über die wichtigsten Produkte/Dienstleistungen der Konkurrenten.
- **KPIs:** 
  - Anzahl der Produkte/Dienstleistungen.
  - Preisniveaus.
  - Alleinstellungsmerkmale (USPs).

## SWOT-Analyse der Konkurrenten
- Identifikation von Stärken, Schwächen, Chancen und Bedrohungen.
- **KPIs:** 
  - Differenzierungsstrategien.
  - Kundenbindungsmaßnahmen.

## Executive Summary
- Kurzüberblick der wichtigsten Konkurrenten und deren Marktpositionen.
"""
    
    competitor_analysis_report = await webResearcher.ainvoke({
        "topic": competitor_analysis_topic,
        "report_structure": competitor_analysis_structure
    })
    return {"competitor_analysis_report": competitor_analysis_report["final_report"]}


async def generate_customer_analysis_report(state : MarketResearchState):
    """
    Analyzes customer opinions and reviews of existing products/services,
    identifying common needs, criticisms, and potential areas for improvement.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated customer analysis report that gets added to the state
    """
    # 3. Kundenmeinungsanalyse
    business_idea = state["business_idea"]
    customer_analysis_topic = f"Führen Sie eine Analyse der Kundenmeinungen und Bewertungen zu bestehenden Produkten oder Dienstleistungen im Zusammenhang mit {business_idea} durch. Ziel ist es, häufige Kundenbedürfnisse, Kritikpunkte und potenzielle Verbesserungsfelder zu identifizieren."
    customer_analysis_structure = f"""# Kundenmeinungsanalyse Report-Struktur

## Analyse von Bewertungen
- Sammeln und Auswerten von Kundenbewertungen (z. B. Foren, Blogs, Social Media, Bewertungsplattformen).
- **KPIs:** 
  - Anzahl analysierter Bewertungen.
  - Anteil positiver/negativer Bewertungen.

## Schlüsselbedürfnisse & Kritikpunkte
- Identifikation wiederkehrender Themen (z. B. Preis, Qualität, Features).
- **KPIs:** 
  - Häufig genannte Bedürfnisse/Kritikpunkte.
  - Sentiment-Analyse-Scores.

## Empfehlungen
- Handlungsempfehlungen zur Produktentwicklung basierend auf der Analyse.

## Executive Summary
- Kurzdarstellung der Kundenpräferenzen und häufigsten Kritikpunkte.
"""
    
    customer_analysis_report = await webResearcher.ainvoke({
        "topic": customer_analysis_topic,
        "report_structure": customer_analysis_structure
    })
    return {"customer_analysis_report": customer_analysis_report["final_report"]}


async def generate_technology_analysis_report(state : MarketResearchState):
    """
    Researches the current state of technology required for implementing the business idea,
    including available solutions, maturity levels, and typical weaknesses.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated technology analysis report that gets added to the state
    """
    business_idea = state["business_idea"]
    # 4. Stand der Technologie
    technology_analysis_topic = f"Recherchieren Sie den aktuellen Stand der Technologie, die für die Umsetzung von {business_idea} erforderlich ist. Ziel ist es, verfügbare technische Lösungen, deren Reifegrad und typische Schwächen zu ermitteln."
    technology_analysis_structure = f"""# Stand der Technologie Report-Struktur

## Verfügbare Technologien
- Liste relevanter Technologien mit Kurzbeschreibung und Anwendung.
- **KPIs:** 
  - Anzahl verfügbarer Technologien.
  - Marktanteile führender Technologien.

## Reifegrad
- Bewertung des Entwicklungsstands (z. B. Proof of Concept, Marktreife).
- **KPIs:** 
  - Anzahl marktreifer Lösungen.
  - Technologische Barrieren.

## Praxisbeispiele
- Fallstudien oder Berichte über ähnliche Implementierungen.

## Executive Summary
- Übersicht der technologischen Basis und aktueller Implementierungen.
"""
    
    technology_analysis_report = await webResearcher.ainvoke({
        "topic": technology_analysis_topic,
        "report_structure": technology_analysis_structure
    })
    return {"technology_analysis_report": technology_analysis_report["final_report"]}


async def generate_technology_trends_report(state : MarketResearchState):
    """
    Researches current technological trends relevant to the business idea implementation,
    focusing on key developments and their potential impact.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated technology trends report that gets added to the state
    """
    business_idea = state["business_idea"]
    # 5. Technologische Trends
    technology_trends_topic = f"Recherchieren Sie die aktuellen technologischen Trends, die für die Umsetzung von {business_idea} relevant sind. Ziel ist es, die wichtigsten Entwicklungen in der Technologie zu identifizieren, die für die Umsetzung von {business_idea} relevant sind."
    technology_trends_structure = """# Technologische Trends Report-Struktur

## Identifikation von Trends
- Liste relevanter Trends und deren mögliche Auswirkungen.
- **KPIs:** 
  - Anzahl relevanter Trends.
  - Innovationsvorsprung (qualitativ bewertet).

## Technologie-Investitionen
- Analyse von Investitionsströmen in bestimmte Technologien.
- **KPIs:** 
  - Höhe der Investitionen.
  - Geografische Verteilung der Investitionen.

## Zukunftsprognosen
- Expertenmeinungen oder Studien zu zukünftigen Entwicklungen.

## Executive Summary
- Überblick der wichtigsten technologischen Trends.
"""

    technology_trends_report = await webResearcher.ainvoke({
        "topic": technology_trends_topic,
        "report_structure": technology_trends_structure
    })
    return {"technology_trends_report": technology_trends_report["final_report"]}



async def generate_legal_compliance_report(state : MarketResearchState):
    """
    Researches regulatory and legal requirements relevant to the business idea,
    identifying potential hurdles and necessary approvals for legal compliance.

    Args:
        state (MarketResearchState): Current state containing the business idea

    Returns:
        dict: Contains the generated legal compliance report that gets added to the state
    """
    business_idea = state["business_idea"]
    # 6. Rechtskonformität 
    legal_compliance_topic = f"Recherchieren Sie regulatorische und gesetzliche Anforderungen, die für die Umsetzung von {business_idea} relevant sind. Ziel ist es, potenzielle Hürden und notwendige Genehmigungen zu identifizieren, um Rechtskonformität sicherzustellen."
    legal_compliance_structure = f"""# Rechtskonformität Report-Struktur

    ## Gesetzliche Vorschriften
    - Übersicht relevanter Gesetze und Verordnungen (z. B. Datenschutz, Produkthaftung).
    - **KPIs:** 
    - Anzahl identifizierter Vorschriften.
    - Schweregrad möglicher Nicht-Konformitäten.

    ## Branchenstandards
    - Übersicht über Zertifizierungen oder Standards (z. B. ISO, CE).
    - **KPIs:** 
    - Anzahl empfohlener Zertifikate.
    - Geschätzte Kosten der Zertifizierung.

    ## Anforderungen nach Region
    - Analyse länderspezifischer Regelungen und Unterschiede.
    - **KPIs:** 
    - Anzahl kritischer Abweichungen zwischen Regionen.

    ## Executive Summary
    - Zusammenfassung der wichtigsten regulatorischen Anforderungen.
    """
    
    legal_compliance_report = await webResearcher.ainvoke({
        "topic": legal_compliance_topic,
        "report_structure": legal_compliance_structure
    })
    return {"legal_compliance_report": legal_compliance_report["final_report"]}


async def generate_final_report(state : MarketResearchState):
    """
    Consolidates all individual reports into a final comprehensive analysis using LLM.
    
    Args:
        state (MarketResearchState): Current state containing all generated reports

    Returns:
        dict: Contains the final consolidated report that gets added to the state
    """

    trend_analysis_report = state["trend_analysis_report"]
    competitor_analysis_report = state["competitor_analysis_report"]
    customer_analysis_report = state["customer_analysis_report"]
    technology_analysis_report = state["technology_analysis_report"]
    technology_trends_report = state["technology_trends_report"]
    legal_compliance_report = state["legal_compliance_report"]


    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


    prompt = PromptTemplate(
        input_variables=["trend_analysis_report", "competitor_analysis_report", "customer_analysis_report", "technology_analysis_report", "technology_trends_report", "legal_compliance_report"],
        template="""
        trend_analysis_report: {trend_analysis_report}
        competitor_analysis_report: {competitor_analysis_report}
        customer_analysis_report: {customer_analysis_report}
        technology_analysis_report: {technology_analysis_report}
        technology_trends_report: {technology_trends_report}
        legal_compliance_report: {legal_compliance_report}

        You are a business analyst. You are given a market analysis report, a competitor analysis report, a customer analysis report, a technology analysis report, a technology trends report, and a legal compliance report.
        You are tasked with creating a final report that includes the most important findings from the given subreports in a final structured report.

        The final report should be formatted as markdown.
        """
    ).format(
        trend_analysis_report=trend_analysis_report,
        competitor_analysis_report=competitor_analysis_report,
        customer_analysis_report=customer_analysis_report,
        technology_analysis_report=technology_analysis_report,
        technology_trends_report=technology_trends_report,
        legal_compliance_report=legal_compliance_report
    )

    llm_with_structured_output = llm.with_structured_output(FinalReport)

    final_report = llm_with_structured_output.invoke(prompt)

    return {"final_report": final_report}







def get_market_research_graph():
    """
    Creates and configures the research workflow graph defining the execution order
    of various analysis steps.

    Returns:
        CompiledGraph: Compiled graph ready for execution 
    """
    graph = StateGraph()

    graph.add_node("generate_market_trends_report", generate_market_trends_report)
    graph.add_node("generate_competitor_analysis_report", generate_competitor_analysis_report)
    graph.add_node("generate_customer_analysis_report", generate_customer_analysis_report)
    graph.add_node("generate_technology_analysis_report", generate_technology_analysis_report)
    graph.add_node("generate_technology_trends_report", generate_technology_trends_report)
    graph.add_node("generate_legal_compliance_report", generate_legal_compliance_report)
    graph.add_node("generate_final_report", generate_final_report)

    graph.add_edge(START, "generate_market_trends_report")
    graph.add_edge(START, "generate_competitor_analysis_report")
    graph.add_edge(START, "generate_customer_analysis_report")
    graph.add_edge(START, "generate_technology_analysis_report")
    graph.add_edge(START, "generate_technology_trends_report")
    graph.add_edge(START, "generate_legal_compliance_report")

    graph.add_edge("generate_market_trends_report", "generate_final_report")
    graph.add_edge("generate_competitor_analysis_report", "generate_final_report")
    graph.add_edge("generate_customer_analysis_report", "generate_final_report")
    graph.add_edge("generate_technology_analysis_report", "generate_final_report")
    graph.add_edge("generate_technology_trends_report", "generate_final_report")
    graph.add_edge("generate_legal_compliance_report", "generate_final_report")

    graph.add_edge("generate_final_report", END)

    return graph.compile()

