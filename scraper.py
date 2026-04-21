import os
import json
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# We configure the model to ONLY output JSON
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def get_va_bill_data():
    # TEST DATA: Using the real bills for your project
    bills = [
        {"id": "HB 1393", "title": "Large Energy User Grid Cost Shifting"},
        {"id": "SB 553", "title": "Data Center Water Consumption Reporting"},
        {"id": "HB 153", "title": "Data Center Siting and Noise Limits"}
    ]
    return bills

def analyze_with_ai(bill_list):
    prompt = f"""
    Analyze these Virginia data center bills: {bill_list}. 
    Provide a JSON list. Each object in the list must have exactly these keys:
    'id' (string),
    'headline' (string, a clear 3-8 word summary of the bill's intent),
    'full_summary' (string, a concise paragraph describing the impact),
    'sentiment_score' (number 1-100),
    'supporters' (string),
    'opponents' (string).
    """
    
    response = model.generate_content(prompt)
    
    # Safely load the JSON
    return json.loads(response.text)

if __name__ == "__main__":
    print("Fetching bills...")
    raw_bills = get_va_bill_data()
    
    print("Analyzing with Gemini...")
    analyzed_data = analyze_with_ai(raw_bills)
    
    with open('data.json', 'w') as f:
        json.dump(analyzed_data, f, indent=4)
    
    print("Success! data.json updated.")
