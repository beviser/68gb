"""
Local development runner for 68GB Game API
"""
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def setup_database():
    """Initialize database"""
    try:
        from database import init_database
        await init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

async def test_crawler():
    """Test crawler functionality"""
    try:
        from crawler.game_crawler import GameCrawler
        crawler = GameCrawler()
        
        print("🔍 Testing crawler...")
        results = await crawler.get_current_results()
        
        if results:
            print("✅ Crawler test successful")
            for game_type, result in results.items():
                if result:
                    print(f"  {game_type}: {result}")
                else:
                    print(f"  {game_type}: No result (normal if site is protected)")
        else:
            print("⚠️ No results from crawler (this is normal)")
        
        return True
    except Exception as e:
        print(f"❌ Crawler test failed: {e}")
        return False

async def test_notifications():
    """Test notification system"""
    try:
        from services.notification_service import NotificationService
        notification_service = NotificationService()
        
        print("🔔 Testing notifications...")
        await notification_service.send_test_notification()
        print("✅ Notification test completed")
        return True
    except Exception as e:
        print(f"❌ Notification test failed: {e}")
        return False

def run_server():
    """Run the FastAPI server"""
    import uvicorn
    from config import settings
    
    print(f"🚀 Starting server on {settings.HOST}:{settings.PORT}")
    print(f"📖 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

async def run_tests():
    """Run all tests"""
    print("🧪 Running local tests...")
    print("=" * 50)
    
    # Test database
    db_ok = await setup_database()
    if not db_ok:
        print("❌ Database setup failed, stopping tests")
        return False
    
    print()
    
    # Test crawler
    crawler_ok = await test_crawler()
    print()
    
    # Test notifications
    notification_ok = await test_notifications()
    print()
    
    print("=" * 50)
    if db_ok and crawler_ok and notification_ok:
        print("✅ All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed, but you can still run the server")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            asyncio.run(run_tests())
        elif command == "server":
            run_server()
        elif command == "setup":
            asyncio.run(setup_database())
        else:
            print("Usage:")
            print("  python run_local.py test    - Run tests")
            print("  python run_local.py server  - Start server")
            print("  python run_local.py setup   - Setup database only")
    else:
        print("🎮 68GB Game API Crawler - Local Development")
        print("=" * 50)
        print()
        
        # Run tests first
        test_result = asyncio.run(run_tests())
        
        print()
        response = input("Do you want to start the server? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            run_server()
        else:
            print("👋 Goodbye!")

if __name__ == "__main__":
    main()
