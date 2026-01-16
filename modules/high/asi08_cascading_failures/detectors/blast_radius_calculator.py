# modules/high/asi08_cascading_failures/detectors/blast_radius_calculator.py
class BlastRadiusCalculator:
    def calculate_blast_radius(self, blast_radius):
       
        if blast_radius >= 5:
            return f"Large blast radius: {blast_radius} components affected"
        elif blast_radius >= 3:
            return f"Medium blast radius: {blast_radius} components affected"
        return None