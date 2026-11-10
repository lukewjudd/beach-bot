# Clovelly Bay / Gordons Bay seabed depth: what exists finer than 5 m

Checked 2026-11-11. Inlet box used: -33.9152..-33.9138, 151.2660..151.2700
(MGA56 roughly E 339700-340068, N 6245893-6246054). Gordons Bay box used:
-33.9180..-33.9158, 151.2640..151.2695.

## 1. NSW Marine LiDAR 2018 raw point clouds (best bet, not tested)

- SEED record: https://datasets.seed.nsw.gov.au/dataset/marine-lidar-las-clouddata-2018
- Classified LAS, 1 x 1 km tiles, GDA2020 MGA56 / AHD (GRS80 version also exists). CC BY 4.0.
- Coverage shapefile (downloaded, no login):
  https://datasets.seed.nsw.gov.au/dataset/f3c2d3eb-f9b2-4193-be20-28e9156d50a6/resource/c8310da4-9784-4945-a5c4-57609e49e6c2/download/marinenswlaslidarcoverage20191024.zip
  The inlet point sits inside block NS_ID 25, `SydneyEastSouthHeadCapeBanks`, project
  `SydEstB2018` ("Sydney Eastern Beaches 2018"), captured 17-19 Aug 2018, Status "Available".
- Density, from the Fugro report of survey (24 MB PDF, no login):
  https://datasets.seed.nsw.gov.au/dataset/45089194-912d-4ecf-8200-969e0796afee/resource/1bb06aa0-6b19-4244-84a5-62c29d2e4e1b/download/nsw_marine_lidar_2018_report_of_survey.pdf
  - RIEGL VQ-820-G: 148 kHz, "nominally 2 pts/m2", about 0.5 m spot spacing over land and
    shallow water (<7 m). Sydney Eastern Beaches section says the RIEGL reached about 8 m depth.
  - LADS HD: 3.4 m x 3.4 m spot spacing, 3-45 m depth.
  - Sydney Eastern Beaches: "minor gaps ... along the foreshore in areas of localised white
    water and turbidity". So expect holes on the wash-zone edges.
  - The inlet is mostly under 7 m, so it should be in the RIEGL zone: roughly 1-2 pts/m2,
    which would support a 1 m grid (maybe 0.5 m in the best spots).
  - The project also made a 1 m DEM, but only for orthorectifying the imagery (Deliverable 9),
    and a 10 cm GSD geo-referenced image mosaic. Neither seems to be published separately.
- How to get it: ELVIS https://elevation.fsdf.org.au -> Order Data, draw a box over Clovelly,
  tick the SydEstB2018 tile(s), enter an email address (pick industry "Other"), and the links
  arrive by email. No account needed, as far as public guides say. I did NOT order. Automated
  fetches of ELVIS's JS bundle were blocked, so I didn't find a direct tile URL.
  Fallback contact: data.broker@environment.nsw.gov.au (in the coverage shapefile).

## 1b. Statewide XYZ (tested): it's the same 5 m grid

- https://datasets.seed.nsw.gov.au/dataset/marine-lidar-topo-bathy-2018
- The `marine_2018_xyz_data.zip` resource is 1.4 GB. It redirects to a signed S3 URL, and
  range requests work, so I read the zip directory and pulled one entry:
  `2018B/2018B/25_NSWENV_20180819_SydneyEastSouthHeadCapeBanks_LD_TPBYGRD005RGL_G20Z56AHD_FLD778_20190702_FV02.xyz`
  (94.6 MB raw, 3.14 M rows, CSV x,y,z, GDA2020 MGA56, AHD).
- Result: 5.0 m cell centres (e.g. 337937.5, 337942.5 ...). Over the inlet box: 2368 cells,
  which matches a full 5 m grid (2372 expected). 512 are below 0 m AHD, and the deepest is
  -6.32 m AHD. Gordons Bay box: 5050 cells, deepest -17.7 m.
- So the XYZ isn't finer than the MapServer, just the same grid in text form.
  `GRD005` in the filename = 5 m.

## 2. Multibeam (NSW DCCEEW / OEH SeabedNSW / HABMAP)

- SEED record: https://datasets.seed.nsw.gov.au/dataset/nsw-environment-multibeam-survey-gridded-bathymetry-and-backscatter-datasets
- Coverage shapefile (v20260127, no login):
  https://datasets.seed.nsw.gov.au/dataset/1801586c-e84d-4929-88e0-7a06927126ed/resource/65c2fccd-4878-4e98-81b8-9da9e7a30b48/download/nsw_multibeam_coverage_published_20260127.zip
- Nearest survey: `NSWOEH_20090930_CoogeeBondi_MB`, 30 Sep 2009, RV Glaucus, GeoSwath 125 kHz,
  2 m grid, AHD, ZAccuracy "<5m" (sic), issued 2012-11-16. Files on the open AODN S3 bucket:
  https://imos-data.aodn.org.au/?prefix=NSW-OEH/Multi-beam/2009/20090930_CoogeeBondi/
  e.g. https://s3-ap-southeast-2.amazonaws.com/imos-data/NSW-OEH/Multi-beam/2009/20090930_CoogeeBondi/NSWOEH_20090930_CoogeeBondi_MB_BTYGRD002GSS_W84Z56AHD_FLD740_20121116_FV02.xyz (101 MB)
  plus .tif (13 MB), .kmz, backscatter, and a ScientificRigour PDF. Licence is CC BY (AODN/NSW).
- Tested: streamed the xyz and clipped it. The grid spacing really is 2.0 m. But there are ZERO
  points in the inlet box. At the inlet's latitude the western edge of coverage is about
  E 340213-340307 (~151.272), so it stops about 150-250 m east of the inlet mouth, and the
  shallowest value there is about -5.5 m. In the Gordons Bay box: 5648 cells (about 18% of the
  box), all in the outer bay at -7 to -18 m AHD, with the edge at about E 339795.
- `NSWOEH_20150623_BondiCoogee_MB` (2 m, Bombora) is 1.4+ km away and doesn't cover it.
- Useful for the outer Gordons Bay / mouth approach only. The inlet itself is too shallow for
  the boat.

## 3. Council / engineering

- Found nothing with a hydrographic survey of the inlet. I looked at Randwick news/precinct
  notes (headland rock stabilisation after the April storms; footpath repair under
  investigation as of Nov 2025), the Clovelly flood study
  (https://www.yoursay.randwick.nsw.gov.au/clovellyfloodstudy), and the Eastern Beaches CMP
  Stage 1 scoping study
  (https://www.waverley.nsw.gov.au/media/documents/environment/Eastern_Beaches_CMP_Stage_1_Scoping_Study_June2020.pdf).
  That scoping study cites the 2018 marine LiDAR as its bathymetry source; I didn't find any
  bespoke survey in it.
- No UNSW WRL Clovelly report turned up in search. WRL has done nearby Bronte seawall work.
- Worth a direct ask: Randwick City Council (concourse/seawall works drawings sometimes include
  a site survey with a few spot levels below the low-water mark). Low value for a depth map.

## 4. Diver models / snorkel charts

- No Sketchfab or university photogrammetry of Clovelly or Gordons Bay found.
- Gordons Bay Underwater Nature Trail: about 600 m of drums and chains, 2 m to about 15 m deep.
  Info is on the sign at the Cliffbrook Parade steps, and the trail is maintained by the
  Gordons Bay Scuba Diving Club. No published depth chart found.
  https://www.randwick.nsw.gov.au/facilities-and-recreation/beaches-and-coast/beaches/gordons-bay
- Reef Life Survey has transect sites around here, but those are depth-at-transect records,
  not a bathymetric surface.

## 5. Satellite-derived bathymetry

- No NSW 10 m SDB product found. GA/EOMAP 10 m Sentinel-2 SDB exists for Shark Bay and
  WA/Kimberley only (ecat.ga.gov.au). Even if something existed, a ~60 m wide inlet would be a
  handful of 10 m pixels, so it's not worth chasing.

## Other

- NSW Spatial Services topographic LiDAR (on ELVIS too) is land only: it gives the rock
  platforms and the concrete above the water level at capture time, not the seabed. It could
  be handy to stitch onto the dry edge of the map.
- Tide datum: everything here is AHD. Fort Denison chart datum (LAT) is about 0.925 m below AHD,
  so depth below LAT = -(z_AHD) - 0.925. Check against current MSQ/AHO tables before using.

## Scratch files (not in repo)

Scripts and downloads are in the session scratchpad: `bin/shpq.py` (pure-python shapefile point
lookup + UTM), `bin/rzip.py` (pull one member out of a remote zip using HTTP Range), and the
`clip.xyz` clips.
