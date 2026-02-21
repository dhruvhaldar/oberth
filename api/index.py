from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os

from oberth.nozzle import MethodOfCharacteristics
from oberth.chemistry import RocketPerformance
from oberth.propellants import get_propellant

app = FastAPI(title="Oberth API", description="Rocket Engine Design & Analysis Suite")

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

@app.post("/api/nozzle")
def calculate_nozzle(req: NozzleRequest):
    """
    Generates nozzle contour using Method of Characteristics.
    """
    moc = MethodOfCharacteristics(gamma=req.gamma, lines=req.lines)
    contour = moc.solve(expansion_ratio=req.expansion_ratio)
    return {"contour": contour, "mesh": moc.mesh}

class PerformanceRequest(BaseModel):
    pc: float = 100e5 # Pa
    pe: float = 1e5   # Pa
    propellants: List[str] = ["LOX", "RP-1"]
    of_range: List[float] = [1.5, 4.0]

@app.post("/api/performance")
def calculate_performance(req: PerformanceRequest):
    """
    Calculates Isp vs O/F ratio.
    """
    engine = RocketPerformance(pc=req.pc, pe=req.pe)
    engine.scan_mixture_ratio(req.propellants, req.of_range)
    # Convert numpy arrays to lists for JSON serialization
    results = {
        "of": engine.results['of'].tolist(),
        "isp": engine.results['isp'].tolist(),
        "propellants": engine.results['propellants']
    }
    return results

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
