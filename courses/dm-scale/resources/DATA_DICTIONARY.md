# Zanzibar Agriculture — Large Teaching Dataset (Z3003)

Synthetic, reproducible (`python generate_zanzibar_large.py`, seed 3003). Fitted to the Week 1 sample (`W1_zanzibar_crop_sample.csv`, 500 farms): per-crop yield, price and revenue means match it, and revenue = yield × 1000 × price_per_kg (±1%). **Synthetic data, not real records.**

| File | Rows | Use in the course |
|---|---|---|
| `zanzibar_farms.csv` | 10,000 farms | dimension table (star schema), clustering |
| `zanzibar_farm_seasons.csv` | 200,000 = 10,000 farms × 10 years (2016–2025) × 2 seasons | data cubes / OLAP, cleaning, sampling, PCA, classification, scaling |
| `zanzibar_input_purchases.csv` | 367,265 rows = 120,000 agro-dealer baskets (one row per item) | Apriori / FP-Growth, pattern evaluation |

## zanzibar_farm_seasons.csv
| Column | Type | Meaning |
|---|---|---|
| record_id | ID | row identifier |
| farm_id | ID | links to `zanzibar_farms.csv` |
| year, season | ordinal | 2016–2025; Masika (long rains) / Vuli (short rains) → time hierarchy |
| region → district | nominal | 5 regions, 11 real districts → location hierarchy |
| crop | nominal | Clove, Cashew, Rice, Coconut, Cassava |
| farm_type | nominal | smallholder, commercial, cooperative, subsistence (hidden cluster structure) |
| farm_size_ha | numeric | 0.2–25 ha |
| fertilizer_used, irrigated, cooperative_member | binary | Yes / No |
| rainfall_mm | numeric | season rainfall; island-wide drought in 2017, wet year 2023 |
| yield_tonnes | numeric | depends on rainfall, fertilizer, irrigation, farm size (real signal for Weeks 6–7) |
| price_per_kg | numeric | crop price with ~2%/year drift |
| revenue_usd | numeric | yield × 1000 × price |
| yield_class | binary label | High / Low vs the crop's median yield |

## Deliberate teaching features
- **Missing values:** 4% of yield (and revenue, yield_class); 1% of rainfall.
- **Sensor errors:** 25 rainfall readings of `9999` (gauge error code): outlier detection practice.
- **Signal for classification:** within a crop, yield correlates with rainfall (r ≈ 0.46) and farm size (≈ 0.32); fertilizer and irrigation both raise yield.
- **Natural clusters:** median farm size is 4.5 ha (commercial), 1.6 (cooperative), 0.9 (smallholder), 0.35 (subsistence).
- **Planted association rules** (verified): rice seed → urea (confidence 0.77, lift 6.8); clove seedlings → shade net (0.77, 4.8); sprayer → pesticide (0.64, 4.4).
- **Decoy item:** `hoe` appears in 60% of baskets. rice seed → hoe has confidence 0.55 but **lift 0.91**, so it looks strong but is not interesting (the Lecture 1 lesson).

## Note
The Week 1–3 sample (500 farms) stays the dataset for hand calculations. Relationships differ slightly: in the small sample, yield is unrelated to rainfall, while here it is related by design.
