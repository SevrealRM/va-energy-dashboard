import os
import json
import requests
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# We configure the model to ONLY output JSON
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def get_va_bill_data():
    # TEST DATA: Simulating the Virginia LIS. Real links for your 2026 project:
    bills = [
        {
            "id": "HB 1393", 
            "title": "Large Energy User Grid Cost Shifting",
            "lis_link": "https://lis.virginia.gov/cgi-bin/legp604.exe?261+ful+HB1393" # Example 2026 link format
        },
        {
            "id": "SB 553", 
            "title": "Data Center Water Consumption Reporting",
            "lis_link": "https://lis.virginia.gov/cgi-bin/legp604.exe?261+ful+SB553"
        },
        {
            "id": "HB 153", 
            "title": "Data Center Siting and Noise Limits",
            "lis_link": "https://lis.virginia.gov/cgi-bin/legp604.exe?261+ful+HB153"
        }
    ]
    return bills

def analyze_with_ai(bill_list):
    prompt = f"""
    Analyze these Virginia data center bills: {bill_list}. 
    Provide a JSON list. Each object in the list must have exactly these keys:
    'id' (string),
    'headline' (string, a catchy 3-5 word summary of the bill's intent),
    'full_summary' (string, a concise paragraph describing the impact),
    'sentiment_score' (number 1-100),
    'supporters' (string),
    'opponents' (string),
    'link' (string, use the 'lis_link' provided for the bill).
    """
    
    response = model.generate_content(prompt)
    
    # Because we forced JSON output, we can load it directly safely
    return json.loads(response.text)
if __name__ == "__main__":
    print("Fetching bills...")
    raw_bills = get_va_bill_data()
    
    print("Analyzing with Gemini...")
    analyzed_data = analyze_with_ai(raw_bills)
    
    with open('data.json', 'w') as f:
        json.dump(analyzed_data, f, indent=4)
    
    print("Success! data.json updated.")
