# Seasonal recreational travel corridor analysis

## Zimmerman Tobacco hypothesis (owner-reported)
Customers driving north for cabins, fishing, camping and weekend recreation may stop near Zimmerman Tobacco on the way. The shop is near a highway, a Holiday gas station, and a directly adjacent liquor store. This is a plausible hypothesis, **not verified evidence of customer origin or a proven cause of sales**.

Typical reported retail sales: $240,000-$290,000/month; summer peak $330,000/month. The summer peak is ~24.5% above the $265,000 typical midpoint, but a single peak is not a seasonality estimate.

## Features to collect and verify
- Road segment AADT and seasonal/monthly vehicle counts where available, northbound vs southbound if measured
- Friday afternoon, weekend, holiday, and summer traffic variations
- Northbound route access: driveway turns, median restrictions, detour distance, visibility, parking
- Distance/time to popular lakes, cabin regions, campgrounds, boat launches and recreation routes
- Gas station, liquor store and convenience retail adjacency, with exact same-stop access
- Monthly retail sales and transaction counts across at least 12 months; weekday vs weekend patterns if POS data available
- Comparison to other highway corridor tobacco stores, including controls for hours, competition, product mix and pricing

## Analytical rules
1. Keep owner reports labeled as such, separate from independently verified measurements.
2. Never use Zimmerman's known sales to train or select coefficients if it is a holdout validation case.
3. Do not claim the route causes sales without comparing similar stores and checking competing explanations.
4. Separate resident trade area from pass-through traveler demand; avoid treating all vehicles as customers.
5. When seasonal counts are missing, output unknown and uncertainty rather than inventing counts.
