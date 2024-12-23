from agents.research.WebResearcher import graph as webResearcher
import streamlit as st
import asyncio
from experiments.flow import generate_research

async def process_results(topic: str):
    async for result in generate_research(topic):
        normalized_field = result["field"].replace("_", " ").title()
        st.markdown(f"### {normalized_field}")
        st.markdown(result["value"])
        st.markdown("---")

def main():
    st.title("´Market Research Report Generator")
    
    # User Input
    topic = st.text_input("Geben Sie ein Thema ein:", "")
    
    # Button to start research
    if st.button("Report erstellen"):
        if topic:
            st.info("Recherche wird durchgeführt... Bitte warten.")
            # Run async function in sync context
            asyncio.run(process_results(topic))
        else:
            st.error("Bitte geben Sie ein Thema ein.")

if __name__ == "__main__":
    main()
