import platform
import subprocess
import re
import json
import os
import random
import time
import hashlib
import requests
from typing import Dict, List, Optional
from openai import AzureOpenAI

class CICollector:
    """Simulates fetching logs from various CI/CD platforms, with real Jenkins integration."""
    
    @staticmethod
    def get_jenkins_config():
        return {
            "url": os.getenv("JENKINS_URL", "http://localhost:8080"),
            "user": os.getenv("JENKINS_USER", "admin"),
            "token": os.getenv("JENKINS_API_TOKEN", "")
        }

    @staticmethod
    def fetch_logs(source: str, job_id: str) -> str:
        """Fetch logs from CI/CD platforms. Uses real API for Jenkins if configured."""
        if source == "Jenkins":
            config = CICollector.get_jenkins_config()
            if config["token"]:
                try:
                    print(f"[COLLECTOR] Fetching REAL logs from Jenkins for {job_id}...")
                    # Jenkins API URL for console output
                    api_url = f"{config['url']}/job/{job_id}/lastBuild/consoleText"
                    response = requests.get(
                        api_url, 
                        auth=(config["user"], config["token"]),
                        timeout=10
                    )
                    if response.status_code == 200:
                        return response.text
                    else:
                        print(f"[ERROR] Jenkins API returned {response.status_code}")
                except Exception as e:
                    print(f"[ERROR] Failed to fetch Jenkins logs: {e}")

        # Fallback to simulated logs
        print(f"[COLLECTOR] Fetching simulated logs from {source} for ID {job_id}...")
        logs = {
            "Jenkins": f"Started by user admin\nRunning as SYSTEM\n[Pipeline] node\n[Pipeline] {{ (Build)\n... \nFATAL: Out of memory killer terminated the process.\n[Pipeline] }} \n[Pipeline] End of Pipeline",
            "GitHub Actions": f"Run actions/checkout@v2\n... \nError: Process completed with exit code 1. ModuleNotFoundError: No module named 'flask'",
            "GitLab CI": f"Running with gitlab-runner 14.0.0\n... \nnpm ERR! 404 'expresss@latest' is not in the npm registry\nERROR: Job failed: exit code 1",
            "ArgoCD": f"Project: default\nStatus: Sync Failed\n... \nkube-system: pod-failure-oom-killer\nEvents: \n  Type     Reason     Age                From               Message\n  ----     ------     ----               ----               -------\n  Warning  Unhealthy  10s (x3 over 30s)  kubelet            Container 'runner' failed liveness probe, will be restarted"
        }
        return logs.get(source, "Default pipeline log snippet...")

    @staticmethod
    def trigger_retry(source: str, job_id: str) -> bool:
        """Trigger platform specific reruns. Uses real API for Jenkins if configured."""
        if source == "Jenkins":
            config = CICollector.get_jenkins_config()
            if config["token"]:
                try:
                    print(f"[RETRY] Triggering REAL Jenkins rerun for {job_id} at {config['url']}...")
                    api_url = f"{config['url']}/job/{job_id}/build"
                    response = requests.post(
                        api_url,
                        auth=(config["user"], config["token"]),
                        timeout=10
                    )
                    print(f"[RETRY] Jenkins Response: {response.status_code}")
                    if response.status_code >= 400:
                        print(f"[RETRY] Jenkins Error Detail: {response.text[:200]}")
                    
                    return response.status_code in [200, 201, 202]
                except Exception as e:
                    print(f"[ERROR] Jenkins retry failed: {e}")
                    return False

        # Simulation fallback
        print(f"[RETRY] Triggering {source} simulated rerun for {job_id}...")
        return True

class SecurityScanner:
    def __init__(self):
        self.vulnerabilities = [
            {"id": "CVE-2024-1234", "level": "HIGH", "desc": "SQL Injection in auth module"},
            {"id": "CVE-2023-5678", "level": "CRITICAL", "desc": "Remote Code Execution in gateway"},
            {"id": "CVE-2024-9012", "level": "MEDIUM", "desc": "Cross-site scripting in UI components"},
            {"id": "CVE-2024-4455", "level": "LOW", "desc": "Insecure cookie flags"}
        ]

    def perform_scan(self) -> List[Dict]:
        """Simulates a security scan result."""
        # Randomly pick 0-3 vulnerabilities
        if random.random() > 0.3:
            return random.sample(self.vulnerabilities, random.randint(0, 3))
        return []

class DriftDetector:
    def __init__(self):
        self.configs = ["Memory Limit", "Timeout Policy", "VPC Gateway", "DB Connections", "IAM Roles"]
        
    def check_drift(self) -> List[Dict]:
        """Simulates configuration drift detection."""
        drifts = []
        if random.random() > 0.8: # 20% chance of drift
            config = random.choice(self.configs)
            drifts.append({
                "config": config,
                "status": "DRIFTED",
                "severity": "MEDIUM" if random.random() > 0.5 else "HIGH"
            })
        return drifts

class CostOptimizer:
    def __init__(self):
        self.strategies = [
            {"id": "COST-001", "name": "Downsize Over-provisioned Pods", "saving": "$450/mo"},
            {"id": "COST-002", "name": "Switch to Spot Instances", "saving": "$1,200/mo"},
            {"id": "COST-003", "name": "Cleanup Orphaned EBS Volumes", "saving": "$120/mo"},
            {"id": "COST-004", "name": "Optimize DynamoDB Throughput", "saving": "$300/mo"}
        ]
        
    def get_suggestions(self, metrics: Dict) -> List[Dict]:
        """Suggests cost optimizations based on resource utilization."""
        suggestions = []
        if metrics["cpu_usage"] < 30 and metrics["memory_usage"] < 40:
            suggestions.append(self.strategies[0])
            suggestions.append(self.strategies[1])
        elif metrics["active_connections"] < 500:
            suggestions.append(self.strategies[3])
        return suggestions

class RiskSimulator:
    def __init__(self):
        self.deployment_history = []
        self.security_scanner = SecurityScanner()
        self.drift_detector = DriftDetector()
        self.cost_optimizer = CostOptimizer()
        self.stress_mode = None
        self.platforms = ["Jenkins", "GitHub Actions", "GitLab CI", "ArgoCD"]
        self.config = {
            "risk_threshold": 0.6,
            "canary_steps": [10, 25, 50, 75, 100],
            "step_delay_ms": 1500
        }
        self.monitoring_stats = {
            "active_pipelines": random.randint(2, 8),
            "failed_pipelines": 0,
            "success_rate": 98.2,
            "total_remediations": 15,
            "recent_remediations": []
        }
        
    def generate_metrics(self) -> Dict:
        """Simulates real-time deployment metrics with stress injection."""
        base_metrics = {
            "timestamp": time.time(),
            "latency_ms": random.uniform(50, 150),
            "error_rate": random.uniform(0, 0.5),
            "cpu_usage": random.uniform(20, 50),
            "memory_usage": random.uniform(30, 55),
            "active_connections": random.randint(100, 1500),
            "vulnerabilities": [],
            "drifts": []
        }

        # Apply Stress Scenarios
        if self.stress_mode == "MALWARE":
            base_metrics["vulnerabilities"] = self.security_scanner.vulnerabilities # All of them!
        elif self.stress_mode == "DRIFT":
            base_metrics["drifts"] = [{"config": "IAM Roles", "status": "DRIFTED", "severity": "HIGH"}]
        elif self.stress_mode == "LATENCY":
            base_metrics["latency_ms"] = random.uniform(800, 1500)
            base_metrics["error_rate"] = random.uniform(10, 40)
            base_metrics["cpu_usage"] = 99.0
        elif self.stress_mode is None:
            # Natural occasional jitter
            if random.random() > 0.95:
                base_metrics["vulnerabilities"] = self.security_scanner.perform_scan()
                base_metrics["drifts"] = self.drift_detector.check_drift()
        
        # Dynamic monitoring updates
        current_active = self.monitoring_stats["active_pipelines"]
        if isinstance(current_active, int):
            self.monitoring_stats["active_pipelines"] = max(1, current_active + random.choice([-1, 0, 1]))
        
        if random.random() > 0.99:
            current_failed = self.monitoring_stats["failed_pipelines"]
            if isinstance(current_failed, int):
                self.monitoring_stats["failed_pipelines"] = current_failed + 1
        
        return base_metrics

    def update_remediation_stats(self, source: str, status: str):
        """Called when a remediation is attempted."""
        current_total = self.monitoring_stats["total_remediations"]
        if isinstance(current_total, int):
            self.monitoring_stats["total_remediations"] = current_total + 1
        
        current_rate = self.monitoring_stats["success_rate"]
        if isinstance(current_rate, (int, float)):
            if status == "Fix Applied Successfully":
                self.monitoring_stats["success_rate"] = min(99.9, float(current_rate) + 0.1)
            else:
                self.monitoring_stats["success_rate"] = max(70.0, float(current_rate) - 0.5)
        
        # Keep track of recent ones
        recent = self.monitoring_stats["recent_remediations"]
        if isinstance(recent, list):
            recent.insert(0, {
                "platform": source,
                "timestamp": time.time(),
                "status": status
            })
            # Slice manually if types are an issue
            new_recent = []
            for i in range(min(5, len(recent))):
                new_recent.append(recent[i])
            self.monitoring_stats["recent_remediations"] = new_recent

    def assess_risk(self, metrics: Dict) -> Dict:
        """Advanced correlation-based risk assessment."""
        score = 0.0
        reasons = []
        
        # 1. Metric-based risk
        if metrics["latency_ms"] > 350:
            score += 0.3
            reasons.append("Anomalous Latency Spike detected.")
        if metrics["error_rate"] > 2.5:
            score += 0.4
            reasons.append("Error rate exceeds safety threshold.")
        
        # 2. Security-based risk
        vulns = metrics.get("vulnerabilities", [])
        for v in vulns:
            if v["level"] == "CRITICAL":
                score += 0.6
                reasons.append(f"Security Block: Critical {v['id']} found.")
            elif v["level"] == "HIGH":
                score += 0.3
                reasons.append(f"Security Alert: High-severity {v['id']}.")

        # 3. Drift-based risk
        drifts = metrics.get("drifts", [])
        for d in drifts:
            risk_inc = 0.4 if d["severity"] == "HIGH" else 0.2
            score += risk_inc
            reasons.append(f"Config Drift: {d['config']} has deviated from baseline.")

        # 4. Correlation Logic (e.g. Latency + High CPU = Potential Leak)
        if metrics["cpu_usage"] > 85 and metrics["latency_ms"] > 300:
            score += 0.2
            reasons.append("Node Exhaustion: CPU/Latency correlation suggests resource leak.")
            
        # Normalize score to 0.0 - 1.0
        score = min(score, 1.0)
        
        status = "HEALTHY"
        threshold = float(self.config.get("risk_threshold", 0.6)) # type: ignore
        if score > threshold:
            status = "CRITICAL"
        elif score > (threshold / 2.0):
            status = "WARNING"
            
        return {
            "risk_score": float(f"{score:.2f}"),
            "status": status,
            "reasons": list(set(reasons)), # Deduplicate
            "recommendation": self.get_recommendation(status),
            "cost_suggestions": self.cost_optimizer.get_suggestions(metrics),
            "details": {
                "vuln_count": len(vulns),
                "drift_count": len(drifts),
                "has_critical": any(v["level"] == "CRITICAL" for v in vulns)
            }
        }

    def get_recommendation(self, status: str) -> str:
        if status == "CRITICAL":
            return "TRIGGER AUTOMATIC ROLLBACK"
        elif status == "WARNING":
            return "ENFORCE CANARY STRATEGY"
        return "PROCEED TO PRODUCTION"

    def simulate_pipeline_step(self, step: str) -> Dict:
        """Simulated results for CI/CD steps across different platforms."""
        source = random.choice(self.platforms)
        # Pipeline is slightly more prone to failure if it's the security scan or docker build
        fail_chance = 0.2 if step in ["Security Scan", "Docker Build", "Integration Tests"] else 0.08
        success = random.random() > fail_chance
        
        status = "SUCCESS" if success else "FAILED"
        if not success:
            current_failed = self.monitoring_stats.get("failed_pipelines", 0)
            if isinstance(current_failed, int):
                self.monitoring_stats["failed_pipelines"] = current_failed + 1
        
        # Generic logs with platform hints
        logs = f"[{source}] Executing step: {step}...\n"
        if success:
            logs += f"[{source}] ✓ Success. {step} completed in {random.uniform(1.0, 5.0):.1f}s"
        else:
            # Inject one of our known error patterns specifically formatted for the platform
            errors = [
                "FATAL: Out of memory killer terminated the process.",
                "Error: Process completed with exit code 1. ModuleNotFoundError: No module named 'flask'",
                "npm ERR! 404 'expresss@latest' is not in the npm registry",
                "Warning: Container 'runner' failed liveness probe, will be restarted (OOM)"
            ]
            error_msg = random.choice(errors)
            logs += f"[{source}] ✗ Error: {error_msg}\n"
            if source == "Jenkins": logs = f"Started by user admin\nRunning as SYSTEM\n[Pipeline] {step}\n{logs}\n[Pipeline] ERROR: {error_msg}"
            elif source == "GitHub Actions": logs = f"##[group]Run {step}\n{logs}\n##[error]Process completed with exit code 1.\n##[endgroup]"

        return {
            "step": step,
            "status": status,
            "duration": random.uniform(0.5, 3.0),
            "logs": logs,
            "source": source
        }

class AutoFixer:
    def __init__(self):
        self.os_type = platform.system()  # 'Windows', 'Linux', 'Darwin'

        # Safe DevOps command whitelist - must start with one of these
        # Restriction: Only allow safe installation/deployment commands for Auto-Remediation
        self.allowed_prefixes = [
            "pip install",
            "npm install",
            "docker build",
            "kubectl apply"
        ]

        # Destructive patterns that should NEVER run
        self.blocked_patterns = [
            r"rm\s+-rf\s+/$",
            r"rm\s+-rf\s+/\*",
            r"rmdir\s+/s\s+/q\s+[A-Za-z]:\\Windows",
            r"format\s+[A-Za-z]:",
            r"del\s+/[Ff]\s+.*system32",
            r"shutdown",
            r"mkfs\.",
            r"dd\s+if=",
        ]

    # ──────────────────────────────────────────────
    # Environment probing (Optimized: Tool Cache)
    # ──────────────────────────────────────────────
    _tool_cache = {}

    def check_tool(self, tool: str) -> bool:
        """Returns True if `tool` is available. Uses cache to prevent repeat subprocess runs."""
        if tool in self._tool_cache:
            return self._tool_cache[tool]
        
        print(f"[DEBUG] Probing environment for tool: {tool}")
        cmd_checker = "where" if self.os_type == "Windows" else "which"
        try:
            # Short timeout and no blocking calls during analysis
            proc = subprocess.run([cmd_checker, tool], capture_output=True, text=True, timeout=1)
            result = proc.returncode == 0
            self._tool_cache[tool] = result
            return result
        except Exception:
            self._tool_cache[tool] = False
            return False

    def get_environment(self) -> dict:
        # Only check tools once per execution
        tools_to_check = ["node", "npm", "mvn", "gradle", "docker", "kubectl", "python", "pip", "git"]
        available: list = []
        for tool in tools_to_check:
            if self.check_tool(tool):
                available.append(tool)
        return {
            "os": self.os_type,
            "tools": available
        }

    # ──────────────────────────────────────────────
    # Safety layer
    # ──────────────────────────────────────────────
    def is_safe(self, cmd: str) -> tuple:
        """Returns (is_safe: bool, reason: str)."""
        import re
        cmd_stripped = cmd.strip()

        # Block hardcoded dangerous patterns first
        for pattern in self.blocked_patterns:
            if re.search(pattern, cmd_stripped, re.IGNORECASE):
                return False, f"BLOCKED (destructive pattern): {pattern}"

        # Allow only whitelisted prefixes
        for prefix in self.allowed_prefixes:
            if cmd_stripped.startswith(prefix):
                return True, "OK"

        return False, f"BLOCKED (not in safe command list): {cmd_stripped[:60]}"

    # ──────────────────────────────────────────────
    # Command execution
    # ──────────────────────────────────────────────
    def execute_commands(self, commands: list) -> tuple:
        """Run a list of commands. Returns (success: bool, log: str)."""
        full_log = ""
        for cmd in commands:
            safe, reason = self.is_safe(cmd)
            full_log += f"\n  $ {cmd}\n"
            if not safe:
                full_log += f"  ⛔ {reason}\n"
                return False, full_log.strip()
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                if proc.stdout.strip():
                    full_log += proc.stdout
                if proc.stderr.strip():
                    full_log += f"  [STDERR] {proc.stderr.strip()}\n"
                if proc.returncode != 0:
                    full_log += f"  ↳ Exit code {proc.returncode} — command failed.\n"
                    return False, full_log.strip()
                else:
                    full_log += "  ✓ Command succeeded.\n"
            except subprocess.TimeoutExpired:
                full_log += "  ✗ Timed out after 20 s.\n"
                return False, full_log.strip()
            except Exception as e:
                full_log += f"  ✗ Exception: {e}\n"
                return False, full_log.strip()
        return True, full_log.strip()

    def run_auto_remediation(self, analysis: dict, job_id: Optional[str] = None, source_override: Optional[str] = None) -> dict:
        print(f"[DEBUG] AutoFixer starting for category: {analysis.get('category')}")
        strategies = analysis.get("strategies", [])
        auto_fix_command = ""
        manual_fix_steps = analysis.get("manual_fix_steps", "Review log and fix the error manually.")
        source = source_override or analysis.get("pipeline_source", "Unknown")
        
        # 1. Identify fix command (Prefer strategies, then analysis top command)
        if strategies:
            cmds = strategies[0].get("commands", [])
            if cmds:
                auto_fix_command = cmds[0]
        
        if not auto_fix_command and analysis.get("commands"):
            auto_fix_command = analysis["commands"][0]

        is_safe_to_run = False
        execution_status = "Manual Fix Required"
        retry_status = "No retry scheduled"

        # 2. Safety Check & Execution
        if auto_fix_command:
            print(f"[DEBUG] Evaluating safety of: {auto_fix_command}")
            safe, reason = self.is_safe(auto_fix_command)
            if safe:
                is_safe_to_run = True
                print(f"[AUTO-REMEDIATION] Source: {source} | Executing safe command: {auto_fix_command}")
                
                # Execute the fix
                success, output = self.execute_commands([auto_fix_command])
                
                if success:
                    execution_status = "Fix Applied Successfully"
                    # 3. Pipeline Retry (Trigger platform-specific retry)
                    target_job = job_id or "unknown-job"
                    if CICollector.trigger_retry(source, target_job):
                        retry_status = f"{source} Retry Triggered ({target_job})"
                    else:
                        retry_status = "Retry Error"
                    print(f"[AUTO-REMEDIATION] Success. Triggering {source} retry...")
                else:
                    execution_status = "Fix Failed"
                    retry_status = "Retry Aborted"
            else:
                print(f"[DEBUG] Command rejected based on restriction: {reason}")
                execution_status = "Manual Fix Required"
        
        return {
            "category": analysis.get("category", "Unknown"),
            "detected_tool": analysis.get("tool", "Unknown"),
            "root_cause": analysis.get("root_cause", "Unknown cause"),
            "auto_fix_available": is_safe_to_run,
            "auto_fix_command": auto_fix_command if is_safe_to_run else "",
            "manual_fix_steps": manual_fix_steps,
            "confidence_score": analysis.get("confidence", 0.9),
            "analysis_source": analysis.get("analysis_source", "AI Engine (Azure OpenAI)"),
            "execution_status": execution_status,
            "retry_status": retry_status,
            "pipeline_source": source,
            "highlighted_lines": analysis.get("highlighted_lines", [])
        }


class PackageCorrector:
    """Provides typo correction for popular packages using Levenshtein distance."""
    
    POPULAR_NPM = [
        "express", "react", "react-dom", "vue", "lodash", "axios", "moment", "chalk", 
        "commander", "webpack", "typescript", "jest", "eslint", "prettier", "nodemon",
        "npm", "yarn", "vite", "next", "tailwindcss", "sass", "babel", "dot-env",
        "jquery", "underscore", "request", "async", "bluebird", "redis", "mongodb"
    ]

    @staticmethod
    def lev_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return PackageCorrector.lev_distance(s2, s1)
        if not s2:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    @classmethod
    def suggest_npm(cls, target: str) -> tuple:
        """Returns (best_match: str, confidence: float)."""
        if not target: return None, 0.0
        
        # Strip potential version tag
        raw_name = target.split("@")[0]
        
        best_match = None
        min_dist = 999
        
        for pkg in cls.POPULAR_NPM:
            dist = cls.lev_distance(raw_name.lower(), pkg.lower())
            if dist < min_dist:
                min_dist = dist
                best_match = pkg
                
        # Confidence logic: 0 distance = 1.0, 1 dist = 0.9, 2 dist = 0.7, else low
        confidence = 0.0
        if min_dist == 0: confidence = 1.0
        elif min_dist == 1: confidence = 0.92
        elif min_dist == 2: confidence = 0.75
        elif min_dist <= 3: confidence = 0.4
        
        # Only suggest if it's reasonably close (dist <= 3 and shorter names require closer match)
        if min_dist > 3 or (len(raw_name) <= 3 and min_dist > 1):
            return None, 0.0
            
        return best_match, confidence


class LogAnalyzer:
    """
    Classifies CI/CD log text and returns structured analysis using Azure OpenAI.
    """

    def __init__(self):
        self.os_type = platform.system()
        self.rules_cache = {}
        
        # Azure OpenAI Configuration
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        self.client = None
        if self.api_key and self.endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint
                )
                print("[PIPELINE-LOG] Azure OpenAI Client Initialized.")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Azure OpenAI client: {e}")

    def analyze(self, log_text: str) -> Dict:
        """Performed 100% using AI Engine (Azure OpenAI) with Platform Detection."""
        import hashlib

        print(f"[PIPELINE-LOG] Received analyze request. Log length: {len(log_text)}")
        if not log_text:
            return self._fallback_result("")

        # Platform Detection Heuristic
        source = "Unknown"
        if "Jenkins" in log_text or "[Pipeline]" in log_text: source = "Jenkins"
        elif "GitHub Actions" in log_text or "actions/run" in log_text: source = "GitHub Actions"
        elif "gitlab-runner" in log_text: source = "GitLab CI"
        elif "ArgoCD" in log_text or "kube-system" in log_text: source = "ArgoCD"

        text_hash = hashlib.md5(log_text.encode()).hexdigest()
        if text_hash in self.rules_cache:
            print("[PIPELINE-LOG] Cache HIT. Returning previous AI analysis.")
            res = self.rules_cache[text_hash]
            res["pipeline_source"] = source
            return res

        # Azure OpenAI Analysis
        print("[PIPELINE-LOG] Consulting Azure OpenAI...")
        try:
            ai_data = self.analyze_log_with_ai(log_text)
            print("[PIPELINE-LOG] AI Analysis successful.")
            res = self._map_ai_to_result(ai_data, log_text)
            res["pipeline_source"] = source
            self.rules_cache[text_hash] = res
            return res
        except Exception as e:
            print(f"[PIPELINE-LOG] AI Analysis failed: {e}")
            res = self._fallback_result(log_text)
            res["pipeline_source"] = source
            res["root_cause"] = f"AI analysis failed: {str(e)}"
            return res

    def analyze_log_with_ai(self, log_text: str) -> Dict:
        """Sends log to Azure OpenAI and parses structured JSON."""
        if not self.client:
            raise Exception("Azure OpenAI client is not configured. Check environment variables.")

        # Truncate log to avoid token limits
        snippet = log_text[-6000:] if len(log_text) > 6000 else log_text

        prompt = (
            "You are a DevOps AI assistant.\n"
            "Analyze the following CI/CD pipeline error log and determine the root cause and solution.\n"
            "Return the result strictly in JSON format with fields:\n"
            "problem_category, detected_tool, root_cause, auto_fix_command, manual_fix_steps, confidence_score."
        )

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"PIPELINE LOG:\n{snippet}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)

    def _map_ai_to_result(self, ai_data: Dict, input_text: str) -> Dict:
        """Maps AI response fields to internal application fields."""
        fix_cmd = ai_data.get("auto_fix_command", "")
        manual_steps = ai_data.get("manual_fix_steps", "N/A")
        if isinstance(manual_steps, list):
            manual_steps = "\n".join(manual_steps)
            
        # Ensure confidence is a float
        confidence = ai_data.get("confidence_score", 0.5)
        try:
            confidence = float(str(confidence).replace("%", ""))
            if confidence > 1:
                confidence = confidence / 100.0
        except:
            confidence = 0.5

        return {
            "category": ai_data.get("problem_category", "AI Identified Issue"),
            "tool": ai_data.get("detected_tool", "Unknown"),
            "root_cause": ai_data.get("root_cause", "Analysis incomplete."),
            "suggested_fix": f"AI Suggestion: {fix_cmd}" if fix_cmd else "Review logs manually.",
            "manual_fix_steps": manual_steps,
            "confidence": confidence,
            "commands": [fix_cmd] if fix_cmd else [],
            "required_tools": [],
            "install_hints": {},
            "prevention_tips": ["Enable structured logging for better precision."],
            "strategies": [
                {
                    "name": "AI Recommended Fix",
                    "commands": [fix_cmd]
                }
            ] if fix_cmd else [],
            "highlighted_lines": [0],
            "correction": None,
            "analysis_source": "AI Engine (Azure OpenAI)"
        }

    def _fallback_result(self, input_text: str) -> Dict:
        return {
            "category": "Unclassified Error",
            "tool": "Unknown",
            "root_cause": "The log analysis failed or timed out.",
            "suggested_fix": "Review the full log manually.",
            "manual_fix_steps": "Review the full log manually.",
            "confidence": 0.1,
            "commands": [],
            "strategies": [],
            "prevention_tips": ["Implement structured logging."],
            "highlighted_lines": [],
            "correction": None,
            "analysis_source": "AI Engine (Error Fallback)"
        }
