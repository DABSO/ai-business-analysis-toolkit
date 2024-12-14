from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from agents.research.WebResearcher import graph as webResearcher

async def generate_research(business_idea: str):
    # 1. Marktanalyse 
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
    yield {
        "field": "market_analysis_report",
        "value": market_analysis_report["final_report"]
    }


    
    # 2. Konkurrentenanalyse
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
    yield {
        "field": "competitor_analysis_report",
        "value": competitor_analysis_report["final_report"]
    }

    # 3. Kundenmeinungsanalyse
    customer_analysis_topic = f"Führen Sie eine Analyse der Kundenmeinungen und Bewertungen zu bestehenden Produkten oder Dienstleistungen im Zusammenhang mit {business_idea} durch. Ziel ist es, häufige Kundenbedürfnisse, Kritikpunkte und potenzielle Verbesserungsfelder zu identifizieren."
    customer_analysis_structure = f"""# Kundenmeinungsanalyse Report-Struktur

## Analyse von Bewertungen
- Sammeln und Auswerten von Kundenbewertungen (z. B. Foren,Blogs, Social Media, Bewertungsplattformen).
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
    yield {
        "field": "customer_analysis_report",
        "value": customer_analysis_report["final_report"]
    }


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
    yield {
        "field": "technology_analysis_report",
        "value": technology_analysis_report["final_report"]
    }

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
    yield {
        "field": "technology_trends_report",
        "value": technology_trends_report["final_report"]
    }



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
    yield {
        "field": "legal_compliance_report",
        "value": legal_compliance_report["final_report"]
    }   
    
    

      




