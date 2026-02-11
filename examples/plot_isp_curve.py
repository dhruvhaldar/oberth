from oberth.chemistry import RocketPerformance

# Compare LOX/LH2 vs LOX/RP-1
engine = RocketPerformance(pc=100e5, pe=1e5) # 100 bar chamber
results = engine.scan_mixture_ratio(
    propellants=['LOX', 'RP-1'],
    of_range=[1.5, 4.0]
)

try:
    results.plot_isp()
    print("ISP Plot generated.")
except Exception as e:
    print(f"Could not plot: {e}")
