from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import numpy as np
from functools import lru_cache

from oberth.nozzle import MethodOfCharacteristics
from oberth.chemistry import RocketPerformance
from oberth.propellants import get_propellant

app = FastAPI(title="Oberth API", description="Rocket Engine Design & Analysis Suite")

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NozzleRequest(BaseModel):
    expansion_ratio: float = 25.0
    gamma: float = 1.2
    lines: int = 20

@lru_cache(maxsize=128)
def _compute_nozzle(expansion_ratio: float, gamma: float, lines: int):
    moc = MethodOfCharacteristics(gamma=gamma, lines=lines)
    moc.solve(expansion_ratio=expansion_ratio)
    # Use in-place rounding to avoid intermediate allocations and reduce JSON payload size
    np.round(moc.contour_array, decimals=5, out=moc.contour_array)
    np.round(moc.mesh_array, decimals=5, out=moc.mesh_array)
    result = {
        "contour": moc.contour_array.tolist(),
        "mesh": moc.mesh_array.tolist()
    }
    # Pre-serialize to JSON to avoid FastAPI/pydantic overhead on cache hits
    json_str = json.dumps(result, separators=(',', ':'))
    return Response(content=json_str, media_type="application/json")

@app.post("/api/nozzle")
def calculate_nozzle(req: NozzleRequest):
    """
    Generates nozzle contour using Method of Characteristics.
    """
    return _compute_nozzle(req.expansion_ratio, req.gamma, req.lines)

class PerformanceRequest(BaseModel):
    pc: float = 100e5 # Pa
    pe: float = 1e5   # Pa
    propellants: List[str] = ["LOX", "RP-1"]
    of_range: List[float] = [1.5, 4.0]

@lru_cache(maxsize=128)
def _compute_performance(pc: float, pe: float, propellants: tuple, of_range: tuple):
    engine = RocketPerformance(pc=pc, pe=pe)
    engine.scan_mixture_ratio(list(propellants), list(of_range))

    # Use in-place rounding to reduce JSON payload size (~47%) and avoid intermediate allocations
    of_array = engine.results['of']
    isp_array = engine.results['isp']
    np.round(of_array, decimals=5, out=of_array)
    np.round(isp_array, decimals=5, out=isp_array)

    result = {
        "of": of_array.tolist(),
        "isp": isp_array.tolist(),
        "propellants": engine.results['propellants']
    }
    # Pre-serialize to JSON to avoid FastAPI/pydantic overhead on cache hits
    json_str = json.dumps(result, separators=(',', ':'))
    return Response(content=json_str, media_type="application/json")

@app.post("/api/performance")
def calculate_performance(req: PerformanceRequest):
    """
    Calculates Isp vs O/F ratio.
    """
    return _compute_performance(
        req.pc,
        req.pe,
        tuple(req.propellants),
        tuple(req.of_range)
    )

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Additional endpoint for propellant info
@app.get("/api/propellants/{name}")
def propellant_info(name: str):
    prop = get_propellant(name)
    if prop:
        return prop
    return {"error": "Propellant not found"}

# Mount static files for local development
# This allows serving the frontend from public/ directory
if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
