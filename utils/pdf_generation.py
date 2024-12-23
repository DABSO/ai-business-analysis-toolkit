from markdown import markdown
from datetime import datetime
import pdfkit
import tempfile
import os

def generate_pdf_report(data):
    """
    Generate a PDF report from the competitor research data
    
    Args:
        data (dict): The competitor research data
    
    Returns:
        bytes: The generated PDF as bytes
    """
    # Create a temporary HTML file for markdown conversion
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
        # Start HTML document with styling
        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    margin: 1cm;
                }
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    line-height: 1.6;
                }
                h1 { 
                    color: #2c3e50;
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e; 
                    margin-top: 30px;
                }
                .competitor { 
                    border: 1px solid #bdc3c7; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .product { 
                    margin: 15px 0; 
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 4px;
                }
                .metadata { 
                    color: #7f8c8d;
                    font-style: italic;
                }
                .report {
                    margin: 15px 0;
                    text-align: justify;
                }
                ul {
                    margin: 10px 0;
                    padding-left: 20px;
                }
                li {
                    margin: 5px 0;
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                .feature-list, .value-prop-list {
                    background: #fff;
                    padding: 10px;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
        """
        
        # Add report header
        html_content += f"""
        <h1>Competitor Research Report</h1>
        <p class="metadata">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """

        # Add competitors
        for competitor in data['competitors']:
            html_content += f"""
            <div class="competitor">
                <h2>🏢 {competitor['name']}</h2>
                <p class="metadata">
                    👥 Employees: {competitor['employees'] or 'Unknown'} |
                    🌐 Website: <a href="https://{competitor['official_website_domain']}">{competitor['official_website_domain']}</a>
                </p>
                
                <div class="report">
                    {markdown(competitor['report'])}
                </div>
                
                <h3>Products</h3>
            """
            
            # Add products
            for product_list in competitor['products']:
                products = product_list if isinstance(product_list, list) else [product_list]
                for product in products:
                    html_content += f"""
                    <div class="product">
                        <h4>{product['name']}</h4>
                        <p>💰 Price: ${product['price']}</p>
                        <p>📅 Billing: {product['billing_model']}</p>
                    """
                    
                    if product['features']:
                        html_content += '<div class="feature-list"><p>✨ Features:</p><ul>'
                        for feature in product['features']:
                            html_content += f"<li>{feature}</li>"
                        html_content += "</ul></div>"
                    
                    if product['value_propositions']:
                        html_content += '<div class="value-prop-list"><p>🎯 Value Propositions:</p><ul>'
                        for prop in product['value_propositions']:
                            html_content += f"<li>{prop}</li>"
                        html_content += "</ul></div>"
                    
                    html_content += "</div>"
            
            html_content += "</div>"
        
        html_content += "</body></html>"
        f.write(html_content)
        f.flush()
        
        # Create a temporary file path for the PDF
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        
        # Convert HTML to PDF using pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_file(f.name, temp_pdf, options=options)
        
        # Read the PDF into memory
        with open(temp_pdf, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Clean up temporary files
        os.unlink(f.name)
        os.unlink(temp_pdf)
        
        return pdf_bytes
