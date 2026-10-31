# Location intelligence data specification

Purpose: improve retail-only tobacco store monthly revenue predictions without leaking validation sales into training.

## Required features per store
- exact_address; geocoded_latitude; geocoded_longitude; geocode_quality
- annual_average_daily_traffic_nearest_road; traffic_count_year; traffic_count_source; road_segment_id
- highway_frontage; direct_highway_visibility; entrance_access; median_turn_restrictions; parking_spaces
- liquor_store_adjacent (same building / directly next door); liquor_stores_0_5_mi; gas_stations_0_5_mi; grocery_anchors_1_mi
- competing_tobacco_shops_1_mi; competing_tobacco_shops_3_mi; competing_tobacco_shops_10_min_drive; competitor_open_status
- adult_population_5_min_drive; adult_population_10_min_drive; adult_population_15_min_drive; median_household_income_10_min_drive
- seasonal_visitation_proxy; tourist_or_lake_route_proxy; month
- store_age_months; operating_hours_per_week; square_feet; product_category_mix_if_available
- each field: source_url, observed_date, verification_status (verified/reported/estimated/unknown), confidence

## Data source priorities
1. Minnesota DOT traffic counts, with segment and count year
2. US Census geocoder and ACS 5-year demographics; use actual drive-time catchments when available, not tract totals as a radius substitute
3. Official city/county business licensing and parcel data for local business identification where accessible
4. Verified store websites and business listings for neighboring anchors, operating hours, and competitor locations
5. Owner-provided store observations, explicitly labeled reported rather than independently verified

## Validation protocol
- Keep Litchfield and Zimmerman actual sales out of training_comparables.csv.
- Do not train on summer peak as if it were typical monthly sales.
- Evaluate each holdout against its actual sales midpoint and report absolute percentage error and interval coverage.
- Report both error and missing-feature count; do not claim <15% error from only two holdouts.
- Compare a baseline model with location-feature models using leave-one-store-out validation; small samples require wide uncertainty intervals.
- Keep retail and wholesale revenue separate.

## Zimmerman observations (owner-reported)
Address: 26219 Fremont Dr Ste 101, Zimmerman, MN 55398
Typical retail monthly sales: $240,000-$290,000; summer peak $330,000.
Liquor store directly adjacent; Holiday gas station nearby; highway in front.
Highway visibility, access details, verified AADT, drive-time population, competitor density, store square footage, and rent remain unverified/unknown.
