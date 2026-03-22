import statistics
import math

def calculate_statistics(data_list, confidence_level=0.95):
    # Takes a raw list of runtimes and returns a stats dictionary
    # Works for both AES and RSA output lists
    
    if len(data_list) < 2:
        return {"mean": 0, "stdev": 0, "ci_low": 0, "ci_high": 0}

    n = len(data_list)
    mean = statistics.mean(data_list)
    stdev = statistics.stdev(data_list)
    
    # Standard Error = s / sqrt(n)
    se = stdev / math.sqrt(n)

    # Critical Values (z*)
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z_crit = z_scores.get(confidence_level, 1.96) # Change z_scores accordingly

    margin_of_error = z_crit * se
    
    return {
        "mean": mean,
        "stdev": stdev,
        "ci_low": mean - margin_of_error,
        "ci_high": mean + margin_of_error
    }