"""Evaluate Litchfield holdout without using its sales as prediction inputs."""
import json
from location_estimate import predict,read_comparables

def run():
    result=predict("231 N Sibley Ave, Litchfield, MN 55355",1200,1900,read_comparables())
    actual_low,actual_high=90000,100000
    midpoint=(actual_low+actual_high)/2
    result["validation_only"]={
      "actual_monthly_sales_low":actual_low,
      "actual_monthly_sales_high":actual_high,
      "actual_midpoint":midpoint,
      "base_error_dollars":result["monthly_sales_base"]-midpoint,
      "base_absolute_percentage_error":round(abs(result["monthly_sales_base"]-midpoint)/midpoint*100,1),
      "note":"Actual sales used only for comparison, not training or predictor input"
    }
    return result
if __name__=="__main__":
    print(json.dumps(run(),indent=2))
