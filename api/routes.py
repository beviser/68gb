"""
API routes for 68GB Game data
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import time

from database import get_db, get_latest_results, GameResult, APILog
from config import settings, GAME_TYPES
from services.notification_service import NotificationService

router = APIRouter()

# Global instances
notification_service = NotificationService()

@router.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Log the request (async, don't wait)
    try:
        from database import log_api_request
        await log_api_request(
            endpoint=str(request.url.path),
            method=request.method,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", ""),
            response_status=response.status_code,
            response_time=process_time
        )
    except Exception:
        pass  # Don't fail the request if logging fails
    
    return response

@router.get("/games")
async def get_supported_games():
    """Get list of supported games"""
    return {
        "games": [
            {
                "type": game_type,
                "name": config["name"],
                "endpoint": f"/games/{game_type}"
            }
            for game_type, config in GAME_TYPES.items()
        ]
    }

@router.get("/games/{game_type}")
async def get_game_info(game_type: str):
    """Get information about a specific game"""
    if game_type not in GAME_TYPES:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    config = GAME_TYPES[game_type]
    return {
        "game_type": game_type,
        "name": config["name"],
        "endpoints": {
            "latest": f"/games/{game_type}/latest",
            "history": f"/games/{game_type}/history",
            "current": f"/games/{game_type}/current"
        }
    }

@router.get("/games/{game_type}/latest")
async def get_latest_game_result(game_type: str, limit: int = Query(1, ge=1, le=100)):
    """Get latest results for a specific game"""
    if game_type not in GAME_TYPES:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    try:
        results = await get_latest_results(game_type=game_type, limit=limit)
        
        if not results:
            return {
                "game_type": game_type,
                "results": [],
                "message": "No results found"
            }
        
        formatted_results = []
        for result in results:
            try:
                import json
                result_data = json.loads(result.result_data) if result.result_data else {}
            except:
                result_data = {}
            
            formatted_results.append({
                "id": result.id,
                "game_type": result.game_type,
                "session_id": result.session_id,
                "result_md5": result.result_md5,
                "result_data": result_data,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            })
        
        return {
            "game_type": game_type,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@router.get("/games/{game_type}/history")
async def get_game_history(
    game_type: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    from_date: Optional[str] = Query(None, description="ISO format date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="ISO format date (YYYY-MM-DD)")
):
    """Get historical results for a specific game"""
    if game_type not in GAME_TYPES:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    try:
        # For now, use the simple get_latest_results function
        # In a real implementation, you'd add date filtering to the database query
        results = await get_latest_results(game_type=game_type, limit=limit)
        
        formatted_results = []
        for result in results[offset:]:
            try:
                import json
                result_data = json.loads(result.result_data) if result.result_data else {}
            except:
                result_data = {}
            
            formatted_results.append({
                "id": result.id,
                "game_type": result.game_type,
                "session_id": result.session_id,
                "result_md5": result.result_md5,
                "result_data": result_data,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            })
        
        return {
            "game_type": game_type,
            "results": formatted_results,
            "count": len(formatted_results),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.get("/games/{game_type}/current")
async def get_current_game_result(game_type: str):
    """Get current/live result for a specific game (triggers fresh crawl)"""
    if game_type not in GAME_TYPES:
        raise HTTPException(status_code=404, detail="Game type not found")
    
    try:
        # Import here to avoid circular imports
        from crawler.game_crawler import GameCrawler
        
        crawler = GameCrawler()
        current_result = await crawler._crawl_game(game_type)
        
        if not current_result:
            # Fallback to latest from database
            results = await get_latest_results(game_type=game_type, limit=1)
            if results:
                result = results[0]
                try:
                    import json
                    result_data = json.loads(result.result_data) if result.result_data else {}
                except:
                    result_data = {}
                
                return {
                    "game_type": game_type,
                    "result": {
                        "id": result.id,
                        "session_id": result.session_id,
                        "result_md5": result.result_md5,
                        "result_data": result_data,
                        "timestamp": result.timestamp.isoformat() if result.timestamp else None
                    },
                    "source": "database",
                    "message": "Live crawl failed, returning latest from database"
                }
            else:
                raise HTTPException(status_code=404, detail="No current result available")
        
        return {
            "game_type": game_type,
            "result": current_result,
            "source": "live",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting current result: {str(e)}")

@router.get("/stats")
async def get_api_stats():
    """Get API usage statistics"""
    try:
        # Get basic stats from database
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import func
        from database import engine, GameResult, APILog
        
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Game results stats
            total_results = db.query(func.count(GameResult.id)).scalar() or 0
            
            game_counts = {}
            for game_type in GAME_TYPES.keys():
                count = db.query(func.count(GameResult.id)).filter(
                    GameResult.game_type == game_type
                ).scalar() or 0
                game_counts[game_type] = count
            
            # API usage stats (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            api_calls_24h = db.query(func.count(APILog.id)).filter(
                APILog.timestamp >= yesterday
            ).scalar() or 0
            
            return {
                "total_game_results": total_results,
                "results_by_game": game_counts,
                "api_calls_last_24h": api_calls_24h,
                "supported_games": list(GAME_TYPES.keys()),
                "server_time": datetime.now().isoformat()
            }
        finally:
            db.close()
            
    except Exception as e:
        return {
            "error": f"Could not retrieve stats: {str(e)}",
            "supported_games": list(GAME_TYPES.keys()),
            "server_time": datetime.now().isoformat()
        }

@router.post("/test-notification")
async def test_notification():
    """Test notification system"""
    try:
        await notification_service.send_test_notification()
        return {"message": "Test notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test notification: {str(e)}")

@router.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "database": "connected",
        "supported_games": list(GAME_TYPES.keys())
    }
