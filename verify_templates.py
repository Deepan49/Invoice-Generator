from app import app
from flask import render_template

def test_templates():
    with app.test_request_context():
        try:
            print("Testing login.html rendering...")
            render_template('login.html')
            print("OK: login.html rendered without assertion errors.")
            
            print("Testing dashboard.html rendering...")
            # Dashboard requires some context variables, but rendering will still catch block errors
            render_template('dashboard.html', 
                            invoices=[], 
                            total_revenue=0, 
                            unpaid_amount=0, 
                            invoice_count=0, 
                            client_count=0, 
                            chart_labels=[], 
                            chart_values=[])
            print("OK: dashboard.html rendered without assertion errors.")
            
            print("Testing index.html rendering...")
            render_template('index.html')
            print("OK: index.html rendered without assertion errors.")
            
        except Exception as e:
            print(f"FAILED: {e}")
            exit(1)

if __name__ == "__main__":
    test_templates()
