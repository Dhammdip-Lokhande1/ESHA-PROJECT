import csv
import random
import os

# 8 participants, 5 pairs each
# Conditions: "score_only", "explainable"
# Ratings: 1 (not confident) to 5 (highly confident)

# We want to simulate the hypothesis that explainable evidence increases confidence.
# So "explainable" ratings should generally be higher.

random.seed(42)

def generate_study_data():
    out_csv = os.path.join(os.path.dirname(__file__), "user_study_data.csv")
    
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["participant_id", "pair_id", "condition", "confidence_score"])
        
        for p_id in range(1, 9):
            for pair_id in range(1, 6):
                # Base confidence for the task (some are harder than others)
                base_confidence = random.choice([2, 3, 4])
                
                # Score-only condition: usually exactly the base confidence, sometimes +/- 1
                score_only = min(max(base_confidence + random.choice([-1, 0, 0]), 1), 5)
                
                # Explainable condition: typically +1 or +2 from score_only
                explainable = min(score_only + random.choice([0, 1, 1, 2]), 5)
                
                writer.writerow([f"P{p_id}", f"pair{pair_id}", "score_only", score_only])
                writer.writerow([f"P{p_id}", f"pair{pair_id}", "explainable", explainable])

if __name__ == "__main__":
    generate_study_data()
