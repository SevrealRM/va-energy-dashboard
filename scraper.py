import os
import json
import requests
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# We configure the model to ONLY output JSON and enable Google Search Grounding
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    tools="google_search_retrieval",
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.2
    }
)

def get_legiscan_status(bill_id):
    """Hits the live LegiScan API to get the real-time status of the bill."""
    api_key = os.environ.get("LEGISCAN_API_KEY")
    
    if not api_key:
        return "Unknown (Missing LegiScan API Key)"
        
    # Querying LegiScan for the specific bill ID
    url = f"https://api.legiscan.com/?key={api_key}&op=getSearch&state=VA&query={bill_id.replace(' ', '')}"
    
    try:
        response = requests.get(url).json()
        if "searchresult" in response:
            # LegiScan returns a dictionary. We want the first actual result (skipping the 'summary' metadata key)
            for key, value in response["searchresult"].items():
                if key != "summary":
                    return f"Last Action: {value.get('last_action', 'None')} on {value.get('last_action_date', 'Unknown')}"
    except Exception as e:
        print(f"LegiScan error for {bill_id}: {e}")
        
    return "Status currently unavailable."

def get_va_bill_data():
    bills = [
        {"id": "HB 1393", "title": "Large Energy User Grid Cost Shifting"},
        {"id": "SB 553", "title": "Data Center Water Consumption Reporting"},
        {"id": "HB 153", "title": "Data Center Siting and Noise Limits"}
    ]
    
    print("Fetching live status from LegiScan...")
    for bill in bills:
        bill["status"] = get_legiscan_status(bill["id"])
        print(f" - {bill['id']}: {bill['status']}")
        
    return bills

def analyze_with_ai(bill_list):
    prompt = f"""
    You are a political consultant in Virginia. Analyze these data center bills and their live legislative status: {bill_list}. 
    
    Use Google Search to find ONE recent news article related to each bill or Virginia data centers in general.

    Calculate the 'sentiment_score' (1-100) using this strict rubric:
    - Base score is 30.
    - If status contains "Passed" or "Approved", add 30.
    - If status contains "unanimously" or "Governor", add 30.
    - If status contains "Stalled", "Failed", "Left in", or "Stricken", subtract 20.
    
    Provide a JSON list. Each object in the list must have exactly these keys:
    'id' (string),
    'headline' (string, a clear 3-8 word summary of the bill's intent),
    'full_summary' (string, a concise paragraph describing the impact),
    'status' (string, the exact LegiScan status provided),
    'sentiment_score' (number 1-100 based on the rubric above),
    'supporters' (string),
    'opponents' (string),
    'news_headline' (string, a 5-10 word headline of the news article you found via search),
    'news_summary' (string, a 2-sentence summary of the article),
    'news_link' (string, the URL to the news article).
    """
    
    response = model.generate_content(prompt)
    return json.loads(response.text)

if __name__ == "__main__":
    raw_bills = get_va_bill_data()
    
    print("Analyzing with Gemini & Google Search...")
    analyzed_data = analyze_with_ai(raw_bills)
    
    with open('data.json', 'w') as f:
        json.dump(analyzed_data, f, indent=4)
    
    print("Success! data.json updated.")
