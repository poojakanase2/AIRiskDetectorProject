# AI Deployment Risk Detector - Project Analysis & Walkthrough

## Overall Architecture
The system is built as a split full-stack application. It features a scalable, asynchronous Python FastAPI backend orchestrating the intelligence and logic, with a responsive, client-rendered Vanilla HTML/JS/CSS frontend dashboard.

The application serves as an active **Deployment Risk Detector** and **Auto Remediation** tool capable of analyzing logs, pinpointing issues using heuristic-based intelligent analysis, providing cost-saving suggestions, detecting system configuration drifts, detecting code vulnerabilities, and automatically executing safe-listed remediation commands.

## Tech Stack Used
**Frontend:**
- HTML5
- CSS3 (Vanilla, native variables, modern glassmorphism UI)
- JavaScript (ES6+, asynchronous fetch, WebSocket API)
- Chart.js (Metrics visualization)
- Lucide Icons (Vector icons)

**Backend:**
- Python 3
- FastAPI (REST endpoints and WebSockets)
- Uvicorn (ASGI web server)
- SQLAlchemy (ORM mapping)
- SQLite (Local data persistence)
- Pydantic (Data validation and models)

## Implementation Workflow
1. **Server Initialization:** When the application runs, Uvicorn initializes the FastAPI app. [database.py](file:///d:/scratch/backend/database.py) spins up a SQLite connection to [risk_history.db](file:///d:/scratch/backend/risk_history.db) mapped with SQLAlchemy, effectively storing any past analyses.
2. **Dashboard Delivery:** To eliminate cross-origin complexity or separate port requirements, the root path (`/`) directly serves the [dashboard.html](file:///d:/scratch/frontend/dashboard.html) from the frontend directory. The `/static` route serves the corresponding JS and CSS.
3. **Real-time Telemetry (WebSocket):** Upon dashboard load, JavaScript issues a WebSocket request (`ws://localhost:8000/ws/stats`). On connection, [main.py](file:///d:/scratch/backend/main.py) begins calling methods on [RiskSimulator](file:///d:/scratch/backend/simulation.py#58-178) (from [simulation.py](file:///d:/scratch/backend/simulation.py)), retrieving generated CPU, Memory, Vulnerability, and Latency stats continuously at 1-second intervals.
4. **Assessment Pipeline:** Risk levels are actively assessed and flagged by the backend based on thresholds set by the client. Results update charts and badges dynamically in the UI.
5. **Autofix/Log-Analyzer Event Call:** Whenever a user pastes an error log and hits submit, a REST `/api/analyze-log` request is dispatched. [LogAnalyzer](file:///d:/scratch/backend/simulation.py#379-655) runs regex heuristics string-matching algorithms on the log to identify standard failures (such as Maven failures, PyPI errors, Docker crashes, tool misconfigurations). If AutoFix is requested, the system safely spins up [AutoFixer](file:///d:/scratch/backend/simulation.py#179-377), checks environmental compatibilities (Windows vs Linux) and executes an OS-aware subprocess from an allowed whitelist to auto-correct the environment issue.

## Folder Structure

```text
d:\scratch\
├── backend/
│   ├── main.py            # Main FastAPI server bridging APIs, WebSockets, and Static folders. Connects the dots.
│   ├── database.py        # Configures SQLAlchemy Engine and Sessions. Defines `RiskAssessmentRecord` and `LogAnalysisRecord` tables.
│   ├── simulation.py      # Core "AI" logics. Houses `RiskSimulator`, `SecurityScanner`, `DriftDetector`, `LogAnalyzer`, and the powerful `AutoFixer`.
│   ├── requirements.txt   # Lists project python dependencies.
│   └── risk_history.db    # (Generated File) SQLite persistent database.
└── frontend/
    ├── dashboard.html     # HTML Layout representing the multi-tab layout, metrics grids, and log forms.
    ├── app.js             # Client-side javascript performing dynamic DOM manipulation, chart refreshes, WS handling.
    └── style.css          # Rich stylesheet handling colors, grids, flexbox, glow effects, animations and fonts.
```

---

## Step-by-Step Project Walkthrough

Follow these instructions in order within your terminal/command line to boot up the application.

### 1. Change to the backend directory
All executions happen within the backend.
```powershell
cd d:\scratch\backend
```

### 2. (Optional) Create and activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Required Dependencies
Install all modules specified in [requirements.txt](file:///d:/scratch/backend/requirements.txt).
```powershell
pip install -r requirements.txt
```

### 4. Run the API and Web Server
Boot up the [main.py](file:///d:/scratch/backend/main.py) python script. By default, it manages starting Uvicorn bound to port 8000 on your system.
```powershell
python main.py
```
*(Alternative command if you wish to run with hot-reload enabled during development: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`)*

### 5. Access the Dashboard
Head over to your favorite web browser and navigate to:
[http://localhost:8000](http://localhost:8000)

### 6. Using the Tool
- **Overview Dashboard:** View the real-time telemetry feed updating the latency/error-rate charts via WebSockets.
- **Canary Deployment Simulation:** Click **Trigger AI-Safe Deployment** to sequentially pass mock stages (Build -> Security Scan -> Testing -> Deploy) and route traffic incrementally into a new node.
- **Stress Protocols:** Test risk assessments using the buttons on the bottom-right (Injection, Config Drift, Traffic Spike, Auto-Heal). Watch the AI catch the anomalies!
- **Log Analyzer:** Head into the **Log Analyzer tab**, provide a sample pipeline failure string (e.g. `npm ERR! code ERESOLVE` or `command not found: node`) and test out the **AI Pipeline Log Analyzer**, discovering why it broke along with safe commands you can run via **AUTO FIX PIPELINE** side panel.
