import numpy as np

class RocketPerformance:
    def __init__(self, pc=100e5, pe=1e5):
        self.pc = pc
        self.pe = pe
        self.results = {}

    def scan_mixture_ratio(self, propellants, of_range):
        """
        Calculates Isp vs O/F for given propellants.
        Returns the object itself for chaining plot_isp.
        """
        # Simplified model: Isp approx proportional to sqrt(Tc/M)
        # Tc(O/F) is bell-shaped, peaking near stoichiometric.
        # M(O/F) increases with O/F.

        start, end = of_range
        of_ratios = np.linspace(start, end, 50)

        # Determine peak O/F based on propellants
        # LOX/RP-1 peak ~ 2.3
        # LOX/LH2 peak ~ 5.0 (mass ratio)

        peak_of = 2.5
        max_isp = 300

        if 'LH2' in propellants or 'Liquid Hydrogen' in propellants:
            peak_of = 5.0 # Actually closer to 6 for optimal Isp but usually run rich
            max_isp = 450
        elif 'RP-1' in propellants or 'Kerosene' in propellants:
            peak_of = 2.3
            max_isp = 320 # Vacuum Isp

        # Vectorized calculation
        # Simplified Isp curve shape: Isp = max_isp * exp(-k * (of - peak_of)^2)
        # Using different widths for rich vs lean side

        # Performance Optimization: calculate the diff first to use for both the mask and the final
        # computation. Pre-calculating the inverted squared widths eliminates an array division
        # and an intermediate width array allocation, reducing execution time.
        diff = of_ratios - peak_of
        inv_width_sq = np.where(diff < 0, 1.0 / (peak_of * 0.6)**2, 1.0 / peak_of**2)
        isps = max_isp * np.exp(-inv_width_sq * (diff * diff))

        self.results = {
            'of': of_ratios,
            'isp': isps,
            'propellants': propellants
        }
        return self

    def plot_isp(self):
        """
        Plots the Specific Impulse vs Mixture Ratio curve.
        """
        if not self.results:
            print("No results to plot. Run scan_mixture_ratio first.")
            return

        import matplotlib.pyplot as plt

        of = self.results['of']
        isp = self.results['isp']
        props = self.results['propellants']

        label = f"{props[0]}/{props[1]}"

        plt.figure(figsize=(10, 6))
        plt.plot(of, isp, 'r-', linewidth=2, label=label)
        plt.title(f'Specific Impulse vs O/F Ratio ({label})')
        plt.xlabel('Oxidizer-to-Fuel Ratio (O/F)')
        plt.ylabel('Specific Impulse (s)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.show()
