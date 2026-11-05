# Sydney / NSW nearshore wave transformation: sources and data for per-beach swell transformation

Research date: 2026-11-05. About 16 tool calls. The NSW Nearshore Wave Tool validation report (Baird, 2024; published Aug 2025) was downloaded and read in full text. Most other sources were read from abstracts or landing pages only, and this is flagged where it applies.

## 1. NSW Nearshore Wave Tool: what it provides, resolution, Sydney coverage, downloadability, licence

### Takeaway
The NSW Nearshore Wave Tool (https://nearshore.waves.nsw.gov.au/) is the best existing source of per-beach offshore-to-nearshore transformation for Sydney. It was built by Baird Australia for NSW DCCEEW, not by UNSW WRL. It uses pre-computed WAVEWATCH-III transfer functions at 10,679 points, spaced 250 m apart along the 10 m and 30 m depth contours. The matrix covers 25 log-spaced periods from 3.6 to 24.3 s and offshore directions from 0 to 230°TN in 5° steps. Each point is coupled to one deepwater point. A hobby project can easily get per-point forecast and hindcast CSVs, plus NetCDF and CSV by email request. The raw transfer matrices (NetCDF per point) are not published for download. The JSON API is undocumented and needs a session token.

### Cited Findings
- **History.** The original "NSW Coastal Wave Model: State Wide Nearshore Wave Transformation Tool" was published by OEH on 25 Jan 2017. It applies Wave Transfer Functions to move deep-water directional wave data to any nearshore location, and gave about 35 years of hindcast. — [OEH publication page](https://www.environment.nsw.gov.au/publications/nsw-coastal-wave-model-state-wide-nearshore-wave-transformation-tool)
- **Redevelopment.** The 2024 redevelopment was done by Baird Australia (report 12359.201.R1.Rev0, 14 May 2024, © 2025 State of NSW and DCCEEW). It provides more than 60 years of hindcast at 10,679 nearshore locations, spaced 250 m apart along the 10 m contour (5,578 points) and the 30 m contour (5,101 points). The tool URL is https://nearshore.waves.nsw.gov.au/. — [NSW Nearshore Wave Tool Validation Report (PDF)](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf); [publication page](https://www.environment.nsw.gov.au/publications/nsw-nearshore-wave-tool-validation-report)
- **Two transfer methods.**
  - Parametric NTF (NTF-P) takes offshore Hs, Tp and direction and looks up transformation coefficients with linear interpolation. It scales energy and adjusts period and direction. The new version adds wave height as a matrix dimension, up to Hs = 11 m, because of frictional and breaking losses in big seas.
  - Full spectral NTF (NTF-S) scales a nearshore response spectrum for each offshore frequency-direction bin and sums them. NTF-S performed better, but it runs only on request. NTF-P pre-populates the hindcast and drives the forecast.
  - [Validation Report §3.1, §3.2.3](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Matrix dimensions.**
  - Tp runs from 3.6 to 24.3 s in 25 log-spaced ordinates, and θp runs from 0 to 230°TN in 5° increments.
  - For NTF-P, Tp < 7 s uses γ = 1.1 with spreading parameter 3, and Tp ≥ 7 s uses γ = 2.3 with spreading 5.
  - NTF-S uses γ = 9 and spreading 80, with energy equivalent to 1 m Hs per bin.
  - WW-III is poor below 3.6 s.
  - Each nearshore location is coupled to a single deepwater point.
  - Earlier sensitivity work (Baird 2017) found transfer coefficients insensitive to input Hs until waves near breaking at 10 m depth.
  - [Validation Report §3.2.3](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Model.** WW-III v6.07 runs in nested grids: global 1°, Australia 0.25°, NSW and Tasman 0.05°, then an unstructured NSW mesh. The mesh goes from about 2.4 km at roughly 100 m depth to about 150 m elements at the 10 m contour. It uses new NSW Marine LiDAR topo-bathy and multibeam data. — [Validation Report §3.2.1, App. A](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf); [search summary of DCCEEW pages](https://www.environment.nsw.gov.au/publications/nsw-nearshore-wave-tool-validation-report)
- **Inputs.** The tool takes offshore Waverider buoy records or deep-water hindcasts. The update uses a 67-year hindcast (1957–2023, ERA5-driven). It includes a 10-day forecast and extreme-value (storm) analysis, and the factsheet points to nearshore.waves.nsw.gov.au/home/forecast. — [NSW Nearshore Wave Tool factsheet](https://www.environment.nsw.gov.au/sites/default/files/2025-04/nsw-nearshore-wave-tool-factsheet-250070.pdf); [tool update PDF](https://www.environment.nsw.gov.au/sites/default/files/2025-04/nsw-nearshore-wave-tool-update.pdf) (both via search snippets; the PDFs were too large to fetch)
- **Forecast.** An offshore wave forecast is pushed through NTF-P, updated about every 12 hours. The offshore forecast source is configurable, and a technical note inside the tool describes it. — [Validation Report §5.1.1](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Downloads.**
  - Forecast and hindcast time series for a selected point can be downloaded as CSV, with up to 1 month per hindcast view.
  - A Data Request page emails NetCDF and CSV links within 24 hours. Each request is limited to 10 points, with one request at a time per email.
  - The About page lists all output points and coordinates.
  - [Validation Report §5.1–5.3](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Back-end.** The tool stores per-point SQLite databases for forecast, hindcast and storm peaks. It also keeps per-point NetCDF files for NTF-P and NTF-S, plus offshore boundary spectra. The matrices are updated with a suite of Matlab code. The report does not say the NTF files are publicly downloadable. — [Validation Report §5.4–5.5](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Sydney validation.** Sites included Narrabeen, Collaroy (several deployments), Bronte and Maroubra. Earlier 2017 validation focused on the Sydney northern beaches (Narrabeen inshore buoy) and Wamberal.
  - Hm0 scored well at Sydney sites. With measured-offshore-input NTF-S, Narrabeen Hm0 had bias −0.02 m and RMSE 0.24 m, Collaroy 0.11 / 0.31 m, Bronte −0.07 / 0.30 m, and Maroubra −0.03 / 0.29 m.
  - Peak period and peak direction scored much worse, with Tp correlation of only about 0.16–0.64 and θp RMSE of 18–34°.
  - The report notes that the Sydney offshore buoy sits 20–25 km NNE of Bronte and Maroubra. That distance adds directional error when measured buoy data is used as input instead of the local hindcast point.
  - [Validation Report §3.3.3 and Appendix B tables](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Validation team.** The 2024 AMSA abstract describing the nearshore monitoring and tool development lists authors Doyle, Morris and Hanslow (NSW DCCEEW), Garber and Bradford (Baird), and Kinsela (Univ. Newcastle). — [AMSA 2024 abstract #203](https://amsa-2024.p.asnevents.com.au/days/2024-09-17/abstract/104950)
- **API (checked directly 2026-11-05).**
  - The web app is Angular on Baird's proprietary "Vasat" framework.
  - Its JS calls `/api/Point?contour=10`, `/api/Point?contour=30` and `POST /api/Point/{id}.data`. The base `/api/Models` answers without auth, but `/api/Point` returns `{"status":40021,"message":"No token supplied"}`.
  - The app gets a session via an OAuth-style `client_credentials` login embedded in the front-end.
  - This means the API is undocumented and not intended for third-party use.
  - Direct inspection of https://nearshore.waves.nsw.gov.au/ (framework also named in [Validation Report §5.4](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf))
- **Licence.** No licence statement for the tool's data outputs was found. The OEH page lists the report as "free". The validation report is "© 2025 State of NSW … All Rights Reserved". — [OEH page](https://www.environment.nsw.gov.au/publications/nsw-coastal-wave-model-state-wide-nearshore-wave-transformation-tool); [Validation Report](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)

### Inferences
- **Practical hobby use.** Pick the nearest 10 m-contour point to each target beach from the About-page point list.
  - Download its forecast CSV and/or request a long NTF-P hindcast (10 points per request).
  - Pair the hindcast with the Sydney buoy (or the tool's offshore input) for the same hours. Then fit empirical per-beach coefficients K(θ, Tp) = Hs_near / Hs_off.
  - The result is a per-beach direction-and-period table derived from the official model, without needing the proprietary NetCDF NTFs. Bin it at about 10° by about 2 s, which is coarser than the 5° by 25-period native matrix.
- **What the empirical table captures.** NTF-P coefficients are effectively Hs-independent below breaking. A ratio table fitted from hindcast pairs should therefore reproduce the tool's own matrix closely, except that multi-modal seas are treated as one parametric sea.
- **Coverage gaps.** 10 m points exist for open-coast Sydney beaches; the grid was not inspected for each beach. Harbour beaches such as Camp Cove and Nielsen Park are probably poorly represented. The NSW WW-III mesh is about 150 m at the 10 m contour, and inner Port Jackson may not be in the 10 m contour set. Check the point list.
- **Forecast option.** Pulling per-point forecasts through the tool's undocumented token-based API is technically possible. It is not a sanctioned interface, so ask DCCEEW (contact on the factsheet) before automating it. The supported route is manual CSV download plus the email data request.
- **Direction and period accuracy.** Peak period and peak direction at the nearshore are much less reliable than Hs, so a hobby project should lean on the Hs ratio. The Sydney buoy is off Long Reef (151.42°E, 33.78°S, 85 m), so for eastern-suburbs beaches the tool's own nearest hindcast point may be a better offshore reference than the buoy.

### Gaps
- No public, licensed download of the NTF-P/NTF-S matrices (NetCDF per point) was found. Whether DCCEEW would supply them on request is unknown.
- The licence for tool outputs (CSV/NetCDF) was not found. The tool's About and terms pages are rendered client-side and were not read.
- The full point list (IDs and coordinates) was not retrieved, so which 10 m points sit off each named beach is unconfirmed.
- The 2017 Baird toolbox report (103 pp; https://www.environment.nsw.gov.au/sites/default/files/nsw-nearshore-wave-transformation-tool-report.pdf) was not read. It may include Sydney northern-beaches validation plots with transfer-coefficient examples.
- The offshore forecast model the tool currently uses (e.g. BoM AUSWAVE vs other) was not confirmed. It is described only in an in-tool technical note.

## 2. Published studies of Sydney's wave climate and directionality

### Takeaway
Sydney's offshore climate is dominated by SSE swell, with easterly (Tradewind), south-easterly (Tasman) and southerly (Southern Ocean) wave types. It has been rotating anticlockwise toward E and SE. The best per-beach quantitative transformation work is at Narrabeen-Collaroy:
- Turner et al. (2016) used a 1,573-run SWAN lookup table from the Sydney buoy to 10 m depth at five profiles.
- Long Reef shelters the south end. Breakers there are about 30% smaller under average (southerly) conditions, and the pattern reverses under NE waves.
- The June 2016 East Coast Low showed that E–NE storm direction, not just height, drove record erosion.

### Cited Findings
- **Mortlock & Goodwin (2015), Continental Shelf Research, DOI 10.1016/j.csr.2015.02.007.**
  - They built a directional wave climate typology from mid-shelf NSW buoys: five synoptic wave climates in winter and six in summer.
  - These cluster into easterly (Tradewind), south-easterly (Tasman Sea) and southerly (Southern Ocean) types, with distinct wave power.
  - Wave power is rotating anticlockwise toward E and SE at the expense of southerly waves.
  - Source read via search summary of the Macquarie Uni record, not full text: [Macquarie Uni record](https://researchers.mq.edu.au/en/publications/directional-wave-climate-and-power-variability-along-the-southeas/)
- **Goodwin (mid-shelf mean wave direction climatology).** The trans-Tasman MSLP difference correlates with Sydney mean wave direction (southerly vs easterly) and with longer vs shorter periods. — [Macquarie Uni record](https://researchers.mq.edu.au/en/publications/a-mid-shelf-mean-wave-direction-climatology-for-southeastern-aust/) (search summary)
- **Mortlock et al. (2017), Water 9(2):121, on the June 2016 East Coast Low.** The E–NE storm wave direction was the major determinant of erosion magnitude. Narrabeen-Collaroy is particularly vulnerable to that direction because of its embayment shape. The paper compares this with the April 2015 ECL, which had a more southerly direction. — [MDPI Water](https://www.mdpi.com/2073-4441/9/2/121) (search summary)
- **Harley et al. (2017), Scientific Reports.** "Extreme coastal erosion enhanced by anomalous extratropical storm wave direction" also covers the June 2016 ECL. Erosion at Narrabeen-Collaroy was the largest in about four decades. — [Risk Frontiers summary](https://riskfrontiers.com/?p=2876); [EurekAlert](https://www.eurekalert.org/news-releases/679614) (full text not read)
- **Turner et al. (2016), Scientific Data 3:160024, the Narrabeen dataset.**
  - The Sydney directional Waverider is about 11 km offshore in about 80 m depth, with hourly data since March 1992.
  - Gaps and pre-1992 data were filled with CAWCR hindcast at 33°48′S 151°24′E.
  - The record (1979–2014) was transformed to 10 m depth at profiles PF1, PF2, PF4, PF6 and PF8 using a SWAN lookup table.
  - The table has 1,573 runs: Hs 0.25–9.5 m, Tp 2–17 s, direction 0–245°TN. It uses a JONSWAP spectrum with γ = 3.3 and keeps Tp unchanged.
  - The lookup table is supplied as a commented MATLAB function.
  - Validation against an inshore buoy between PF4 and PF6 (2011) gave Hs R = 0.94, bias −0.02 m, RMSE 0.18 m, and direction RMSE 11.2°.
  - [PMC4828941](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941/)
- **Long Reef sheltering (from the same paper).** The 1.5 km Long Reef Point headland at the south end shelters southerly waves. Modelled breaking height is about 30% higher at the north end than the south under average conditions. Under NE waves, south-end breakers are about 30% larger. — [PMC4828941](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941/)
- **Turner et al. (2016) licensing.** The article is CC BY 4.0 and the data are on Dryad (doi:10.5061/dryad.28g01) as CSV, including inshore waves. The live repository is http://narrabeen.wrl.unsw.edu.au. — [PMC4828941](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941/); [Dryad](https://datadryad.org/stash/dataset/doi:10.5061/dryad.28g01)
- **Wave climate context (from the validation report).**
  - Mean Hs ranges from 1.43 m at Batemans Bay to 1.63 m at Sydney.
  - The 100-yr ARI design Hs is 9.1 m at Botany Bay.
  - Tropical cyclones affect Sydney's wave climate on average about 16.5 days per year.
  - About 40% of central-region (Sydney) storms cluster in time.
  - Foundational Sydney references: Short & Wright (1981) "Beach systems of the Sydney region"; Trenaman & Short (1987) "Deepwater and breaker wave climate of the Sydney region", Coastal Studies Unit TR 87/1; Wright (1976) on nearshore wave-power dissipation in the Sydney region; Lawson & Abernethy (1975) on wave statistics off Botany Bay.
  - [Validation Report §1.2.3 and references](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Taylor et al. (2015).** This work compared parametric, quasi-spectral and full-spectral transfer methods on the NSW coast and found full-spectral best. — cited in [Validation Report §3](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)

### Inferences
- **Narrabeen MATLAB function.** Turner's lookup table is directly reusable as a Sydney-buoy to 10 m transfer for five points along Narrabeen-Collaroy. It covers the north end (PF1, near Narrabeen headland) to the south end (PF8, Collaroy, sheltered by Long Reef). It is open (Dryad/CC BY), so it is the most accessible per-beach direction-and-period transformation table found.
- **Rule of thumb for headland-sheltered ends.** The ±30% north–south reversal at Narrabeen for S vs NE waves is a citable rule of thumb. It applies to beaches with a headland at one end, such as Bondi/Ben Buckler, Manly/Shelly and Palm Beach/Barrenjoey, but by analogy only.

### Gaps
- The full texts of Mortlock & Goodwin (2015), Harley et al. (2017), Short & Trembanis (2004) and Splinter/Kinsela papers were not read. Their per-beach numbers, if any, are not captured here.
- Shand et al. (NSW wave climate and extremes) was not located in this pass.
- Trenaman & Short (1987) "Deepwater and breaker wave climate of the Sydney region" is likely the best old per-beach breaker-height table for Sydney. It was not found online.

## 3. Per-beach exposure info (Bondi to Palm Beach, harbour beaches), council studies, hazard studies

### Takeaway
No council CMP or hazard study with a per-beach table of nearshore/offshore Hs by direction was found for the eastern suburbs or northern beaches in this pass. Two quantitative per-beach sources were found:
- Narrabeen-Collaroy, from Turner et al. (2016).
- Measured nearshore buoys at Bronte and Maroubra (2016), Collaroy and Narrabeen, which can be compared against the Sydney buoy.

Everything else (Ben Buckler, Wedding Cake Island, Barrenjoey and so on) remains local or anecdotal knowledge that was not verified.

### Cited Findings
- **Waverley Beaches CMP Stage 1 Scoping Study (April 2024, Erin Sellers Pty Ltd for Waverley Council).** It covers Bondi, Tamarama and Bronte. The PDF returned HTTP 403 and was not read. — [Waverley Council PDF](https://www.waverley.nsw.gov.au/media/documents/environment/Waverley_Beaches_CMP_Stage_1_-_Scoping_Study_final.pdf)
- **Bronte SLSC seawall.** A coastal engineering assessment (RHDHV, Dec 2023) and a UNSW WRL peer review (Mar 2024) exist. Per the search summary they focus on overtopping and wave loads, not on transformation tables. — [NSW Planning Portal document](https://apps.planningportal.nsw.gov.au/prweb/PRRestService/DocMgmt/v1/PublicDocuments/DATA-WORKATTACH-FILE%20PEC-DPE-EP-WORK%20PPSSEC-239!20240119T035244.642%20GMT) (search summary)
- **Narrabeen-Collaroy.** This is the only Sydney beach with published per-location transformation, at 5 profiles (see §2). — [PMC4828941](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941/)
- **Bronte and Maroubra validation.** Both were nearshore validation sites for the NSW tool. Their Hm0 transformations validated with RMSE of about 0.3 m. — [Validation Report App. B](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)

### Inferences
- **Most practical route.** For eastern-suburbs and most northern beaches, the best path to per-beach transformation coefficients is to derive them from the NSW Nearshore Wave Tool hindcast (see §1). Published council tables were not found.
- **Harbour beaches.** Camp Cove and Nielsen Park are almost certainly outside reliable coverage of the statewide tool. They would need a separate rule, such as a heavy reduction that becomes non-zero only for large long-period E–ENE swell entering the Heads. That rule would be an assumption, not a sourced figure.

### Gaps
- Beachsafe (SLSA) hazard ratings were not retrieved in this pass. They give a 1–10 hazard rating per beach, not a wave transformation.
- Randwick (Coogee, Maroubra, Malabar, Little Bay), Woollahra and Northern Beaches CMP or coastal hazard study appendices with SWAN/MIKE21 nearshore tables were not located. Candidate documents worth searching:
  - Northern Beaches Council Collaroy-Narrabeen and Bilgola/Avalon coastal zone management studies (historically WorleyParsons/BMT WBM/Royal HaskoningDHV).
  - Randwick Coastal Management Program stage reports.
  - Manly Ocean Beach coastline hazard definition studies.
- No verified sources were found for the specific local claims:
  - Ben Buckler shadowing north Bondi from NE.
  - Wedding Cake Island at Coogee.
  - Barrenjoey sheltering north Palm Beach.
  - Long-period S swell wrapping into NE-facing beaches.
  
  Only Long Reef sheltering of Collaroy is sourced (§2). The rest must stay as unverified local knowledge.

## 4. Wave buoy and nearshore data availability (MHL, nearshore buoys, Narrabeen, CoastSnap)

### Takeaway
Three open data sets can be paired with offshore buoy data to calibrate per-beach ratios:
- The Sydney offshore Waverider (MHL, off Long Reef, about 85 m depth, since 1987, directional since 1992), via AODN THREDDS.
- NSW DCCEEW nearshore wave buoy deployments (CC BY; Sydney sites include Bronte, Maroubra, Collaroy, Narrabeen), via data.nsw.gov.au.
- The UNSW WRL Narrabeen dataset (CC BY article, Dryad data).

### Cited Findings
- **Sydney buoy record.** Position 151.42°E, 33.78°S, depth 85 m. The record runs from 17 Jul 1987 to the end of 2023 (36.5 years), with the max-Hs date given as 3 Mar 1992. MHL archives only integrated parameters and a "summarised" directional spectrum. Full 2D spectra are not continuously available, and the archived Datawell spreading is overly broad. — [Validation Report Table 2.2, §2.1.2.1](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **MHL buoy data access and licence.**
  - Data is on AODN THREDDS (`thredds.aodn.org.au/thredds/catalog/NSW-OEH/Manly_Hydraulics_Laboratory/Wave/`), and the Sydney record is "WAVESYD".
  - Licence terms conflict. Older AODN records carry a NSW Government disclaimer: acknowledge the provider, no third-party redistribution or commercial use without approval.
  - data.gov.au lists "Licence Not Specified".
  - MHL's 2023–24 wave climate summary states CC BY 4.0.
  - Contact: data-request@mhl.nsw.gov.au.
  - [researchdata.edu.au WAVESYD](https://researchdata.edu.au/manly-hydraulics-laboratory-buoy-wavesyd/679776); [data.gov.au](https://data.gov.au/data/dataset/000cb6d7-dea9-4e3a-869e-08f99e5f3434); [MHL 2023–24 annual summary](https://s3-ap-southeast-2.amazonaws.com/www-data.manly.hydraulics.works/www/publications/oeh/2024/mhl3067%20wave%20climate%20annual%20summary%202023-2024%20final.pdf) (search summaries)
- **Kinsela et al. (2024), Scientific Data, DOI 10.1038/s41597-023-02865-x.** More than 7,000 days of nearshore buoy observations in water shallower than 35 m at 20 NSW locations. — [PubMed 38347013](https://www.pubmed.gov/38347013/) (search summary; full text blocked by redirect)
- **Sydney deployments in the completed-deployments dataset.**
  - Bronte, 11 Aug to 17 Oct 2016, 14 m depth.
  - Maroubra, 11 Aug to 26 Oct 2016.
  - Collaroy, Collaroy2, Collaroy5, Figure8Pools (Royal NP) and Deeban.
  - The "active deployments" dataset is CC BY 3.0 AU.
  - [data.nsw.gov.au active](https://data.nsw.gov.au/data/dataset/8d8da699-5c6a-482b-aea0-2f0015ad1b20); [data.nsw.gov.au completed](https://data.nsw.gov.au/data/dataset/13dcfe36-a8ad-42ad-ad48-5734897df4c7); [researchdata.edu.au 2016–2023](https://researchdata.edu.au/nsw-nearshore-wave-2016-2023/2839356) (search summaries)
- **"Sydney (Long Reef)" spectral data.** The validation report says only the Sydney (Long Reef) buoy's measured spectral data was available. In context that means the offshore Sydney buoy, not a separate Long Reef nearshore buoy. — [Validation Report §3.3.3](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)
- **Narrabeen.** Monthly profiles since 1976, 10 m inshore wave series, and bathymetry are available on Dryad (about 98 MB of CSV) and at the WRL live site. — [PMC4828941](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941/); [Dryad](https://datadryad.org/stash/dataset/doi:10.5061/dryad.28g01)
- **Funding and operators.** The Collaroy-Narrabeen inshore buoys were run by UNSW WRL. SIMS / IMOS also contributed nearshore buoy services. — [Validation Report acknowledgements](https://www.environment.nsw.gov.au/sites/default/files/2025-08/nsw-nearshore-wave-tool-validation-report.pdf)

### Inferences
- **Calibration check for a hobby model.** Pair the Bronte and Maroubra 2016 nearshore records (CC BY) with concurrent Sydney buoy data. This gives about 2–2.5 months of measured nearshore/offshore Hs ratios by direction. That is short, but enough to sanity-check the NSW tool's ratios for the eastern suburbs.
- **MHL licensing.** For a non-commercial hobby project that does not redistribute raw data, either the attribution-only CC BY or the older disclaimer terms appear workable, with acknowledgement of MHL/DCCEEW. Confirm with MHL if republishing raw buoy values.

### Gaps
- No Sydney "inshore" MHL buoy separate from the offshore Sydney buoy was confirmed.
- The exact nearshore deployment list (dates and depths for Collaroy, Narrabeen, and any Manly, Long Reef or Bondi deployments) was not fully enumerated. The Kinsela et al. full text was blocked.
- CoastSnap stations (e.g. Manly, North Narrabeen, Bondi?) were not researched. They provide shoreline imagery, not wave data.
- No information was found on the BoM or MHL real-time inshore sensors at Sydney beaches.
