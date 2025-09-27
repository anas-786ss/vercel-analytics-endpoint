from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/analytics")
async def analytics_endpoint(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    telemetry = body.get("telemetry", {})

    results = {}
    for region in regions:
        # Get data for this region
        data = telemetry.get(region, [])
        if not data:
            # If no data, skip region
            continue
        latencies = [record.get("latency_ms") for record in data if "latency_ms" in record]
        uptimes = [record.get("uptime") for record in data if "uptime" in record]
        breaches = sum(1 for l in latencies if l > threshold_ms)

        # Compute metrics
        avg_latency = float(np.mean(latencies)) if latencies else None
        p95_latency = float(np.percentile(latencies, 95)) if latencies else None
        avg_uptime = float(np.mean(uptimes)) if uptimes else None

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return results
