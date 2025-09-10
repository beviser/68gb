"""
Test script for game crawler functionality
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.game_crawler import GameCrawler
from services.notification_service import NotificationService
from config import GAME_TYPES

async def test_crawler_initialization():
    """Test crawler initialization"""
    print("🔍 Testing crawler initialization...")
    try:
        crawler = GameCrawler()
        print("✅ Crawler initialized successfully")
        return crawler
    except Exception as e:
        print(f"❌ Crawler initialization failed: {e}")
        return None

async def test_notification_service():
    """Test notification service"""
    print("🔍 Testing notification service...")
    try:
        notification_service = NotificationService()
        await notification_service.send_test_notification()
        print("✅ Notification service test completed")
    except Exception as e:
        print(f"❌ Notification service test failed: {e}")

async def test_single_crawl():
    """Test single crawl for each game type"""
    print("🔍 Testing single crawl for each game type...")
    
    crawler = GameCrawler()
    
    for game_type in GAME_TYPES.keys():
        print(f"  Testing {game_type}...")
        try:
            result = await crawler._crawl_game(game_type)
            if result:
                print(f"  ✅ {game_type}: {result}")
            else:
                print(f"  ⚠️ {game_type}: No result (this is normal if site is protected)")
        except Exception as e:
            print(f"  ❌ {game_type}: {e}")

async def test_data_processing():
    """Test data processing functions"""
    print("🔍 Testing data processing functions...")
    
    crawler = GameCrawler()
    
    # Test MD5 generation
    test_data = "test_result_123"
    md5_hash = crawler._generate_md5(test_data)
    print(f"  MD5 for '{test_data}': {md5_hash}")
    
    # Test data validation
    valid_data = {
        "result": "tai",
        "timestamp": "2023-09-08T10:30:45",
        "session_id": "test_session"
    }
    
    invalid_data = {
        "invalid_field": "value"
    }
    
    is_valid_1 = crawler._is_valid_game_data(valid_data, "tai_xiu")
    is_valid_2 = crawler._is_valid_game_data(invalid_data, "tai_xiu")
    
    print(f"  Valid data check: {is_valid_1} (should be True)")
    print(f"  Invalid data check: {is_valid_2} (should be False)")

async def test_html_parsing():
    """Test HTML parsing functionality"""
    print("🔍 Testing HTML parsing...")
    
    crawler = GameCrawler()
    
    # Test HTML with game data
    test_html = '''
    <html>
        <body>
            <div class="game-result" data-result='{"result": "tai", "md5": "abc123"}'>
                Game Result: Tai
            </div>
            <script>
                var gameData = {"result_md5": "def456", "session": "test_session"};
            </script>
        </body>
    </html>
    '''
    
    try:
        parsed_data = crawler._parse_html_for_game_data(test_html, "tai_xiu")
        if parsed_data:
            print(f"  ✅ Parsed data: {parsed_data}")
        else:
            print("  ⚠️ No data parsed from test HTML")
    except Exception as e:
        print(f"  ❌ HTML parsing failed: {e}")

async def test_text_data_creation():
    """Test creating game data from text"""
    print("🔍 Testing text data creation...")
    
    crawler = GameCrawler()
    
    test_texts = [
        "Result: 123",
        "Tai Xiu: 456 - Session: abc",
        "Game ended with result 789"
    ]
    
    for text in test_texts:
        try:
            data = crawler._create_game_data_from_text(text, "tai_xiu")
            print(f"  Text: '{text}' -> {data}")
        except Exception as e:
            print(f"  ❌ Failed to create data from '{text}': {e}")

async def main():
    """Run all crawler tests"""
    print("🚀 Starting Crawler Tests")
    print("=" * 50)
    
    # Initialize database (create tables if needed)
    try:
        from database import init_database
        await init_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    print()
    
    tests = [
        test_crawler_initialization,
        test_notification_service,
        test_data_processing,
        test_html_parsing,
        test_text_data_creation,
        test_single_crawl,  # This one might take longer
    ]
    
    for test in tests:
        try:
            await test()
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            print()
    
    print("✅ All crawler tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
