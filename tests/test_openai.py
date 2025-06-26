import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def test_chat_api():
    """Test the Chat API"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say hello in exactly 5 words"}
            ],
            max_tokens=20
        )
        print("✅ Chat API Test Successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Chat API Test Failed: {e}")
        return False

def test_embedding_api():
    """Test the Embedding API"""
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="This is a test sentence for embeddings."
        )
        embedding = response.data[0].embedding
        print("✅ Embedding API Test Successful!")
        print(f"Embedding length: {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"❌ Embedding API Test Failed: {e}")
        return False

def check_account_info():
    """Check your account limits and usage"""
    try:
        # Note: This endpoint might not be available in all API versions
        print("\n📊 Account Information:")
        print("Go to https://platform.openai.com/account/usage to check usage")
        print("Go to https://platform.openai.com/account/limits to check limits")
    except Exception as e:
        print(f"Could not fetch account info: {e}")

if __name__ == "__main__":
    print("🧪 Testing OpenAI Configuration...\n")
    
    # Check if API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Make sure your .env file contains the API key")
        exit(1)
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format - should start with 'sk-'")
        exit(1)
    
    print(f"🔑 API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    
    # Run tests
    chat_success = test_chat_api()
    embedding_success = test_embedding_api()
    
    if chat_success and embedding_success:
        print("\n🎉 All OpenAI tests passed! You're ready to go!")
    else:
        print("\n❌ Some tests failed. Check your API key and billing.")
    
    check_account_info()