from simulation import CICollector, LogAnalyzer, AutoFixer
import os
from dotenv import load_dotenv

load_dotenv()

job_id = "testje"
logs = CICollector.fetch_logs("Jenkins", job_id)
print(f"FETCHED LOGS ({len(logs)} bytes)")

analyzer = LogAnalyzer()
analysis = analyzer.analyze(logs)
print(f"ANALYSIS CATEGORY: {analysis.get('category')}")

fixer = AutoFixer()
result = fixer.run_auto_remediation(analysis, job_id, "Jenkins")
print("\nFIX RESULT:\n")
import json
print(json.dumps(result, indent=2))
