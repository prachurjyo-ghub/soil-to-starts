# Crop planning dataset

7,834 rows × 18 columns. One row is one crop, BAMIS region, printed season and standard calendar week.

`crop_planning_dataset.csv` is the repository's flat data file for Python/R/imports. The source workspace also contains an Excel workbook, but it is not copied into this `assets/` directory and should not be assumed byte-for-byte or label-for-label identical after repository normalization.

`bamis_region_district_mapping.csv` maps the 14 BAMIS calendar regions to all 64 districts and their eight current administrative divisions.

Columns: crop, season, region, district_coverage, standard_week, month, growth_stage, duration_min_days, duration_max_days, rainfall_mm, temp_min_c, temp_max_c, temp_mean_c, humidity_mean_pct, sunshine_hours, wind_speed_kmh, source_pdf, source_page.

Weather values are printed calendar normals, not required crop thresholds or yield/suitability outcomes. Durations are printed calendar durations, not assumed plantation lifespans. Sunshine hours are retained as printed for the calendar period; no conversion is inferred.

`district_coverage` is a normalized BAMIS region coverage list derived from the district lists printed in the source PDF titles. It does not turn regional calendar normals into district-level measurements. Blank means missing; Unspecified means no explicit season label. Stage labels use the original calendar's spatial alignment. Source references allow checking each row.

For repository consistency, 106 Bengali/OCR-corrupted values in the `month` column were converted by exact observed-label mapping to full English Gregorian month names. No week-based month inference was used, and no crop, season, region, weather, duration, source or page value was changed. Zero Bengali-script cells remain in this CSV. The external source builder has not yet incorporated this normalization, so rebuilding from that workspace can reintroduce the original labels until the builder is updated.

Conflicting crop/region labels, ambiguous compressed week columns, a low resolution scan, implausible numeric values and duplicate records are excluded or explicitly corrected from agreeing printed labels. Three copied district-list errors are corrected from agreeing folder/title/table regions and repeated regional weather rows. The ambiguous `Onion/Mymensingh/26480.pdf` calendar is excluded because its Mymensingh folder/title conflicts with its Cumilla table and district list. See crop_planning_dataset_report.json for the exact audit.

The website also requires soil, irrigation and source-backed rotation rules, which these weather calendars cannot establish. No illustrative website scores, invented pH values or success labels were included.

For modeling, keep source calendars/regions grouped when splitting data because regional weather values recur across crops. A supervised yield/rotation-success target needs separate measured labels.

Rebuild: python scripts/build_planning_dataset.py (requires openpyxl and the existing BAMIS_Dataset/documents extraction).
