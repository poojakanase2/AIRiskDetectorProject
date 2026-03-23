from fastapi import FastAPI, BackgroundTasks, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from simulation import RiskSimulator, LogAnalyzer, AutoFixer, CICollector
from database import init_db, SessionLocal, RiskAssessmentRecord, LogAnalysisRecord, get_db
import asyncio
import os
import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import tempfile

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
# Initialize autonomous settings
simulator.config["autonomous_healing"] = True
simulator.config["monitor_interval_sec"] = 45

log_analyzer = LogAnalyzer()
autofixer = AutoFixer()

# Track which jobs we are currently investigating
active_healing_jobs = set()
REMEDIATION_LOG = os.path.join(tempfile.gettempdir(), "remediation.log")

async def autonomous_healing_monitor():
    """Background task that polls Jenkins and performs autonomous repairs."""
    print("[AUTONOMOUS] Starting Jenkins Self-Healing Engine...")
    while True:
        if simulator.config.get("autonomous_healing"):
            try:
                # 1. Fetch Failed Jobs
                failed_jobs = await asyncio.to_thread(CICollector.get_failed_jenkins_jobs)
                
                for job_id in failed_jobs:
                    if job_id in active_healing_jobs:
                        continue
                    
                    print(f"[AUTONOMOUS] Detected FAILURE in job: {job_id}. Initiating AI repair...")
                    active_healing_jobs.add(job_id)
                    
                    try:
                        # 2. Fetch Logs
                        logs = await asyncio.to_thread(CICollector.fetch_logs, "Jenkins", job_id)
                        
                        # 3. Analyze Logs
                        analysis = await asyncio.to_thread(log_analyzer.analyze, logs)
                        
                        # 4. Apply Auto-Fix
                        fix_result = await asyncio.to_thread(autofixer.run_auto_remediation, analysis, job_id, "Jenkins")
                        
                        # 5. Log Result
                        print(f"[AUTONOMOUS] Repair complete for {job_id}: {fix_result.get('execution_status')}")
                        
                        # Update global stats
                        simulator.update_remediation_stats(
                            "Jenkins", 
                            fix_result.get("execution_status", "Manual Fix Required")
                        )
                    except Exception as e:
                        print(f"[AUTONOMOUS] Error repairing {job_id}: {e}")
                    finally:
                        # Wait some time before handling this job again if it stays failed
                        # In real world we might want tracking of 'fix attempts' to avoid loops
                        pass
                
                # Cleanup active healing set (only jobs that ARE NOT in failed list anymore)
                all_current_failed = set(failed_jobs)
                for job in list(active_healing_jobs):
                    if job not in all_current_failed:
                        print(f"[AUTONOMOUS] Job {job} is now recovered. Clearing from active watch.")
                        active_healing_jobs.remove(job)

            except Exception as e:
                print(f"[AUTONOMOUS] Monitor Loop Error: {e}")
        
        await asyncio.sleep(int(simulator.config.get("monitor_interval_sec", 45)))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_healing_monitor())

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
    category: Optional[str] = "Unknown"
    detected_tool: Optional[str] = "Unknown"
    root_cause: Optional[str] = "Unknown"
    execution_status: Optional[str] = "N/A"
    confidence_score: Optional[float] = 0.0
    analysis_source: Optional[str] = "Rule Engine"
    auto_fix_available: Optional[bool] = False
    auto_fix_command: Optional[str] = ""
    manual_fix_steps: Optional[str] = ""
    retry_status: Optional[str] = "N/A"
    pipeline_source: Optional[str] = "Unknown"
    remediation_mode: Optional[str] = "Standard"
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
async def simulate_pipeline(auto_fix: bool = False):
    steps = ["Build", "Security Scan", "Unit Tests", "Integration Tests"]
    results = []
    
    for step in steps:
        # Simulate the step behavior
        step_result = simulator.simulate_pipeline_step(step)
        results.append(step_result)
        
        if step_result["status"] == "FAILED":
            if auto_fix:
                print(f"[SIMULATION] Auto-fixing failure in step: {step}")
                # Analyze failure logs
                try:
                    analysis = await asyncio.wait_for(
                        asyncio.to_thread(log_analyzer.analyze, step_result["logs"]),
                        timeout=30.0
                    )
                    # Run auto-remediation
                    fix_result = await asyncio.wait_for(
                        asyncio.to_thread(autofixer.run_auto_remediation, analysis, "sim-job-123", step_result["source"]),
                        timeout=15.0
                    )
                    step_result["remediation"] = fix_result
                    
                    # Update monitoring stats
                    simulator.update_remediation_stats(
                        step_result["source"],
                        fix_result.get("execution_status", "Manual Fix Required")
                    )
                except Exception as e:
                    print(f"[SIMULATION] Auto-fix failed to execute: {e}")
                    step_result["remediation_error"] = str(e)
            
            # Stop pipeline on failure
            break
            
    return results

@app.post("/api/remediate-job", response_model=AutoFixResponse)
async def remediate_job(request: PullRemediationRequest):
    """
    Pull-based remediation: Fetches logs, analyzes them, and attempts a fix.
    """
    print(f"[API] Pull remediation request for {request.source} job: {request.job_id}")
    
    # 1. Fetch Logs
    try:
        with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Pull remediation START for {request.job_id}")
        logs = await asyncio.to_thread(CICollector.fetch_logs, request.source, request.job_id)
        if not logs or "[ERROR]" in logs:
            error_msg = logs if logs else "Failed to fetch logs from Jenkins."
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Log fetch FAILED: {error_msg}")
            return {
                "execution_status": "Remediation Aborted",
                "retry_status": "Log Fetch Error",
                "root_cause": error_msg,
                "original_log": logs or "Log capture failed."
            }
        
        with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Logs fetched: {len(logs)} bytes")
            
        # 2. Analyze Logs
        try:
            analysis = await asyncio.wait_for(
                asyncio.to_thread(log_analyzer.analyze, logs),
                timeout=30.0
            )
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Analysis OK: {analysis.get('category')}")
        except Exception as e:
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Analysis FAILED: {e}")
            analysis = log_analyzer._fallback_result(logs)
            analysis["category"] = "Analysis Error"
            analysis["root_cause"] = f"AI analysis timed out or failed: {str(e)}"

        # 3. Apply Auto-Fix
        try:
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Starting Fixer...")
            fix_result = await asyncio.wait_for(
                asyncio.to_thread(autofixer.run_auto_remediation, analysis, request.job_id, request.source),
                timeout=20.0
            )
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Fix result: {fix_result.get('execution_status')}")
        except Exception as e:
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Fixer CRASHED: {e}")
            return {
                "execution_status": "Remediation Engine Error",
                "retry_status": "Internal Failure",
                "root_cause": f"AutoFixer encountered an error: {str(e)}",
                "original_log": logs
            }
        
        # Update stats
        simulator.update_remediation_stats(
            request.source,
            fix_result.get("execution_status", "Manual Fix Required")
        )
        
        # Include logs in the response so UI can show them
        fix_result["original_log"] = logs
        return fix_result

    except Exception as e:
        with open("/tmp/remediation.log", "a") as f: f.write(f"\n[API] CRITICAL FAILURE: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error during remediation: {str(e)}")

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
            log_snippet=log_text_raw[:500], # Store first 500 chars
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
        
        # Heuristic: Look for job name in Jenkins logs if common patterns exist
        if not detected_job:
            job_match = re.search(r"job/([\w-]+)/", request.log_text)
            if job_match:
                detected_job = job_match.group(1)
            elif "Started by" in request.log_text:
                # If it's a Jenkins log, but job name isn't in URL, check if we can find it
                # Often in Console Output it's not explicitly named unless in URLs
                pass
        
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

@app.post("/api/admin/stress")
async def trigger_stress(mode: str):
    if mode == "RECOVERY":
        simulator.stress_mode = None
    else:
        simulator.stress_mode = mode
    return {"status": "success", "mode": mode}

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
                "assessment": assessment,
                "monitoring_stats": simulator.monitoring_stats
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
