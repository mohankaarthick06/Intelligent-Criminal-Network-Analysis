CrimeGraph AI — Synthetic Sample Dataset (Indian-format numbers + location fields)
=====================================================================================
IMPORTANT: All records, mobile numbers, IDs, device identifiers, call events, and location
assignments in this package are synthetic. The Indian-format +91 mobile numbers are randomly
generated and may coincidentally correspond to real subscribers; do not call or message them.
Locations are city-level demo labels/centroids, not actual device geolocation or real cell-site
measurements. This dataset is for ML prototyping only, not investigative use.

Files
-----
cdr.csv
  5,000 synthetic call events. Caller/receiver phone numbers use +91 format. Includes
  cell_id and cell_city/state/pincode/latitude/longitude as synthetic event-location fields.
  Caller/receiver person IDs are included for controlled experimentation only; do not use
  them as predictive features.

phone_device_history.csv
  Synthetic phone-to-device history with phone_number in +91 format and primary city/state/
  pincode/latitude/longitude. Locations are assigned for demonstration, not inferred from
  telecom data.

imei_summary.csv
  Aggregated synthetic device activity by IMEI. No geolocation is attached because it is
  an aggregate by device; use CDR cell-location columns for event-level location.

identity_resolution_pairs.csv
  Pair-level binary classification dataset. Target: same_identity_label (1/0). Includes
  engineered similarity features and synthetic city/state/latitude/longitude for both records.
  Use only intended feature columns as X; do not include record_a/record_b or labels as features.
  The location columns are simplified synthetic primary locations and may not be perfectly
  consistent with the pair labels; they are not ground truth.

behavior_anomaly_features.csv
  Synthetic behavioral features and synthetic_anomaly_label for evaluation, plus a synthetic
  city/state/pincode/latitude/longitude per entity.

synthetic_location_reference.csv
  Reference table for the 10 cities used and their approximate city-centre coordinates.

Suggested use
-------------
1. Identity matching: compare Logistic Regression, Random Forest, and XGBoost on
   same_identity_label. Evaluate precision, recall, F1, PR-AUC, and calibration.
2. Anomaly detection: fit IsolationForest without synthetic_anomaly_label; use that label
   only for evaluation.
3. Graph analytics: create a graph from cdr.csv using caller_person_id and receiver_person_id
   for controlled demo only; calculate Common Neighbors, Jaccard, and Louvain communities.
4. Avoid leakage: IDs and target labels must not be model inputs.
5. The location coordinates are city centroids. Do not interpret them as exact device locations.
