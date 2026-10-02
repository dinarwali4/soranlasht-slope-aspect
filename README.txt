SORANLASHT (above Kuragh & Charun, Upper Chitral) — SLOPE & ASPECT
RegenX.eco · prepared 2 Oct 2026

METHOD (from Esri blog "Calculate slope and aspect with Native Maps SDKs", 15 Sep 2026, SDK 300.1)
- Slope 0–90 deg; aspect 0–<360 deg clockwise from N (90 E, 180 S, 270 W), flat = -1.
- 8 compass bands (N = 337.5–22.5, NE 22.5–67.5 ... NW 292.5–337.5).
- Aspect-slope classes = slope bucket (10: 0–5, 20: 5–20, 30: 20–40, 40: >40 deg) + aspect bucket (1..8);
  rendered with Esri's exact 32-colour colormap (hue = direction, intensity = steepness, grey = flat).
- Slope rendered with viridis (Esri sample uses 0–90 stretch; here 0–60 for contrast).
- Kernel: Horn 3x3 (ArcGIS standard). Verified on synthetic E- and N-facing planes (90.0 / 0.0 deg).
- DEM: Copernicus GLO-30 (30 m). Display rasters cubic-resampled to 10 m for smooth rendering only —
  information content is 30 m. Statistics computed on the native 30 m grid.

SITE DEFINITION
Soranlasht = the connected bench (slope <=15 deg, 2,050–2,320 m) seeded at 36.2166N 72.1765E, confirmed by
the user on screen. It is the ground served by the user's own "Untitled Path" / "Water Uplift point" lines.
Earlier candidates (Charun Oweer bench; Charun valley floor) were rejected by the user.

RESULTS
Area 35.1 ha · elevation 2125–2239 m (mean 2174)
~209 m above Charun, ~223 m above Kuragh, behind a 25–45 deg scarp
Slope mean 10.5 deg (p10 6.3, median 10.7, p90 14.2)
Slope bands: {'0-5': 4.0, '5-20': 95.4, '20-40': 0.5, '>40': 0.0}
Aspect: {'N': 45.0, 'NE': 4.0, 'E': 0.0, 'SE': 0.0, 'S': 0.3, 'SW': 4.0, 'W': 7.8, 'NW': 38.8}
Mean aspect 335 deg (NNW), consistency R = 0.85; best-fit plane 8.2 deg toward 337 deg
ESE sector (101.25–123.75 deg): 0.0%  ·  E-to-SE (67.5–157.5): 0.0%
=> The bench does NOT face ESE. It is a uniform, gently NNW-facing ramp (Esri classes 5–20 deg N 44%, NW 37%).

IMAGERY
- Google Earth Pro latest layer at the bench: Airbus, 26 Jul 2024.
- Historical high-res layers captured: Nov 2013, May 2017, Aug 2020, Oct 2022, Jul 2024 (slider dates).
  Earth layers before 2013 are Landsat-grade only here. The bench is bare/unirrigated at every date.
- Esri World Imagery basemap for figures 01–04: Maxar, 30 Sep 2022.

FILES
figures/01–05   annotated maps on Esri imagery + cross-sections / aspect rose
figures/06–11   Google Earth Pro captures (latest, overlays, 3D oblique, historical timeline)
google_earth/Soranlasht_slope_aspect.kmz   open in Earth Pro: outline, 3 switchable overlays, contours, arrows, your paths
data/           outline GeoJSON-style geometry + stats
scripts/        Python used (paths refer to the session scratchpad; rerun from a folder holding glo30.tif)

CAVEATS
- 30 m DEM smooths small terraces and gully walls; slopes on short steep breaks are underestimated.
- Bench boundary is a DEM threshold (<=15 deg), not a surveyed or cadastral boundary.
