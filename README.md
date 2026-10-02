# Soranlasht — slope & aspect

Terrain analysis of **Soranlasht**, the bench above Kuragh and Charun (Upper Chitral, Pakistan), 36.2166° N 72.1765° E, 2,125–2,239 m.

**Live report:** https://dinarwali4.github.io/soranlasht-slope-aspect/

**Finding:** the bench faces north-north-west (mean aspect 335°, 84% N or NW), not ESE (0% of cells). It is a 6–14° ramp, 35 ha, about 210 m above both villages, and bare and unirrigated in every Google Earth high-res layer from Nov 2013 to Jul 2024.

**Method:** Esri, [Calculate slope and aspect with Native Maps SDKs](https://www.esri.com/arcgis-blog/products/developers/developers/calculate-slope-and-aspect-in-native-maps-sdks) (SDK 300.1): Horn 3×3 slope/aspect, 8 compass bands, and Esri's 32-class aspect-slope colormap, applied to Copernicus GLO-30.

| Path | Contents |
|---|---|
| `index.html`, `img/` | the report page (GitHub Pages) |
| `figures/` | 11 full-resolution annotated maps |
| `google_earth/Soranlasht_slope_aspect.kmz` | open in Google Earth Pro |
| `data/` | outline geometry and statistics |
| `scripts/` | Python used; see `README.txt` for method notes and caveats |

Imagery: Google Earth Pro (Airbus and historical layers), Esri World Imagery (Maxar). DEM: Copernicus GLO-30 © DLR/Airbus, provided under COPERNICUS by the EU and ESA. Prepared by RegenX.eco.
