from agents.research.WebResearcher import graph as webResearcher
import streamlit as st
import asyncio
from agents.business_landscape_research.BusinessLandscapeResearcher import BusinessLandscapeResearcher


async def process_results(topic: str):
    researcher = BusinessLandscapeResearcher()
    async for result in researcher.ainvoke(topic=topic):
        normalized_field = result["field"].replace("_", " ").title()
        st.markdown(f"### {normalized_field}")
        st.markdown(result["value"])
        st.markdown("---")

def main():
    st.title("Business Landscape Evaluation")
    
    # User Input
    topic = st.text_input("Enter your business idea:", "")
    
    # Button to start research
    if st.button("Generate Report"):
        if topic:
            st.info("Research is being conducted... Please wait.")
            # Run async function in sync context
            asyncio.run(process_results(topic))
        else:
            st.error("Please enter a business idea.")

if __name__ == "__main__":
    main()
