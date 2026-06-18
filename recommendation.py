# recommendation.py
import numpy as np

class EnergyRecommendation:
    """
    Calculates dynamic track parameters based on initial exit velocity 
    to prevent slow pacing, extreme high G-forces, or stalling.
    """
    g = 9.8

    @classmethod
    def get_recommendations(cls, start_type, start_value):
        """
        Calculates the available exit velocity budget based on the start track parameters.
        """
        v_exit = 0.0
        
        # Mirroring the calculation formulas from tracks.py
        if start_type == "Launcher":
            # v_exit = sqrt(2 * a * L) | Assuming constant 2.5g acceleration
            v_exit = np.sqrt(2 * 2.5 * cls.g * start_value)
        elif start_type == "Lift Hill":
            v_exit = np.sqrt(2 * cls.g * start_value)
        elif start_type == "Rollback":
            v_exit = np.sqrt(2 * cls.g * start_value)
            
        total_energy_height = (v_exit ** 2) / (2 * cls.g)
        
        # Target a comfortable apex velocity range of 5 m/s to 12 m/s for solid pacing
        v_target_low = 5.0
        v_target_high = 12.0
        
        # Heights corresponding to these target speeds
        h_target_max = total_energy_height - (v_target_low ** 2) / (2 * cls.g)
        h_target_min = total_energy_height - (v_target_high ** 2) / (2 * cls.g)
        
        # Guard against negative heights
        h_target_min = max(2.0, h_target_min)
        h_target_max = max(5.0, h_target_max)

        return {
            "v_exit": v_exit,
            "max_energy_height": total_energy_height,
            "Camelback": (round(h_target_min, 1), round(h_target_max, 1)),
            "Loop": (round(h_target_min / 1.5, 1), round(h_target_max / 1.5, 1)), # Loops have distinct dynamic constraints
            "Corkscrew": (round(h_target_min / 4.0, 1), round(h_target_max / 4.0, 1)), # Section scaling has H = h * 4
            "Cobral Roll": (round(h_target_min, 1), round(h_target_max, 1)),
            "Helix": (round(h_target_min / 2.0, 1), round(h_target_max / 2.0, 1)) # R = 2 * h geometry rule
        }