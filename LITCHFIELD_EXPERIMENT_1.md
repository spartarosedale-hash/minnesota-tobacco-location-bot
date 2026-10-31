# Litchfield Tobacco — Holdout Experiment 1

**Site:** 231 N Sibley Ave, Litchfield, MN 55355

**Known premises:** 1,200 sq ft, monthly rent $1,900.

**Prediction inputs:** eight other user-reported tobacco store comparables. Litchfield sales are excluded from prediction.

**Baseline method:** each comparable's sales midpoint adjusted by the ratio of 1,200 sq ft to its area, with adjustment capped at 0.67–1.5. Low = smallest adjusted midpoint, base = median, high = largest.

| Result | Monthly sales |
|---|---:|
| Low | $8,700 |
| Base | $61,000 |
| High | $93,800 |
| Reported actual range (validation only) | $90,000–$100,000 |
| Actual midpoint (validation only) | $95,000 |
| Base forecast error | -$34,000 (-35.8%) |

**Interpretation:** Size-only baseline underpredicts Litchfield. The high scenario overlaps the low end of reported actual sales but does not cover its midpoint. This is a retrospective validation against user-reported sales, not a prospective blind test.

**Next experiment:** Collect independent site factors (adult trade-area population, traffic, competing stores, accessibility) for all training sites; compare leave-one-store-out error before applying to Litchfield. Do not tune weights to Litchfield's reported actual sales. A small dataset does not support high-confidence location predictions.
