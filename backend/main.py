from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from simulation import RiskSimulator, LogAnalyzer, AutoFixer, CICollector
from database import init_db, SessionLocal, RiskAssessmentRecord, LogAnalysisRecord, get_db
import asyncio
import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Deployment Risk Detector")

# Initialize DB on startup
init_db()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = RiskSimulator()
log_analyzer = LogAnalyzer()
autofixer = AutoFixer()

class LogAnalysisRequest(BaseModel):
    log_text: str

class LogAnalysisResponse(BaseModel):
    category: str
    tool: str
    root_cause: str
    suggested_fix: str
    confidence: float
    commands: List[str]
    required_tools: List[str]
    install_hints: dict
    prevention_tips: List[str]
    highlighted_lines: List[int]
    strategies: List[dict]
    correction: Optional[dict] = None
    manual_fix_steps: Optional[str] = None
    analysis_source: str = "AI Engine (Azure OpenAI)"
    pipeline_source: str = "Unknown"

class AutoFixRequest(BaseModel):
    log_text: str

class AutoFixResponse(BaseModel):
    category: str
    detected_tool: str
    root_cause: str
    auto_fix_available: bool
    retry_status: str
    pipeline_source: str
    original_log: Optional[str] = None
    highlighted_lines: List[int] = []

class PullRemediationRequest(BaseModel):
    source: str  # e.g., "Jenkins"
    job_id: str

@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dashboard.html"))

# Mount static files (JS, CSS) from the parent directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")), name="static")

@app.get("/api/admin/config")
async def get_config():
    return simulator.config

@app.post("/api/admin/config")
async def update_config(config: dict):
    # Basic validation
    if "risk_threshold" in config:
        simulator.config["risk_threshold"] = float(config["risk_threshold"])
    return simulator.config

@app.get("/api/monitoring")
async def get_monitoring():
    metrics = simulator.generate_metrics()
    return {
        "metrics": metrics,
        "assessment": simulator.assess_risk(metrics)
    }

@app.get("/api/history")
async def get_history(limit: int = 10):
    db = SessionLocal()
    try:
        records = db.query(RiskAssessmentRecord).order_by(RiskAssessmentRecord.timestamp.desc()).limit(limit).all()
        return [{"id": r.id, "timestamp": r.timestamp, "risk_score": r.risk_score, "status": r.status} for r in records]
    finally:
        db.close()

@app.get("/api/pipeline/simulate")
async def simulate_pipeline():
    steps = ["Build", "Security Scan", "Unit Tests", "Integration Tests"]
    results = []
    for step in steps:
        results.append(simulator.simulate_pipeline_step(step))
        if results[-1]["status"] == "FAILED":
            break
    return results

@app.post("/api/remediate-job", response_model=AutoFixResponse)
async def remediate_job(request: PullRemediationRequest):
    """
    Pull-based remediation: Fetches logs, analyzes them, and attempts a fix.
    """
    print(f"[API] Pull remediation request for {request.source} job: {request.job_id}")
    
    # 1. Fetch Logs
    logs = await asyncio.to_thread(CICollector.fetch_logs, request.source, request.job_id)
    if not logs or logs == "Default pipeline log snippet...":
        # Check if we were expecting real logs
        token = os.getenv("JENKINS_API_TOKEN")
        if request.source == "Jenkins" and not token:
            print("[WARNING] Jenkins API Token missing. Using simulated logs.")

    # 2. Analyze Logs
    try:
        analysis = await asyncio.wait_for(
            asyncio.to_thread(log_analyzer.analyze, logs),
            timeout=30.0
        )
    except Exception as e:
        print(f"[API] Pull analysis failed: {e}")
        analysis = log_analyzer._fallback_result(logs)
        analysis["category"] = "Analysis Error"
        analysis["root_cause"] = str(e)

    # 3. Apply Auto-Fix
    fix_result = await asyncio.wait_for(
        asyncio.to_thread(autofixer.run_auto_remediation, analysis, request.job_id, request.source),
        timeout=15.0
    )
    
    # Update stats
    simulator.update_remediation_stats(
        request.source,
        fix_result.get("execution_status", "Manual Fix Required")
    )
    
    # Include logs in the response so UI can show them
    fix_result["original_log"] = logs
    
    return fix_result

@app.post("/api/analyze-log", response_model=LogAnalysisResponse)
async def analyze_log(request: LogAnalysisRequest):
    print(f"[API] POST /api/analyze-log | Log length: {len(request.log_text)}")
    try:
        # Increased timeout for real Azure OpenAI calls
        analysis = await asyncio.wait_for(
            asyncio.to_thread(log_analyzer.analyze, request.log_text),
            timeout=30.0
        )
        print("[API] Log analysis successful.")
    except asyncio.TimeoutError:
        print("[API] Log analysis TIMED OUT after 30s.")
        analysis = log_analyzer._fallback_result(request.log_text)
        analysis["category"] = "Analysis Timeout"
        analysis["root_cause"] = "Analysis exceeded 30s limit. The AI service may be slow or unresponsive."
    except Exception as e:
        print(f"[API] Log analysis CRASHED: {str(e)}")
        analysis = log_analyzer._fallback_result(request.log_text)
        analysis["category"] = "Analysis Error"
        analysis["root_cause"] = f"An internal error occurred: {str(e)}"

    # Optional: Save to Database
    db = SessionLocal()
    try:
        log_text_raw = request.log_text
        record = LogAnalysisRecord(
            log_snippet=log_text_raw[0:500], # Store first 500 chars
            category=analysis["category"],
            root_cause=analysis["root_cause"],
            suggested_fix=analysis["suggested_fix"],
            commands=analysis["commands"],
            prevention_tips=analysis["prevention_tips"]
        )
        db.add(record)
        db.commit()
    finally:
        db.close()
        
    return analysis

@app.post("/api/autofix", response_model=AutoFixResponse)
async def autofix_pipeline(request: AutoFixRequest):
    print(f"[API] POST /api/autofix | Log length: {len(request.log_text)}")
    try:
        # Combined timeout for parsing + planning
        analysis = await asyncio.wait_for(
            asyncio.to_thread(log_analyzer.analyze, request.log_text),
            timeout=30.0
        )
        print(f"[API] Phase 1 (Parsing) complete: {analysis.get('category')}")
        
        # Step 2: AutoFixer analyzes environment and prepares the fix plan
        # Try to detect job name from logs if possible
        detected_job = "test-pipeline" if "test-pipeline" in request.log_text else None
        
        fix_result = await asyncio.wait_for(
            asyncio.to_thread(autofixer.run_auto_remediation, analysis, detected_job, analysis.get("pipeline_source")),
            timeout=10.0
        )
        print("[API] Phase 2 (Planning) complete. Sending response.")
        
        # Update monitoring stats
        simulator.update_remediation_stats(
            fix_result.get("pipeline_source", "Unknown"),
            fix_result.get("execution_status", "Manual Fix Required")
        )
        
        # Include log text for UI display
        fix_result["original_log"] = request.log_text
        return fix_result
    except Exception as e:
        print(f"[API] AutoFix error: {e}")
        return {
            "category": "AutoFix Failed",
            "detected_tool": "Unknown",
            "root_cause": str(e),
            "auto_fix_available": False,
            "auto_fix_command": "",
            "manual_fix_steps": "Error during automation. Please check logs.",
            "confidence_score": 0.0,
            "analysis_source": "Error Handler",
            "execution_status": "Failed",
            "retry_status": "No retry",
            "pipeline_source": "Unknown",
            "original_log": request.log_text
        }

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "AI Engine"}

@app.websocket("/ws/stats")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("New WebSocket connection accepted")
    try:
        while True:
            # Generate fresh metrics and assessment
            metrics = simulator.generate_metrics()
            assessment = simulator.assess_risk(metrics)
            
            # Use data from the monitoring DB potentially if needed
            
            await websocket.send_json({
                "metrics": metrics,
                "assessment": assessment
            })
            await asyncio.sleep(2)
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
