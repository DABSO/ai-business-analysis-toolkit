import streamlit as st
import pdfkit
from io import BytesIO
from agents.business_model_canvas_generator.BusinessModelCanvasGenerator import (
    generate_business_model_canvas,
    BusinessModelSchema,
    BusinessModelType,
    AgeRange,
    PurchasingBehavior,
    ServiceArea,
    PresenceForm,
    MarketingChannels,
    BrandingStrategy,
    KeyResources,
    MainActivities,
    GrowthStrategy,
    CompetitiveStrategy,
    RevenueModelType,
    PricingStrategy,
)

def main():
    st.title("Business Model Canvas Generator")
    st.write("Enter your business idea below to generate and edit your Business Model Canvas.")

    business_idea = st.text_area("Business Idea", height=150)

    if 'target_segments_count' not in st.session_state:
        st.session_state.target_segments_count = 0
    if 'value_proposition_count' not in st.session_state:
        st.session_state.value_proposition_count = 0

    if st.button("Generate Business Model Canvas"):
        with st.spinner("Generating Business Model Canvas..."):
            try:
                canvas: BusinessModelSchema = generate_business_model_canvas(business_idea)
                canvas_data = canvas.dict()
                # Initialize session state for dynamic lists
                st.session_state.target_segments_count = len(canvas_data.get('target_segments', []))
                st.session_state.value_proposition_count = len(canvas_data.get('value_proposition', []))
            except Exception as e:
                st.error(f"Error generating Business Model Canvas: {e}")
                return

        st.success("Business Model Canvas generated successfully!")

    if 'canvas_data' not in st.session_state and 'canvas_data' in locals():
        st.session_state.canvas_data = canvas_data

    if 'canvas_data' in st.session_state:
        st.write("Edit Business Model Canvas")
        with st.container():

            # General Information
            st.header("General Information")
            analysis = st.text_area("Analysis", value=st.session_state.canvas_data['general_information']['analysis'])
            business_model_type = st.multiselect(
                "Business Model Type",
                options=[e.value for e in BusinessModelType],
                default=st.session_state.canvas_data['general_information']['business_model_type']
            )
            industry = st.text_input("Industry", value=st.session_state.canvas_data['general_information']['industry'])

            st.markdown("---")

            # Target Segments
            st.header("Target Segments")

            target_segments = []
            for i in range(st.session_state.target_segments_count):
                st.subheader(f"Target Segment {i + 1}")
                try:
                    segment_data = st.session_state.canvas_data['target_segments'][i]
                except IndexError:
                    segment_data = {}
                customer_type = st.multiselect(
                    "Customer Type",
                    options=[e.value for e in BusinessModelType],
                    default=segment_data.get('customer_type', [])
                )
                demographics = segment_data.get('demographics', {})
                age_range = st.selectbox(
                    "Age Range",
                    options=[e.value for e in AgeRange],
                    index=[e.value for e in AgeRange].index(demographics.get('age_range', 'Adults')) if 'age_range' in demographics else 0,
                    key=f"age_range_{i}"
                )
                income_level = st.text_input("Income Level", value=demographics.get('income_level', ''), key=f"income_level_{i}")
                lifestyle = st.text_input("Lifestyle", value=demographics.get('lifestyle', ''), key=f"lifestyle_{i}")
                purchasing_behavior = st.selectbox(
                    "Purchasing Behavior",
                    options=[e.value for e in PurchasingBehavior],
                    index=[e.value for e in PurchasingBehavior].index(segment_data.get('purchasing_behavior', 'Planned')) if 'purchasing_behavior' in segment_data else 1,
                    key=f"purchasing_behavior_{i}"
                )
                geographic_segmentation = st.text_input("Geographic Segmentation", value=segment_data.get('geographic_segmentation', ''), key=f"geographic_segmentation_{i}")

                target_segments.append({
                    "customer_type": customer_type,
                    "demographics": {
                        "age_range": age_range,
                        "income_level": income_level,
                        "lifestyle": lifestyle
                    },
                    "purchasing_behavior": purchasing_behavior,
                    "geographic_segmentation": geographic_segmentation
                })
            if st.button("Add Target Segment"):
                st.session_state.target_segments_count += 1
            st.markdown("---")

            # Value Proposition
            st.header("Value Proposition")

            value_propositions = []
            for i in range(st.session_state.value_proposition_count):
                st.subheader(f"Value Proposition {i + 1}")
                try:
                    vp_data = st.session_state.canvas_data['value_proposition'][i]
                except IndexError:
                    vp_data = {}
                usp = st.text_input("Unique Selling Proposition (USP)", value=vp_data.get('usp', ''), key=f"usp_{i}")
                customer_problem = st.text_area("Customer Problem", value=vp_data.get('customer_problem', ''), key=f"customer_problem_{i}")
                job_to_be_done = st.text_area("Job to be Done", value=vp_data.get('job_to_be_done', ''), key=f"job_to_be_done_{i}")
                customer_pains = st.text_area("Customer Pains (comma separated)", value=", ".join(vp_data.get('customer_pains', [])), key=f"customer_pains_{i}")
                customer_gains = st.text_area("Customer Gains (comma separated)", value=", ".join(vp_data.get('customer_gains', [])), key=f"customer_gains_{i}")

                value_propositions.append({
                    "usp": usp,
                    "customer_problem": customer_problem,
                    "job_to_be_done": job_to_be_done,
                    "customer_pains": [pain.strip() for pain in customer_pains.split(",")],
                    "customer_gains": [gain.strip() for gain in customer_gains.split(",")]
                })
            if st.button("Add Value Proposition"):
                st.session_state.value_proposition_count += 1

            st.markdown("---")

            # Offer Portfolio
            st.header("Offer Portfolio")
            offer_portfolio = {}
            main_offer = st.text_area("Main Offers (comma separated)", value=", ".join(st.session_state.canvas_data['offer_portfolio']['main_offer']), key="main_offer")
            additional_offers = st.text_area("Additional Offers (comma separated)", value=", ".join(st.session_state.canvas_data['offer_portfolio'].get('additional_offers', [])), key="additional_offers")

            offer_portfolio['main_offer'] = [offer.strip() for offer in main_offer.split(",")]
            offer_portfolio['additional_offers'] = [offer.strip() for offer in additional_offers.split(",")]

            st.markdown("---")

            # Revenue Model
            st.header("Revenue Model")
            revenue_model = st.multiselect(
                "Revenue Models",
                options=[e.value for e in RevenueModelType],
                default=st.session_state.canvas_data['revenue_model']['revenue_model']
            )
            pricing_strategy = st.selectbox(
                "Pricing Strategy",
                options=[e.value for e in PricingStrategy] + ["None"],
                index=len(PricingStrategy) if st.session_state.canvas_data['revenue_model']['pricing_strategy'] is None else [e.value for e in PricingStrategy].index(st.session_state.canvas_data['revenue_model'].get('pricing_strategy', 'Value-Based Pricing'))
            )

            st.markdown("---")

            # Presence
            st.header("Presence")
            presence_form = st.selectbox(
                "Presence Form",
                options=[e.value for e in PresenceForm],
                index=[e.value for e in PresenceForm].index(st.session_state.canvas_data['presence']['presence_form'])
            )
            service_area = st.selectbox(
                "Service Area",
                options=[e.value for e in ServiceArea],
                index=[e.value for e in ServiceArea].index(st.session_state.canvas_data['presence']['service_area'])
            )

            st.markdown("---")

            # Strategy
            st.header("Strategy")
            growth_strategy = st.selectbox(
                "Growth Strategy",
                options=[e.value for e in GrowthStrategy],
                index=[e.value for e in GrowthStrategy].index(st.session_state.canvas_data['strategy']['growth_strategy'])
            )
            competitive_strategy = st.selectbox(
                "Competitive Strategy",
                options=[e.value for e in CompetitiveStrategy],
                index=[e.value for e in CompetitiveStrategy].index(st.session_state.canvas_data['strategy']['competitive_strategy'])
            )

            st.markdown("---")

            # Marketing
            st.header("Marketing")
            marketing_channels = st.multiselect(
                "Marketing Channels",
                options=[e.value for e in MarketingChannels],
                default=st.session_state.canvas_data['marketing']['channels']
            )
            branding_strategy = st.selectbox(
                "Branding Strategy",
                options=[e.value for e in BrandingStrategy] + ["None"],
                index=len(BrandingStrategy) if st.session_state.canvas_data['marketing']['branding_strategy'] is None else [e.value for e in BrandingStrategy].index(st.session_state.canvas_data['marketing'].get('branding_strategy', 'Premium'))
            )

            st.markdown("---")

            # Resources
            st.header("Resources")
            key_resources = st.multiselect(
                "Key Resources",
                options=[e.value for e in KeyResources],
                default=st.session_state.canvas_data['resources']['key_resources']
            )
            key_partners = st.text_area("Key Partners (comma separated)", value=", ".join(st.session_state.canvas_data['resources'].get('key_partners', [])), key="key_partners")

            st.markdown("---")

            # Processes
            st.header("Processes")
            main_activities = st.multiselect(
                "Main Activities",
                options=[e.value for e in MainActivities],
                default=st.session_state.canvas_data['processes']['main_activities']
            )
            automation_potential = st.selectbox(
                "Automation Potential",
                options=["Yes", "No"],
                index=1 if not st.session_state.canvas_data['processes'].get('automation_potential', False) else 0
            )

            st.markdown("---")

            submitted = st.button("Generate and Download PDF")

            if submitted:
                with st.spinner("Generating PDF..."):
                    try:
                        # Compile edited data
                        updated_canvas = {
                            'general_information': {
                                'analysis': analysis,
                                'business_model_type': business_model_type,
                                'industry': industry
                            },
                            'target_segments': target_segments,
                            'value_proposition': value_propositions,
                            'offer_portfolio': offer_portfolio,
                            'revenue_model': {
                                'revenue_model': revenue_model,
                                'pricing_strategy': pricing_strategy if pricing_strategy != "None" else None
                            },
                            'presence': {
                                'presence_form': presence_form,
                                'service_area': service_area
                            },
                            'strategy': {
                                'growth_strategy': growth_strategy,
                                'competitive_strategy': competitive_strategy
                            },

                            'marketing': {
                                'channels': marketing_channels,
                                'branding_strategy': branding_strategy if branding_strategy != "None" else None
                            },
                            'resources': {
                                'key_resources': key_resources,
                                'key_partners': [partner.strip() for partner in key_partners.split(",")]
                            },
                            'processes': {
                                'main_activities': main_activities,
                                'automation_potential': True if automation_potential == "Yes" else False
                            }
                        }

                        html = generate_html(updated_canvas)

                        # Configure pdfkit
                        config = pdfkit.configuration()  # Assumes wkhtmltopdf is in PATH

                        # Convert PDF to bytes
                        pdf_bytes = BytesIO(pdfkit.from_string(html, False, configuration=config))

                        st.download_button(
                            label="Download Business Model Canvas as PDF",
                            data=pdf_bytes,
                            file_name="business_model_canvas.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")

def generate_html(data):
    html = f"""
    <html>
    <head>
        <title>Business Model Canvas</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ text-align: center; color: #2E86C1; }}
            h2 {{ color: #2874A6; border-bottom: 2px solid #2E86C1; padding-bottom: 5px; }}
            h3 {{ color: #1B4F72; }}
            p {{ line-height: 1.6; }}
            .section {{ margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <h1>Business Model Canvas</h1>

        <div class="section">
            <h2>General Information</h2>
            <p><strong>Analysis:</strong> {data['general_information']['analysis']}</p>
            <p><strong>Business Model Type:</strong> {', '.join(data['general_information']['business_model_type'])}</p>
            <p><strong>Industry:</strong> {data['general_information']['industry']}</p>
        </div>

        <div class="section">
            <h2>Target Segments</h2>
    """

    for idx, segment in enumerate(data['target_segments'], 1):
        html += f"""
            <h3>Target Segment {idx}</h3>
            <p><strong>Customer Type:</strong> {', '.join(segment['customer_type'])}</p>
            <p><strong>Age Range:</strong> {segment['demographics']['age_range']}</p>
            <p><strong>Income Level:</strong> {segment['demographics']['income_level']}</p>
            <p><strong>Lifestyle:</strong> {segment['demographics']['lifestyle']}</p>
            <p><strong>Purchasing Behavior:</strong> {segment['purchasing_behavior']}</p>
            <p><strong>Geographic Segmentation:</strong> {segment['geographic_segmentation']}</p>
        """

    html += """
        </div>
    """

    # Value Proposition
    html += """
        <div class="section">
            <h2>Value Proposition</h2>
    """
    for idx, vp in enumerate(data['value_proposition'], 1):
        html += f"""
            <h3>Value Proposition {idx}</h3>
            <p><strong>USP:</strong> {vp['usp']}</p>
            <p><strong>Customer Problem:</strong> {vp['customer_problem']}</p>
            <p><strong>Job to be Done:</strong> {vp['job_to_be_done']}</p>
            <p><strong>Customer Pains:</strong> {', '.join(vp['customer_pains'])}</p>
            <p><strong>Customer Gains:</strong> {', '.join(vp['customer_gains'])}</p>
        """

    html += """
        </div>
    """

    # Offer Portfolio
    html += f"""
        <div class="section">
            <h2>Offer Portfolio</h2>
            <p><strong>Main Offers:</strong> {', '.join(data['offer_portfolio']['main_offer'])}</p>
            <p><strong>Additional Offers:</strong> {', '.join(data['offer_portfolio'].get('additional_offers', []))}</p>
        </div>
    """

    # Revenue Model
    pricing_strategy = data['revenue_model']['pricing_strategy'] if data['revenue_model']['pricing_strategy'] else "N/A"
    html += f"""
        <div class="section">
            <h2>Revenue Model</h2>
            <p><strong>Revenue Models:</strong> {', '.join(data['revenue_model']['revenue_model'])}</p>
            <p><strong>Pricing Strategy:</strong> {pricing_strategy}</p>
        </div>
    """

    # Presence
    html += f"""
        <div class="section">
            <h2>Presence</h2>
            <p><strong>Presence Form:</strong> {data['presence']['presence_form']}</p>
            <p><strong>Service Area:</strong> {data['presence']['service_area']}</p>
        </div>
    """

    # Strategy
    html += f"""
        <div class="section">
            <h2>Strategy</h2>
            <p><strong>Growth Strategy:</strong> {data['strategy']['growth_strategy']}</p>
            <p><strong>Competitive Strategy:</strong> {data['strategy']['competitive_strategy']}</p>
        </div>
    """

    # Marketing
    branding_strategy = data['marketing']['branding_strategy'] if data['marketing']['branding_strategy'] else "N/A"
    html += f"""
        <div class="section">
            <h2>Marketing</h2>
            <p><strong>Marketing Channels:</strong> {', '.join(data['marketing']['channels'])}</p>
            <p><strong>Branding Strategy:</strong> {branding_strategy}</p>
        </div>
    """

    # Resources
    key_partners = ', '.join(data['resources']['key_partners'])
    html += f"""
        <div class="section">
            <h2>Resources</h2>
            <p><strong>Key Resources:</strong> {', '.join(data['resources']['key_resources'])}</p>
            <p><strong>Key Partners:</strong> {key_partners}</p>
        </div>
    """

    # Processes
    automation_potential = "Yes" if data['processes']['automation_potential'] else "No"
    html += f"""
        <div class="section">
            <h2>Processes</h2>
            <p><strong>Main Activities:</strong> {', '.join(data['processes']['main_activities'])}</p>
            <p><strong>Automation Potential:</strong> {automation_potential}</p>
        </div>
    """

    html += """
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    main()
