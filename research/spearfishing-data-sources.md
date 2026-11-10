# Spearfishing data sources: what we can fetch without a login

Raw notes, tested from the shell on 2026-11-11. Box of interest: Palm Beach to Kurnell,
lat -33.55 to -34.05, lon 151.15 to 151.40.

Test points:
- "Mahon" -33.9420, 151.2695
- "Long Reef" -33.7440, 151.3210

Heads-up on those pins: OSM puts Mahon Pool at -33.9430, 151.2639 and Long Reef Point at
-33.7420, 151.3171 (Nominatim). So the test pins sit about 525 m and 450 m east of the
features, out on the reef/sand. All the numbers below are for the pins as given unless I
say "OSM point".

No accounts or tokens were needed for anything I tested. The places a login or an email
would come in are called out below.

---

## 1. NSW Marine LiDAR Topo-Bathy 2018 (DCCEEW)

- Landing page (SEED): https://datasets.seed.nsw.gov.au/dataset/marine-lidar-topo-bathy-2018
  (also on data.gov.au: https://data.gov.au/data/dataset/nsw-marine-lidar-topo-bathy-2018)
- Licence: CC BY 4.0 (SEED CKAN `license_id: cc-by`, "Creative Commons Attribution 4.0").
  The data.gov.au copy says CC BY 3.0 AU. Go with SEED, attribute NSW DCCEEW.
- What it is: Fugro airborne LiDAR plus LADS, 2018, 5 m x 5 m GeoTIFFs, depth to about 35 m,
  AHD heights (negative = below datum), GDA94 TM with central meridian 153 (same as MGA 56).
  Covers the whole NSW coast, so Sydney is in. Not for navigation.
- CKAN API (no key): https://datasets.seed.nsw.gov.au/api/3/action/package_show?id=marine-lidar-topo-bathy-2018

Endpoints:
- ArcGIS REST MapServer (Map, Query, Data), no login:
  https://mapprod2.environment.nsw.gov.au/arcgis/rest/services/Coastal_Marine/NSW_Marine_Lidar_Bathymetry_Data_2018/MapServer
  - layer 0: isobaths every 5 m (polylines)
  - layer 1: slope in degrees (raster)
  - layer 2: Bathymetry DEM in metres (raster)
  - It's a MapServer, not an ImageServer, so there's no `getSamples`. `identify` returns the
    raw pixel value, which is enough.
- Download packages, SEED links that 302 to a presigned S3 URL valid for 1 hour. A plain GET works
  (HEAD gets a 403 because the URL is signed for GET only):
  - Coverage zip, 5.5 MB: https://datasets.seed.nsw.gov.au/dataset/45089194-912d-4ecf-8200-969e0796afee/resource/d630ffae-7b8d-4ea1-a292-06a6b471dd5c/download/marinenswcoastallidarcoverage20190827.zip
  - Statewide XYZ zip, 1,405,235,379 bytes (about 1.4 GB): https://datasets.seed.nsw.gov.au/dataset/45089194-912d-4ecf-8200-969e0796afee/resource/6b5229e0-eda0-4dd5-bde5-d42de7b0fd2a/download/marine_2018_xyz_data.zip
  - I only range-fetched the first 100 bytes (206 Partial Content) to prove they're reachable.
- ELVIS (https://elevation.fsdf.org.au) is a browser app. The old FME index endpoint
  (elvis2018-ga.fmecloud.com/.../ReturnDownloadables.fmw) timed out, and I found no documented API.
  ELVIS bulk orders have historically needed an email address. You don't need it: SEED has the
  same data.

Identify call (one point):

```
curl "https://mapprod2.environment.nsw.gov.au/arcgis/rest/services/Coastal_Marine/NSW_Marine_Lidar_Bathymetry_Data_2018/MapServer/identify?geometry=151.2695,-33.9420&geometryType=esriGeometryPoint&sr=4326&layers=all:1,2&tolerance=0&mapExtent=151.2685,-33.9430,151.2705,-33.9410&imageDisplay=200,200,96&returnGeometry=false&f=json"
```

Sample results:
- Mahon pin: depth -24.26 m, slope 12.67 deg
- Long Reef pin: depth -6.33 m, slope 9.84 deg

200 m radius, 25 m grid of identify calls (197 points, 6 in parallel, takes a few seconds):

| site | pts with data | depth min / max / median (m) | slope median / max | share >10 deg |
|---|---|---|---|---|
| Mahon pin | 197/197 | -33.06 / -14.59 / -26.59 | 4.6 / 28.3 | 23% |
| Long Reef pin | 176/197 | -14.88 / -0.01 / -4.54 | 6.4 / 46.0 | 31% |
| Mahon Pool (OSM point) | 84/197 | -11.40 / -0.02 / -5.96 | 8.0 / 27.8 | 41% |
| Long Reef Point (OSM) | 85/197 | -4.08 / -0.01 / -0.55 | 2.4 / 11.0 | 3% |

The missing points are land or no-data. At the OSM Long Reef point the centre pixel itself is null
(dry rock platform).

### Depth range within 200 m of a point

- Quick option: the identify grid above. It's about 200 requests per spot, so precompute it once
  per spot into a JSON file (like swell_windows.json). Don't do it in the hourly run.
- Proper option: download the GeoTIFF/XYZ once, clip a 400 m box per spot, and compute min/max/
  percentiles, slope, and roughness offline in numpy. Commit the results. The 1.4 GB XYZ is the
  only bulk file, so it's a one-off download.
- Note: the local `gdalinfo` is broken (Homebrew, missing libaws-c-mqtt). I read the GA TIFFs
  with Pillow + numpy instead. `brew reinstall gdal` or `pip install rasterio` would fix that for
  offline work.

### Rock vs sand and relief

At 5 m this is practical:
- Slope is already served (layer 1). Share of cells over 10 deg, or the max, is a decent "relief" number.
- Roughness: std-dev of depth in a 3x3 or 5x5 window, or VRM, from the 5 m grid. Needs the raster
  (offline), not identify.
- Better still, DCCEEW already classified it. Seabed Landforms, from the same LiDAR, as polygons:
  https://mapprod2.environment.nsw.gov.au/arcgis/rest/services/Coastal_Marine/SeabedLandforms/MapServer/0
  Field `LANDFORM`: Reefs, Peaks, Scarps (>10 deg), Depressions and channels (Smooth/Rugose), Plains.
  Polygons within 200 m (query with `distance=200&units=esriSRUnit_Meter`):
  - Mahon pin: Peaks 14, Depressions/channels Smooth 9, Scarps 9, Rugose 8, Reefs 4, Plains 1. The pin itself is "Peaks".
  - Long Reef pin: Reefs 17, Rugose 9, Peaks 8, Scarps 8, Smooth 1. The pin itself is "Depressions and channels Rugose".
- And the DPIRD habitat map, with reef/sand polygons:
  https://spatial.industry.nsw.gov.au/arcgis/rest/services/PUBLIC/NSW_Marine_Habitats/MapServer/0
  (field `Habitat`). Within 200 m: Mahon pin reef (Sydney Seabed Mapping, conf 6; Avery nearshore
  reef, conf 5) plus a bit of Geoswath sand. Long Reef pin all reef (Avery, OSRA photo mapping).

---

## 2. Geoscience Australia AusBathyTopo and AusSeabed

- AusBathyTopo 250m (Australia) 2026, eCat: https://ecat.ga.gov.au/geonetwork/srv/api/records/7ff1f558-8ef4-427b-9696-007b76aab2c6
  (PID http://pid.geoscience.gov.au/dataset/ga/150050). GA overview: https://www.ga.gov.au/scientific-topics/marine-and-coastal/seabed/ausbathytopo-grids
- Licence: CC BY 4.0.
- Downloads (S3 behind files.ausseabed.gov.au, no login, range requests work):
  - https://files.ausseabed.gov.au/survey/AusBathyTopo_Australia_2026_250m.zip (2,380,292,468 bytes)
  - https://files.ausseabed.gov.au/survey/AusBathyTopo_Australia_2026_250m_derivatives.zip (8,743,578,837 bytes)
- WCS 2.0.1 on the AusSeabed GeoServer, no login. This is the useful one:
  https://warehouse.ausseabed.gov.au/geoserver/ows?service=WCS&version=2.0.1&request=GetCapabilities
  (228 coverages; WMS has 3447 layers). Axis labels are `Lat Long`, EPSG:4326, nodata 3.4e38.
  Grid is 0.0025 deg (about 230 m east-west here).

```
curl -o abt.tif "https://warehouse.ausseabed.gov.au/geoserver/ows?service=WCS&version=2.0.1&request=GetCoverage&coverageId=ausseabed__AusBathyTopo__Australia__Bathymetry__250m_2026_OV&format=image/tiff&subset=Lat(-33.948,-33.936)&subset=Long(151.2635,151.2755)"
```

  Returns a 5x5 float32 GeoTIFF. Middle cell:
  - Mahon pin: -25.3 m (box ranges +24.0 on land to -36.0)
  - Long Reef pin: -5.1 m (box -33.750..-33.738, 151.315..151.327; ranges +7.0 to -24.8)
  This agrees with the LiDAR to within about 1 m at both pins, but at 250 m it's useless for reef
  structure. It's fine as a fallback or offshore context.
- 30 m AusBathyTopo grids exist only for Bass Strait, the GBR, Northern Australia, Torres Strait, and
  Perth (2026). None covers Sydney.
- AusSeabed survey grids in the Sydney box (from WMS caps): Sydney Harbour 2 m 2004
  (151.186-151.275, -33.868 to -33.828) and Sydney Harbour 16 m 1997. Both are inside the harbour
  only, with no open coast. The rest is coarse: NSW Continental Slope 50 m 2006, Southern Australia
  UTM56 100 m 1999, and CSIRO shelf backscatter SJ56 75 m 2013. Coverage ids follow the pattern
  `ausseabed__<Name>_OV` (OV = values, HS = hillshade).
- Public bucket `ausseabed-public-warehouse-bathymetry` (ap-southeast-2) lists anonymously, but it
  only holds `custom/` and `Backup_Layers_Not_FoundinPortal/` UUID folders. It's not the main store,
  so use the WCS.

---

## 3. NSW DPIRD aquatic reserves and spearfishing closures

- Dataset: NSW Marine Protected Areas (DPIRD), https://data.nsw.gov.au/data/dataset/nsw-marine-protected-areas
  Licence CC BY 4.0. Marine park zones plus aquatic reserves, from the Management Rules Regulation
  and Gazette. "Guide only."
- Endpoints, no login:
  - REST (newer, CAPAD 2024 polygons): https://spatial.industry.nsw.gov.au/arcgis/rest/services/Fisheries_Portal/NSW_Marine_Protected_Areas/MapServer/0 (maxRecordCount 2000, GeoJSON output works)
  - REST (SEED-listed): https://spatial.industry.nsw.gov.au/arcgis/rest/services/PUBLIC/Marine_Protected_Areas/MapServer/0
  - WFS: https://spatial.industry.nsw.gov.au/arcgis/services/PUBLIC/Marine_Protected_Areas/MapServer/WFSServer?request=GetCapabilities&service=WFS
  - WMS: same path with WMSServer
  - Marine park zones: PUBLIC/Marine_Park_Zones/MapServer (no Sydney marine park, so not needed here)
- Sydney box query returns the aquatic reserves Towra Point (x3), Boat Harbour, Narrabeen, Cabbage
  Tree Bay, North Sydney Harbour, Long Reef, Barrenjoey, Cape Banks, and Bronte-Coogee.
- Point-in-polygon: both pins and both OSM points return no reserve. Long Reef AR bbox is
  151.3041..151.3223, -33.7463..-33.7326, so the Long Reef pin is inside the bbox but outside the polygon.
  Bronte-Coogee stops at -33.921, north of Mahon.
- To get polygons:

```
.../Fisheries_Portal/NSW_Marine_Protected_Areas/MapServer/0/query?where=NAME='Long Reef'&outFields=NAME,TYPE&outSR=4326&geometryPrecision=5&f=geojson
```

  Long Reef comes back as 928 vertices. Bundle a simplified GeoJSON of the Sydney reserves into the site.
- Spearfishing closures as polygons: I didn't find a public machine-readable layer.
  - SEED / data.nsw search for "spearfishing", "fishing closure": nothing.
  - spatial.industry.nsw.gov.au Fisheries_Portal/Portal/PUBLIC services: no closure layer.
  - A DPI ArcGIS Online "Other_Features" FeatureServer (FishSmart app layers: MPAs, IPAs,
    spearfishing closures, RFHs) shows up in search, but it now returns 400 Invalid URL. Gone.
  - The Fisheries Spatial Data Portal "Extract Data" tool
    (https://www.dpi.nsw.gov.au/fishing/fisheries-research/spatial-data-portal) emails a shapefile zip
    after you fill in a form with name/email and accept the licence. It's free but it's a manual
    form, not an API. I didn't use it. The user guide's licence wording is muddled (says CC BY-NC-ND
    and "CC BY 4.0" in the same breath). Contact: fisheries.data@dpi.nsw.gov.au.
  - Authoritative text and maps: https://www.dpi.nsw.gov.au/fishing/closures/spearfishing-closures
    and the Recreational Spearfishing Guide PDF. For Sydney, the closures (e.g. Sydney Harbour /
    Shiprock-type spots) would need hand-digitising from those maps, or ask DPIRD for the layer.

---

## 4. NSW Imagery (Spatial Services) as a map layer

- Landing: https://data.nsw.gov.au/data/dataset/nsw-imagery. CKAN says CC BY 3.0 AU
  (https://creativecommons.org/licenses/by/3.0/au/). Older Spatial Services sheets cite CC BY-ND 4.0
  or CC BY 4.0, and the service copyright says "© Department of Customer Service 2020".
  Attribute "© Spatial Services NSW" / "State Government of NSW and Spatial Services (DCS)". OSM wiki
  notes it's not cleared for OSM tracing. Displaying it as a basemap is the intended use ("consume
  imagery without hosting it").
- No key. Web Mercator (3857) cache, LODs 0-23.
- XYZ tile URL (note the {z}/{y}/{x} order):

```
https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/tile/{z}/{y}/{x}
```

  - WMTS: https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/WMTS/1.0.0/WMTSCapabilities.xml
  - WMS: https://maps.six.nsw.gov.au/arcgis/services/public/NSW_Imagery/MapServer/WMSServer?request=GetCapabilities&service=WMS
- Test at z18:
  - Mahon pin: .../tile/18/157374/241223 gave 200 image/jpeg, 5,499 bytes (open water)
  - Long Reef pin: .../tile/18/157201/241260 gave 200 image/jpeg, 16,172 bytes (white water over reef at top left)

---

## 5. AUCHD (Australasian Underwater Cultural Heritage Database) shipwrecks

- Landing: https://www.dcceew.gov.au/parks-heritage/heritage/underwater-heritage/auchd
- Public search UI, no login: https://environment.gov.au/shipwreck/public/wreck/search.do and the map
  search https://environment.gov.au/shipwreck/public/maps/shipwreck-map-search-load.do. Both return
  200 HTML. `/shipwreck/login.do` exists for permit and notification forms, not for searching.
- No API, no bulk download, no WFS/REST found. The map page posts to internal `.do` endpoints
  (shipwreck-map-search-submit.do, display-shipwreck-infowindow.do). Those are an undocumented
  session-based form flow, so I didn't script them.
- data.gov.au "Australian National Shipwrecks" (CC BY 3.0 AU,
  https://data.gov.au/data/dataset/australian-national-shipwrecks) just points back to the same
  search app. It's metadata only.
- DCCEEW_Geospatial on ArcGIS Online has "Underwater Cultural Heritage Protection Zones" (File
  Geodatabase, item 9eb26ad044b24c8cac589e92241ee9a0). Those are zones, not wreck points.
- Practical route: hand-pick the handful of diveable Sydney wrecks from the search UI (each record
  has lat/lon and accuracy), store them in our own JSON with an AUCHD record link, and attribute
  DCCEEW. Or email DCCEEW for an export.

---

## Accounts and tokens (per the follow-up)

- Nothing above needs a token for read access.
- Fisheries Spatial Data Portal extract: no account, but a name/email form, and the link is emailed.
- ELVIS: no account. Bulk orders want an email. Not needed given SEED.
- AUCHD: no public API to put a token on.
