from dotenv import load_dotenv
import os
import asyncio
import json
from pydantic import BaseModel
import streamlit as st
import threading
import time

load_dotenv()

from agents.competitor_research.CompetitorResearcher import CompetitionResearcher
from utils.pdf_generation import generate_pdf_report

# Custom JSON encoder to handle Pydantic objects
class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)

def convert_to_dict(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_dict(value) for key, value in obj.items()}
    else:
        return obj

def display_product(product):
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(product["name"])
            st.write(f"💰 Price: ${product['price']}")
            st.write(f"📅 Billing: {product['billing_model']}")
            
        with col2:
            if product["features"]:
                st.write("✨ Features:")
                for feature in product["features"]:
                    st.write(f"- {feature}")
            
            if product["value_propositions"]:
                st.write("🎯 Value Propositions:")
                for prop in product["value_propositions"]:
                    st.write(f"- {prop}")

def update_timer(placeholder, start_time, stop_event):
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        placeholder.text(f"⏱️ Time elapsed: {elapsed_time:.1f} seconds")
        time.sleep(0.1)  # Update every 0.1 seconds

def main():
    st.title("Competitor Research Report")
    
    business_idea = st.text_area(
        "Enter your business idea",
        placeholder="Example: An AI-powered writing assistant for academic papers, focusing on citation support.",
        help="Describe your business idea in detail to get better competitor analysis"
    )
    
    # Add search settings in a collapsible section
    with st.expander("🔧 Advanced Search Settings"):
        col1, col2 = st.columns(2)
        with col1:
            num_competition_queries = st.slider("Competition Queries", 1, 10, 3, help="Number of queries to find competitors")
            num_stat_queries = st.slider("Stat Queries", 1, 10, 2, help="Number of queries to find statistics")
            num_product_queries = st.slider("Product Queries", 1, 10, 2, help="Number of queries to find products")
            
        with col2:
            num_competition_results = st.slider("Competition Results", 1, 20, 10, help="Number of competitor results to process")
            num_stat_results = st.slider("Stat Results", 1, 10, 3, help="Number of statistic results to process")
            num_product_results = st.slider("Product Results", 1, 10, 2, help="Number of product results to process")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            num_competition_tokens = st.slider("Competition Tokens", 100, 2000, 1000, 100, help="Tokens per competition source")
        with col4:
            num_stat_tokens = st.slider("Stat Tokens", 100, 2000, 1000, 100, help="Tokens per stat source")
        with col5:
            num_product_tokens = st.slider("Product Tokens", 100, 2000, 1000, 100, help="Tokens per product source")
    
    if st.button("🔍 Research Competitors", type="primary"):
        if not business_idea:
            st.warning("Please enter a business idea first.")
            return
            
        # Update the parameters dict with slider values
        research_params = {
            "business_idea": business_idea,
            "num_competition_queries": num_competition_queries,
            "num_stat_queries": num_stat_queries,
            "num_product_queries": num_product_queries,
            "num_competition_results": num_competition_results,
            "num_stat_results": num_stat_results,
            "num_product_results": num_product_results,
            "num_competition_tokens_per_source": num_competition_tokens,
            "num_stat_tokens_per_source": num_stat_tokens,
            "num_product_tokens_per_source": num_product_tokens
        }
            
        start_time = time.time()
        progress_placeholder = st.empty()
        stop_event = threading.Event()
        
        # Start timer thread
        timer_thread = threading.Thread(
            target=update_timer, 
            args=(progress_placeholder, start_time, stop_event)
        )
        timer_thread.start()
        
        with st.spinner("Researching competitors..."):
            try:
                competition_researcher = CompetitionResearcher()
                result = asyncio.run(competition_researcher.ainvoke(**research_params))
                
                # Stop the timer
                stop_event.set()
                timer_thread.join()
                
                final_time = time.time() - start_time
                progress_placeholder.text(f"⏱️ Completed in {final_time:.1f} seconds")

                data = convert_to_dict(result)
                
                
                # Display results count
                st.success(f"Found {len(data['competitors'])} competitors")

                # Create PDF download button in a container
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("📄 Generate PDF"):
                            with st.spinner("Generating PDF report..."):
                                # Generate PDF bytes directly
                                pdf_bytes = generate_pdf_report(data)
                                
                                # Store PDF in session state for download
                                st.session_state.pdf_bytes = pdf_bytes
                                st.session_state.show_download = True
                    
                    with col2:
                        if 'show_download' in st.session_state and st.session_state.show_download:
                            st.download_button(
                                label="📥 Download Report",
                                data=st.session_state.pdf_bytes,
                                file_name="competitor_research_report.pdf",
                                mime="application/pdf",
                                help="Click to download the PDF report"
                            )
                
                
                # Display competitors
                for competitor in data["competitors"]:
                    with st.expander(f"🏢 {competitor['name']}"):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.write(f"👥 Employees: {competitor['employees'] or 'Unknown'}")
                        with col2:
                            st.write(f"🌐 Website: [{competitor['official_website_domain']}](https://{competitor['official_website_domain']})")

                        st.markdown(competitor["report"])
                        
                        st.subheader("Products")
                        for product_list in competitor["products"]:
                            if isinstance(product_list, list):
                                for product in product_list:
                                    st.divider()
                                    display_product(product)
                            else:
                                st.divider()
                                display_product(product_list)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Add some helpful information at the bottom
    with st.sidebar:
        st.markdown("""
        ### How to use
        1. Enter your business idea in the text area
        2. Click "Research Competitors" to start the analysis
        3. Expand competitor cards to view detailed information
        
        ### Tips
        - Be specific about your business idea
        - Include your target market and main features
        - Wait for the analysis to complete
        """)

if __name__ == "__main__":
    main()

