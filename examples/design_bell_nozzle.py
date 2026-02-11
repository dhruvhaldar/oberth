from oberth.nozzle import MethodOfCharacteristics

# Design a nozzle for Mach 5 exit
moc = MethodOfCharacteristics(gamma=1.2, lines=20)
contour = moc.solve(expansion_ratio=25)

# This will show a plot if run locally, or just execute
try:
    moc.plot_mesh()
    print("MOC Plot generated.")
except Exception as e:
    print(f"Could not plot: {e}")
