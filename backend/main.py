from fastapi import FastAPI, BackgroundTasks, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from simulation import RiskSimulator, LogAnalyzer, AutoFixer, CICollector
from database import init_db, SessionLocal, RiskAssessmentRecord, LogAnalysisRecord, HealingHistoryRecord, get_db
import asyncio
import os
import re
from datetime import datetime
from typing import Optional, List, Any
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
simulator.config["monitor_interval_sec"] = 60

log_analyzer = LogAnalyzer()
autofixer = AutoFixer()

# Track which jobs# Registry for background healing tasks
active_healing_jobs = set()
LAST_JOB_ID = "new-pipeline2" # Default fallback
REMEDIATION_LOG = os.path.join(tempfile.gettempdir(), "remediation.log")

async def autonomous_healing_monitor():
    """Background task that polls Jenkins and performs autonomous repairs."""
    print("[AUTONOMOUS] Starting Jenkins Self-Healing Engine...")
    while True:
        if simulator.config.get("autonomous_healing"):
            try:
                # 1. Fetch Failed Jobs
                config = CICollector.get_jenkins_config()
                if not config.get("token") or not config.get("url"):
                    # print("[AUTONOMOUS] Jenkins not configured. Skipping scan...")
                    await asyncio.sleep(30)
                    continue

                failed_jobs = await asyncio.to_thread(CICollector.get_failed_jenkins_jobs)
                
                for job_id in failed_jobs:
                    # Allow multiple attempts if needed (removing strict block)
                    print(f"[AUTONOMOUS] Detected FAILURE in job: {job_id}. Initiating AI repair...")
                    active_healing_jobs.add(job_id)
                    
                    try:
                        # 2. Fetch Logs
                        logs = await asyncio.to_thread(CICollector.fetch_logs, "Jenkins", job_id)
                        
                        # 3. Analyze Logs (Passing job_id for context)
                        analysis = await asyncio.to_thread(log_analyzer.analyze, logs, job_id)
                        
                        # [CHANGED] Background monitor now ONLY scans and analyzes.
                        # It no longer performs auto-remediation automatically.
                        print(f"[AUTONOMOUS] Analysis complete for {job_id}: {analysis.get('category')}")
                        
                        # Update global stats to reflect a failure was detected
                        simulator.monitoring_stats["failed_pipelines"] = len(failed_jobs)
                        
                    except Exception as e:
                        print(f"[AUTONOMOUS] Error analyzing {job_id}: {e}")
                
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
    tool: Any
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
    job_id: Optional[str] = None

class AutoFixResponse(BaseModel):
    category: Optional[str] = "Unknown"
    detected_tool: Optional[Any] = "Unknown"
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

class JenkinsConfig(BaseModel):
    url: str
    user: str
    token: str

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

@app.get("/api/jenkins/config")
async def get_jenkins_config():
    return CICollector.get_jenkins_config()

@app.post("/api/jenkins/config")
async def update_jenkins_config(config: JenkinsConfig):
    # Update in-memory
    CICollector.set_jenkins_config(config.url, config.user, config.token)
    
    # Persist to .env to survive hot-reloads/restarts
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        # Update or add lines
        new_lines = []
        keys_to_update = {
            "JENKINS_URL": config.url.rstrip('/'),
            "JENKINS_USER": config.user,
            "JENKINS_API_TOKEN": config.token
        }
        
        found_keys = set()
        for line in lines:
            updated = False
            for key, val in keys_to_update.items():
                if line.strip().startswith(key) or line.strip().startswith(f"# {key}"):
                    new_lines.append(f"{key}={val}\n")
                    found_keys.add(key)
                    updated = True
                    break
            if not updated:
                new_lines.append(line)
        
        # Add keys that weren't in the file
        for key, val in keys_to_update.items():
            if key not in found_keys:
                new_lines.append(f"{key}={val}\n")
        
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        return {"status": "success", "message": "Jenkins configuration updated and persisted."}
    except Exception as e:
        print(f"[ERROR] Failed to persist config to .env: {e}")
        return {"status": "success", "message": "Jenkins configuration updated (memory only). Persistence error."}

@app.post("/api/jenkins/test")
async def test_jenkins_connection(config: JenkinsConfig):
    result = await asyncio.to_thread(CICollector.test_connection, config.url, config.user, config.token)
    if not result["success"]:
        # We don't raise 401/403 here because it's a test connection endpoint 
        # that should return the error message in the body for the UI
        pass
    return result

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
                        asyncio.to_thread(log_analyzer.analyze, step_result["logs"], "simulation-job"),
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
    Pull-based analysis: Fetches logs and analyzes them, but does NOT perform an auto-fix.
    The fix must be manually triggered via the 'Auto-Fix' button.
    """
    print(f"[API] Pull analysis request for {request.source} job: {request.job_id}")
    
    # 1. Fetch Logs
    try:
        with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Pull analysis START for {request.job_id}")
        logs = await asyncio.to_thread(CICollector.fetch_logs, request.source, request.job_id)
        if not logs or "[ERROR]" in logs:
            error_msg = logs if logs else "Failed to fetch logs from Jenkins."
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Log fetch FAILED: {error_msg}")
            return {
                "execution_status": "Analysis Aborted",
                "retry_status": "Log Fetch Error",
                "root_cause": error_msg,
                "original_log": logs or "Log capture failed."
            }
        
        with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Logs fetched: {len(logs)} bytes")
            
        # 2. Analyze Logs
        try:
            analysis = await asyncio.wait_for(
                asyncio.to_thread(log_analyzer.analyze, logs, request.job_id),
                timeout=30.0
            )
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Analysis OK: {analysis.get('category')}")
        except Exception as e:
            with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] Analysis FAILED: {e}")
            analysis = log_analyzer._fallback_result(logs)
            analysis["category"] = "Analysis Error"
            analysis["root_cause"] = f"AI analysis timed out or failed: {str(e)}"

        # Prepare a response that shows the analysis without execution results
        response = {
            "category": analysis.get("category", "Unknown"),
            "detected_tool": analysis.get("tool", "Unknown"),
            "root_cause": analysis.get("root_cause", "Unknown"),
            "execution_status": "Observation Mode (No Fix Applied)",
            "retry_status": "Manual Action Required",
            "auto_fix_available": len(analysis.get("commands", [])) > 0 or analysis.get("analyzer_file_correction") is not None,
            "auto_fix_command": analysis["commands"][0] if analysis.get("commands") else "",
            "manual_fix_steps": analysis.get("manual_fix_steps", "N/A"),
            "confidence_score": analysis.get("confidence", 0.0),
            "analysis_source": analysis.get("analysis_source", "AI Engine"),
            "pipeline_source": request.source,
            "original_log": logs,
            "highlighted_lines": analysis.get("highlighted_lines", [])
        }
        
        return response

    except Exception as e:
        with open(REMEDIATION_LOG, "a") as f: f.write(f"\n[API] CRITICAL FAILURE: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error during pull analysis: {str(e)}")

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
    print(f"[API] POST /api/autofix | JobID: {request.job_id} | Log length: {len(request.log_text)}")
    
    global LAST_JOB_ID
    if request.job_id: LAST_JOB_ID = request.job_id
    
    try:
        # Step 2: AutoFixer analyzes environment and prepares the fix plan
        # Priority: 1. Request Job ID, 2. Regex Detection, 3. Manual Fallback
        detected_job = request.job_id
        
        # Heuristic search if not explicitly provided
        if not detected_job:
            job_match = re.search(r"job/([\w-]+)/", request.log_text)
            if job_match:
                detected_job = job_match.group(1)
            elif "Building in workspace" in request.log_text:
                ws_match = re.search(r"workspace\\([\w-]+)", request.log_text)
                if ws_match: detected_job = ws_match.group(1)

        # Combined timeout for parsing + planning
        analysis = await asyncio.wait_for(
            asyncio.to_thread(log_analyzer.analyze, request.log_text, detected_job or "manual-upload"),
            timeout=30.0
        )
        
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
        
        # [NEW] Persist Remediation History to Database
        db = SessionLocal()
        try:
            record = HealingHistoryRecord(
                job_id=target_job,
                source=fix_result.get("pipeline_source", "Unknown"),
                category=fix_result.get("category", "Unknown"),
                root_cause=fix_result.get("root_cause", "Unknown"),
                execution_status=fix_result.get("execution_status", "N/A"),
                retry_status=fix_result.get("retry_status", "N/A"),
                confidence=fix_result.get("confidence_score", 0.0)
            )
            db.add(record)
            db.commit()
            print(f"[DB] Remediation history saved for {target_job}.")
        except Exception as db_err:
            print(f"[DB ERROR] Failed to save history: {db_err}")
        finally:
            db.close()

        # Step 3: TRIGGER BUILD EVERY TIME (Orange button requirement)
        target_job = detected_job or "manual-upload"
        
        # [NEW] Persist Remediation History to Database
        db = SessionLocal()
        try:
            record = HealingHistoryRecord(
                job_id=target_job,
                source=fix_result.get("pipeline_source", "Unknown"),
                category=fix_result.get("category", "Unknown"),
                root_cause=fix_result.get("root_cause", "Unknown"),
                execution_status=fix_result.get("execution_status", "N/A"),
                retry_status=fix_result.get("retry_status", "N/A"),
                confidence=fix_result.get("confidence_score", 0.0)
            )
            db.add(record)
            db.commit()
            print(f"[DB] Remediation history saved for {target_job}.")
        except Exception as db_err:
            print(f"[DB ERROR] Failed to save history: {db_err}")
        finally:
            db.close()

        if target_job != "manual-upload":
            print(f"[API] Auto-Fix Button: Force triggering build for {target_job}")
            CICollector.trigger_retry("Jenkins", target_job)
            fix_result["retry_status"] = f"Action Triggered for {target_job}. Build starting..."
        else:
            # Fallback if no job detected (just triggers first in list if available)
            all_jobs = CICollector.get_all_jobs()
            if all_jobs:
                CICollector.trigger_retry("Jenkins", all_jobs[0])
                fix_result["retry_status"] = f"Action Triggered for {all_jobs[0]} (Fallback)."

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

@app.get("/api/healing/history")
async def get_healing_history():
    """Returns the history of all remediation attempts."""
    db = SessionLocal()
    try:
        # Fetch last 50 remediation attempts
        records = db.query(HealingHistoryRecord).order_by(HealingHistoryRecord.timestamp.desc()).limit(50).all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "job_id": r.job_id,
                "source": r.source,
                "category": r.category,
                "root_cause": r.root_cause,
                "execution_status": r.execution_status,
                "retry_status": r.retry_status,
                "confidence": r.confidence
            } for r in records
        ]
    finally:
        db.close()

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
