import requests
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def test_chatbot():
    """Quick verification that chatbot works after cleanup"""
    
    tests = [
        ("google package", "Should return Google package info"),
        ("companies allowing backlogs", "Should list backlog-friendly companies"),
        ("how many tier 2 companies", "Should return tier-2 count"),
        ("amazon cgpa", "Should return Amazon CGPA requirement"),
        ("placement rules", "Should return placement policy"),
    ]
    
    print("="*60)
    print("POST-CLEANUP VERIFICATION TEST")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for query, description in tests:
        try:
            response = requests.post(RASA_URL, json={"sender": "verify", "message": query}, timeout=10)
            bot_text = response.json()[0].get('text', '') if response.json() else ''
            
            if "sorry" not in bot_text.lower() and "didn't" not in bot_text.lower() and bot_text:
                print(f"✅ PASS: {description}")
                print(f"   Query: {query}")
                print(f"   Response: {bot_text[:60]}...")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Query: {query}")
                print(f"   Response: {bot_text[:60]}...")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: {description}")
            print(f"   Query: {query}")
            print(f"   Error: {str(e)[:60]}...")
            failed += 1
        print()
    
    print("="*60)
    print(f"RESULTS: {passed}/{len(tests)} passed")
    print("="*60)
    
    return passed == len(tests)

if __name__ == "__main__":
    success = test_chatbot()
    sys.exit(0 if success else 1)
