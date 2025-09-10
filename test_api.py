"""
Test script for 68GB Game API
"""
import asyncio
import httpx
import json
from datetime import datetime

# API base URL - change this to your deployed URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

async def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

async def test_root_endpoint():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

async def test_games_list():
    """Test games list endpoint"""
    print("🔍 Testing games list...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/games")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()

async def test_game_info():
    """Test game info endpoints"""
    games = ["tai_xiu", "ban_do"]
    
    for game in games:
        print(f"🔍 Testing {game} info...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/games/{game}")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()

async def test_latest_results():
    """Test latest results endpoints"""
    games = ["tai_xiu", "ban_do"]
    
    for game in games:
        print(f"🔍 Testing {game} latest results...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/games/{game}/latest")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()

async def test_current_results():
    """Test current results endpoints (live crawl)"""
    games = ["tai_xiu", "ban_do"]
    
    for game in games:
        print(f"🔍 Testing {game} current results (live crawl)...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(f"{API_BASE}/games/{game}/current")
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except httpx.TimeoutException:
                print("⚠️ Request timed out (this is normal for live crawling)")
            except Exception as e:
                print(f"❌ Error: {e}")
            print()

async def test_stats():
    """Test stats endpoint"""
    print("🔍 Testing stats...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()

async def test_notification():
    """Test notification endpoint"""
    print("🔍 Testing notification...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/test-notification")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()

async def test_invalid_game():
    """Test invalid game type"""
    print("🔍 Testing invalid game type...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/games/invalid_game/latest")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()

async def main():
    """Run all tests"""
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_root_endpoint,
        test_games_list,
        test_game_info,
        test_latest_results,
        test_stats,
        test_notification,
        test_invalid_game,
        # test_current_results,  # Uncomment to test live crawling (slow)
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            print()
    
    print("✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    # Change BASE_URL to test deployed version
    # BASE_URL = "https://your-app-name.onrender.com"
    # API_BASE = f"{BASE_URL}/api/v1"
    
    asyncio.run(main())
