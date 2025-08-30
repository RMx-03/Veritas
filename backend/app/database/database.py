from supabase import create_client, Client
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialize Supabase client
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase initialization error: {e}")

# Helper to run blocking DB operations in a thread
async def _db_exec(callable_):
    return await asyncio.to_thread(callable_)

async def save_analysis_result(analysis_id: str, analysis_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
    """
    Save analysis result to Supabase database
    """
    if not supabase:
        print("Supabase not configured - analysis not saved")
        return False
    
    try:
        # Prepare data for database
        db_data = {
            "id": analysis_id,
            "filename": filename or "unknown",
            "analysis_data": analysis_data,
            "nutrition_facts": analysis_data.get("nutrition_facts", {}),
            "overall_score": analysis_data.get("health_score", {}).get("score", 0),
            "health_recommendation": analysis_data.get("recommendations", []),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Insert into database
        try:
            result = await _db_exec(lambda: supabase.table("analysis_results").insert(db_data).execute())
            
            if result.data:
                print(f"Analysis {analysis_id} saved successfully")
                return True
            else:
                print(f"Failed to save analysis {analysis_id}")
                return False
        except Exception as db_error:
            # Fallback to local storage if database table doesn't exist
            print(f"Database save failed, using local storage: {db_error}")
            # Prefer in-memory async fallback to avoid blocking
            mem_ok = await save_analysis_local_memory(analysis_id, analysis_data, filename)
            # Also try to persist to disk for durability (best-effort)
            try:
                file_ok = save_analysis_local_file(analysis_id, analysis_data, filename or "unknown")
            except Exception as _:
                file_ok = False
            return bool(mem_ok or file_ok)
            
    except Exception as e:
        print(f"Database save error: {e}")
        return False

def save_analysis_local_file(analysis_id: str, analysis_data: Dict[str, Any], filename: str = "") -> bool:
    """
    Fallback: Save analysis to local JSON file when database is unavailable
    """
    try:
        import json
        import os
        from datetime import datetime
        
        # Create local storage directory
        storage_dir = "local_analysis_storage"
        os.makedirs(storage_dir, exist_ok=True)
        
        # Prepare data for local storage
        local_data = {
            "analysis_id": analysis_id,
            "filename": filename,
            "analysis_data": analysis_data,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "storage_type": "local_fallback"
        }
        
        # Save to JSON file
        file_path = os.path.join(storage_dir, f"{analysis_id}.json")
        with open(file_path, 'w') as f:
            json.dump(local_data, f, indent=2)
        
        print(f"Analysis {analysis_id} saved locally to {file_path}")
        return True
        
    except Exception as e:
        print(f"Local storage save error: {e}")
        return False

async def get_analysis_history(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve analysis history from database
    """
    if not supabase:
        return []
    
    try:
        result = await _db_exec(lambda: supabase.table("analysis_results").select(
            "id, filename, overall_score, health_recommendation, created_at"
        ).order("created_at", desc=True).limit(limit).execute())
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"Database fetch error: {e}")
        return []

async def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve specific analysis by ID
    """
    if not supabase:
        return None
    
    try:
        result = await _db_exec(lambda: supabase.table("analysis_results").select("*").eq("id", analysis_id).execute())
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
        
    except Exception as e:
        print(f"Database fetch error: {e}")
        return None

async def update_analysis_result(analysis_id: str, updated_data: Dict[str, Any]) -> bool:
    """
    Update existing analysis result
    """
    if not supabase:
        return False
    
    try:
        updated_data["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        result = await _db_exec(lambda: supabase.table("analysis_results").update(updated_data).eq("id", analysis_id).execute())
        
        return bool(result.data)
        
    except Exception as e:
        print(f"Database update error: {e}")
        return False

async def delete_analysis_result(analysis_id: str) -> bool:
    """
    Delete analysis result from database
    """
    if not supabase:
        return False
    
    try:
        result = await _db_exec(lambda: supabase.table("analysis_results").delete().eq("id", analysis_id).execute())
        return bool(result.data)
        
    except Exception as e:
        print(f"Database delete error: {e}")
        return False

async def get_analysis_stats() -> Dict[str, Any]:
    """
    Get analysis statistics
    """
    if not supabase:
        return {}
    
    try:
        # Get total count
        count_result = await _db_exec(lambda: supabase.table("analysis_results").select("id", count="exact").execute())
        total_analyses = count_result.count if count_result.count else 0
        
        # Get average score
        score_result = await _db_exec(lambda: supabase.table("analysis_results").select("overall_score").execute())
        scores = [item["overall_score"] for item in score_result.data if score_result.data]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_result = await _db_exec(lambda: supabase.table("analysis_results").select("id", count="exact").gte("created_at", week_ago).execute())
        recent_count = recent_result.count if recent_result.count else 0
        
        return {
            "totalAnalyses": total_analyses,
            "averageScore": round(avg_score, 1),
            "recentAnalyses": recent_count
        }
        
    except Exception as e:
        print(f"Database stats error: {e}")
        return {}

# Local fallback storage for when Supabase is not available
LOCAL_STORAGE = []

async def save_analysis_local_memory(analysis_id: str, analysis_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
    """
    Fallback: Save analysis to local storage
    """
    try:
        local_data = {
            "id": analysis_id,
            "filename": filename or "unknown",
            "analysis_data": analysis_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        LOCAL_STORAGE.append(local_data)
        
        # Keep only last 50 analyses in memory
        if len(LOCAL_STORAGE) > 50:
            LOCAL_STORAGE.pop(0)
        
        return True
        
    except Exception as e:
        print(f"Local storage error: {e}")
        return False

async def get_analysis_history_local(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fallback: Get analysis history from local storage
    """
    try:
        # Sort by created_at descending and limit results
        sorted_data = sorted(LOCAL_STORAGE, key=lambda x: x["created_at"], reverse=True)
        return sorted_data[:limit]
        
    except Exception as e:
        print(f"Local storage fetch error: {e}")
        return []
