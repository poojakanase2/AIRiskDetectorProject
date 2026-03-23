from simulation import CICollector, LogAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()

logs = CICollector.fetch_logs("Jenkins", "testje")
print(f"FETCHED LOGS ({len(logs)} bytes):\n")
print(logs[-1000:]) # last 1000 chars

analyzer = LogAnalyzer()
analysis = analyzer.analyze(logs)
print("\nANALYSIS:\n")
import json
print(json.dumps(analysis, indent=2))
