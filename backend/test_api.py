"""
Simple test script for the GitHub Chat API.
Make sure the server is running (uvicorn main:app --reload) before running this script.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_healthcheck():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/healthcheck")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_initialize_repo(owner: str, repo: str):
    """Test initializing a repository."""
    print(f"📦 Initializing repository {owner}/{repo}...")
    response = requests.post(
        f"{BASE_URL}/api/repository/initialize",
        json={"owner": owner, "repo": repo}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        print(f"Summary: {data['summary'][:200]}...")
        print(f"Tree (first 500 chars): {data['tree'][:500]}...\n")
        return True
    else:
        print(f"Error: {response.text}\n")
        return False


def test_chat(owner: str, repo: str, query: str, history=None):
    """Test sending a chat query."""
    if history is None:
        history = []
    
    print(f"💬 Sending query: '{query}'...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "owner": owner,
            "repo": repo,
            "query": query,
            "history": history
        }
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response'][:500]}...")
        print(f"History length: {len(data['history'])}\n")
        return data
    else:
        print(f"Error: {response.text}\n")
        return None


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 GitHub Chat API Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    if not test_healthcheck():
        print("❌ Health check failed! Make sure the server is running.")
        print("Run: uvicorn main:app --reload")
        return
    
    print("✅ Health check passed!\n")
    
    # Test 2: Initialize a small repository
    owner = "rtyley"
    repo = "small-test-repo"
    
    if not test_initialize_repo(owner, repo):
        print("❌ Repository initialization failed!")
        return
    
    print("✅ Repository initialization passed!\n")
    
    # Test 3: Send a chat query
    query1 = "What is this repository about?"
    result1 = test_chat(owner, repo, query1)
    
    if not result1:
        print("❌ First chat query failed!")
        return
    
    print("✅ First chat query passed!\n")
    
    # Test 4: Send a follow-up query with history
    query2 = "What technologies does it use?"
    result2 = test_chat(owner, repo, query2, history=result1["history"])
    
    if not result2:
        print("❌ Second chat query failed!")
        return
    
    print("✅ Second chat query passed!\n")
    
    print("=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

