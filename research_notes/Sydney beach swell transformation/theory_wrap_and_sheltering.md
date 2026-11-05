# Theory and empirical methods: headland sheltering, refraction/diffraction "wrap", and breaking height vs swell direction and period

Scope: physics and lightweight formulas for turning offshore (Open-Meteo) swell height/direction/period, per partition, into a nearshore/breaking height at a beach between rocky headlands (Sydney). Every number below carries a source. Values I computed from cited formulas are marked "(computed)". Derivations from standard theory that I could not tie to a fetched source are in the Inferences sections.

## 1. Swell window: definition and computation

### Takeaway
I found no published coastal-engineering "swell window" algorithm for single surf breaks. In practice the window is a geometric construct: cast rays from a point just offshore of the beach and keep the bearings with an unobstructed path to open ocean. The closest formal analogues are the obstruction grids used in global wave models (WAVEWATCH III). Those grids block energy per direction using the coastline geometry (GSHHS), and like a hard window they still need a diffraction or spreading correction near the obstacle.

### Cited Findings
- Unresolved islands are a major source of local error in global wave models. NCEP's WAVEWATCH III handles them with a sub-grid "obstruction grid", a method borrowed from SWAN. This had a local but dramatic effect on model errors, and refining the whole grid was judged uneconomic. — [Tolman 2003, Ocean Modelling](https://data-ww3.ifremer.fr/BIB/Tolman_OM2003.pdf)
- Chawla & Tolman automated obstruction-grid generation from the GSHHS coastline, accounting for islands overlapping grid cells and for their orientation. A known limitation is that the grid does not record where inside a cell the obstruction sits, so results within a few grid increments of an island are not accurate. — [Chawla & Tolman 2007, Ocean Modelling](https://data-ww3.ifremer.fr/BIB/Chawla_Tolman_OM2007.pdf)
- The newer Unresolved Obstacles Source Term (UOST, now in WAVEWATCH III) treats sub-grid blocking as a direction-dependent dissipation source. It accounts for swell direction and the layout of obstacles within each cell. — [Mentaschi et al. 2020, Ocean Dynamics](https://link.springer.com/article/10.1007/s10236-020-01410-3)
- Sydney field work shows that headlands create alongshore gradients in wave height, surf-zone width and beach state. Rip/exit behaviour changes from the protected headland end to the exposed end, and headland geometry and wave direction control the circulation. — [UNSW thesis, field observations of embayed beaches](https://unsworks.unsw.edu.au/fapi/datastream/unsworks:12647/SOURCE02?view=true)
- At Narrabeen–Collaroy, the bounding headlands and the curvature of the embayment produce a distinctive alongshore wave-energy gradient. Storm waves in the region typically come from the S to SE. — [Turner et al. 2016, Scientific Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC4828941)

### Inferences
- A practical per-beach window: from a point about 0.5–1 km seaward of mid-beach, cast rays every 1–2° and mark each bearing "open" if the ray reaches about 50–100 km without hitting land. Headland tips then set the window edges (θ_left, θ_right). This is the sub-grid geometric logic of the obstruction grid, applied at a single point.
- A hard window is wrong right at its edges. The obstruction-grid limitation (no sub-cell position) and the diffraction results in section 3 both show that energy leaks into the geometric shadow. The leak grows as directional spreading widens and as wavelength grows relative to the distance to the headland tip. The edges need a soft "wrap" (section 6).
- Alongshore variation matters. One window per beach averages over the sheltered corner and the exposed end, which the Sydney field studies show can differ a lot. Consider two or three sample points per beach (sheltered corner, middle, exposed end).

### Gaps
- I found no peer-reviewed or industry write-up (Surfline, MSW, Swellnet) of how commercial surf forecasters compute swell windows. Surfguru says only that it uses simplified calculations near each beach plus surfer feedback ([Surfguru](https://surfguru.com.br/conteudo/estimating-wave-height-at-surf-spots-2024-07-05-29190.html)).

## 2. Refraction and shoaling (Snell's law, Kr, Ks) and their period/depth dependence

### Takeaway
Under linear theory with straight, parallel contours, H = H0·Ks·Kr, where Ks = sqrt(cg0/cg) and Kr = sqrt(cos θ0 / cos θ), and the direction follows Snell's law, sin θ / c = constant. Long-period swell feels the bottom earlier: at a given depth it has turned more toward shore-normal and shoals more. This is the main physical reason long-period swell "wraps" into embayments better.

### Cited Findings
- Conservation of wave power between orthogonals gives H2 = H1·K_R·K_S, with K_R = (cos θ1 / cos θ2)^½ and K_S = ((n c)1 / (n c)2)^½, where n = cg/c. — [Apsley, Manchester hydraulics notes (slides)](https://personalpages.manchester.ac.uk/staff/david.d.apsley/lectures/hydraulics3/slidesWaveTransformation.pdf)
- Refraction is the change of direction caused by depth-dependent wave speed and follows Snell's law. Equivalently, k sin θ is constant along a ray over straight, parallel contours. — [Apsley notes](https://personalpages.manchester.ac.uk/staff/david.d.apsley/lectures/hydraulics3/WavesTransformation.pdf)
- Group velocity equals phase celerity in shallow water (n → 1) and is half the phase speed in deep water. Conservation of energy flux then makes height increase into shallow water. — [TU Delft Bijker lecture notes](https://repository.tudelft.nl/file/File_d0a7b258-0d24-4314-aa48-ff2f7294a2af); [Wikipedia: Wave shoaling](https://www.wikipedia.com/wiki/Wave_shoaling)
- (Computed) Linear theory, exact dispersion solved iteratively, deep-water incidence θ0 = 45° to shore-normal:

| T (s) | L0 (m) | Ks at 10 m | θ at 10 m | Kr at 10 m | Ks at 5 m | θ at 5 m | Kr at 5 m |
|---|---|---|---|---|---|---|---|
| 6 | 56 | 0.91 | 37.5° | 0.94 | 0.94 | 28.6° | 0.90 |
| 10 | 156 | 0.98 | 24.7° | 0.88 | 1.11 | 17.8° | 0.86 |
| 14 | 306 | 1.11 | 18.0° | 0.86 | 1.28 | 12.9° | 0.85 |
| 16 | 400 | 1.17 | 15.8° | 0.86 | 1.36 | 11.3° | 0.85 |

  At 10 m depth, a 14 s swell is shoaled about 21% more than a 6 s swell of the same offshore height (1.11 vs 0.91). It has also turned to within 18° of shore-normal, versus 37.5° for the 6 s swell.

### Inferences
- For a lightweight model, apply Kr to the component of direction relative to the beach normal *after* the window/diffraction factor. Kr ≈ sqrt(cos θ0) is a reasonable asymptote once θ near breaking is small (cos θ_b ≈ 1). The breaking-height formulas in section 8 already include shoaling, so do not also apply Ks.
- The straight-parallel-contour assumption fails at headland-bound Sydney beaches. Real bathymetry (reefs, a sand lobe at mid-beach) causes focusing and defocusing, which only a ray or spectral model (SWAN) captures. Treat Kr as an angle-to-beach penalty, not a bathymetric truth.

### Gaps
- I did not fetch the CEM Part II-3 shoaling and refraction pages: the tpub mirror failed its TLS certificate check. The formulas above are the standard ones and agree with Apsley and Delft.

## 3. Diffraction behind a headland/breakwater (Sommerfeld/Penney & Price; Goda random-wave diagrams; Kd vs angle and smax)

### Takeaway
For monochromatic waves, the Penney & Price (Sommerfeld) solution gives Kd ≈ 0.5 (height) on the geometric shadow line, falling off into the shadow at a rate that depends on r/L. For real directional random seas, Goda et al. (1978) showed that diffraction depends mainly on the directional spreading parameter smax. A narrow-spread long swell (smax = 75) penetrates the shadow much *less* than a wind sea (smax = 10). Kraus (1984) gives a closed-form fit that is ideal for a per-beach calculation:

  K(θ) = sqrt( 0.5 · [ tanh( smax·θ / W ) + 1 ] ),  W = −0.000130·smax² + 0.270·smax + 5.31,  θ in radians (negative = into shadow).

### Cited Findings
- Penney & Price (1952) showed that Sommerfeld's (1896) solution for light at a semi-infinite screen applies to linear water waves passing a thin, rigid, impermeable breakwater in constant depth. — [ICCE paper on semi-infinite breakwater diffraction](https://icce-ojs-tamu.tdl.org/icce/article/download/2517/2183/10924)
- With no reflection, the monochromatic wave height along the shadow line stays at 0.5 of the incident height. — [ICCE paper](https://icce-ojs-tamu.tdl.org/icce/article/download/2517/2183/10924)
- The CEM defines Kd = Hd/Hi and notes that it depends on incident wave period and direction of approach. — [CEM EM 1110-2-1100 Part II-7](https://coastalengineeringmanual.tpub.com/Part-II-Chap7/Part-II-Chap70010.htm)
- Monochromatic diffraction methods that ignore the spectrum can give incorrect predictions of wave height near structures, in fact overestimates. Goda et al. (1978) and Goda (1985) provide random directional-spectrum diffraction diagrams for a semi-infinite breakwater or large island, parameterised by smax. — [USACE CETN-I-18 (rev. 3/88), "Irregular wave diffraction by Goda's method"](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content)
- Recommended deep-water (smax)0: wind waves = 10; short swell (large steepness) = 25; long swell (small steepness) = 75. — [CETN-I-18](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content); [Goda & Suzuki 1975, PARI](https://www.pari.go.jp/en/1975/12/197512023001.html)
- Kraus (1984), J. Waterway Port Coastal Ocean Eng. 110(2):276–282, gives the closed form K(θ) = sqrt(0.5[tanh(smax·θ/W) + 1]), with θ the angle from the incident wave direction at the tip, in radians. The text of the note prints W = −0.000103 smax² + 0.270 smax + 5.31. Its worked example uses −0.000130 and gets W = 24.83 for smax = 75, which is consistent only with 0.000130. The difference in W is under 1% (24.83 vs 24.98), so it does not matter in practice. Worked example: smax = 75, θ = −30° gives K = 0.201, "comparable to" Goda's diagram. Kraus's fit is good except where K < 0.2, where it underestimates (non-conservative close behind the structure). — [CETN-I-18](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content)
- smax grows as waves refract into shallow water (Goda 1985, Fig. 1 of CETN-I-18). Worked example: (smax)0 = 10, d/L0 = 0.0407, α0 = 30° gives smax = 75 at the breakwater tip. Refraction narrows the directional spread. — [CETN-I-18](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content)
- The CEM reproduces Goda's (2000) diagrams for a semi-infinite breakwater and for a gap (B/L = 1) under directional random waves at normal incidence. — [CEM Fig. II-7-13](https://coastalengineeringmanual.tpub.com/Part-II-Chap7/Part-II-Chap70020.htm); [CEM Fig. II-7-14](https://coastalengineeringmanual.tpub.com/Part-II-Chap7/Part-II-Chap70021.htm)
- (Computed from Kraus 1984) Height ratio K(θ). Negative θ is into the shadow, positive is on the lit side:

| θ (deg) | smax = 10 (wind sea) | smax = 25 (short swell) | smax = 75 (long swell) |
|---|---|---|---|
| +30 (lit) | 0.89 | 0.95 | 0.98 |
| +15 (lit) | 0.81 | 0.87 | 0.91 |
| 0 (shadow line) | 0.71 | 0.71 | 0.71 |
| −15 | 0.59 | 0.50 | 0.41 |
| −30 | 0.46 | 0.32 | 0.20 |
| −45 | 0.35 | 0.19 | 0.09 |
| −60 | 0.26 | 0.11 | 0.04 |
| −90 | 0.14 | 0.04 | 0.01 |

  W = 8.0 (smax 10), 12.0 (smax 25), 24.8 (smax 75). The fit has no r/L dependence: it is the far-field angular distribution.

### Inferences
- **Random vs monochromatic on the shadow line.** Kraus's fit gives 0.707 on the shadow line, meaning energy ratio 0.5, height ratio sqrt(0.5). Monochromatic Penney & Price gives 0.5 in height. The random-wave result is the energy-averaged one and is the right one to use with Hs.
- **Counter-intuitive period effect.** Goda's framework says long, clean swell (high smax) is *less* able to spread into a geometric shadow than a short-period wind sea. The common surfer observation that long-period swell "wraps" better comes mainly from refraction (section 2): long waves feel the bottom further offshore and turn toward the bay. It is not mainly diffraction. Within monochromatic theory, longer L does raise Kd at a fixed distance r (Kd depends on r/L), but that effect is confined to within a few wavelengths of the tip.
- **Monochromatic far field (standard Sommerfeld asymptotics, not from a fetched source).** Deep in the shadow, |Kd| ≈ 1 / (2π·sqrt(2r/L)·|sin(β/2)|)-type decay in r/L. For a 14 s swell (L ≈ 150–200 m in 10–20 m depth) and a beach 500 m behind the tip (r/L ≈ 3), that leaves roughly 0.05–0.15 at 30–60° into the shadow. That is comparable to the Kraus smax = 75 values, so the two approaches give the same order of magnitude in Sydney-scale embayments. Verify against Penney & Price before relying on these numbers.
- **Applying it to a headland.** θ is the angle at the headland tip between the incident swell direction and the line from the tip to the beach point. The headland is not a thin breakwater: it reflects, it has shoaling reef around the tip, and refraction around the tip's bathymetry adds energy. So K(θ) is a lower bound on sheltering leakage. A simple, defensible scheme: H_beach = H0 · K(θ_into_shadow, smax(T, steepness)) · Kr, followed by a breaking-height formula.

### Gaps
- I could not extract Goda's full diagram contours (the 1978 ICCE PDF is a scanned image), so only Kraus's fit values are tabulated. Kraus notes the fit underestimates where K < 0.2.
- I found no explicit closed-form smax-vs-steepness formula (the Goda & Suzuki 1975 figure). The categorical 10/25/75 guidance is what the sources support.
- I found no sourced shallow-water smax conversion beyond the single CETN worked point.

## 4. What CEM (USACE) and Goda directly provide

### Takeaway
The directly usable items are: (a) Kd = Hd/Hi and the Goda random-wave diagrams (CEM Figs II-7-13 and II-7-14); (b) the smax categories 10/25/75 and their increase on refraction; (c) Kraus's closed-form fit via CETN-I-18; (d) H = H0·Ks·Kr; (e) the Komar & Gaughan breaking height, which the CEM includes; (f) the parabolic bay-shape equation in CEM Part III-2.

### Cited Findings
- See the citations in sections 3, 5 and 8. The CEM includes the parabolic bay-shape equation, with coefficients in Fig. III-2-27b taken from Silvester & Hsu (1993). — [CEM Part III-2](https://coastalengineeringmanual.tpub.com/Part_III-Chap_2/Part_III-Chap_20060.htm)
- Goda & Suzuki: a method to infer smax from deep-water steepness, with typical values of 10 (wind sea) and 75 (swell). — [PARI 1975](https://www.pari.go.jp/en/1975/12/197512023001.html)
- Field data (Japan) show that for wind sea, directional spreading broadens as steepness Hm0/Lp increases, while for swell it narrows. A 2021 study found that the swell guidance (Goda et al. 1975) is not fully confirmed: in its data the dependence on wave age and steepness was weak, though the Goda reference values still bracketed the observations. — [Le Merle, OSTST 2020](https://meetings.aviso.altimetry.fr/fileadmin/user_upload/tx_ausyclsseminar/files/OSTST2020_EvaLeMerle.pdf); [JSCE Kaigan 2021 77(2) I_49](https://www.jstage.jst.go.jp/article/kaigan/77/2/77_I_49/_article/-char/en)

### Inferences
- For Open-Meteo partitions, use smax ≈ 10 for wind waves. For swell, scale 25 → 75 as steepness H0/L0 falls; for example, smax = 75 if H0/L0 < ~0.005 (long, clean groundswell), 25 if > ~0.015, and interpolate between. These thresholds are my heuristic, not sourced values.

### Gaps
- I could not access Goda's book text directly. Its exact tables and equations (for example the Mitsuyasu spreading function, s = smax·(f/fp)^5 below the peak and (f/fp)^−2.5 above) are standard but were not verified in a fetched source.

## 5. Parabolic bay shape / headland-bay beach models (Hsu & Evans; González & Medina; MEPBAY)

### Takeaway
The parabolic bay-shape equation, R/R0 = C0 + C1(β/θ) + C2(β/θ)², relates a beach's static-equilibrium planform to the diffraction point (headland tip) and the dominant wave obliquity β. It can be inverted to infer the *dominant effective wave direction* at the diffraction point from a beach's shape. That is useful for calibrating which offshore direction a beach is "tuned" to. It does not give wave height along the beach.

### Cited Findings
- Equation: R/R0 = C0 + C1(β/θ) + C2(β/θ)². R is the radius from the diffraction point (headland tip) to the shoreline at angle θ from the wave crest line. R0 is the control line from the diffraction point to the downcoast control point. β is the angle between the control line and the wave crest at the diffraction point. — [IHSet docs (Hsu & Evans 1989)](https://ihcantabria.github.io/IHSetDocs/Model_description/models/static_equilibrium/equilibrium_planform/ihsetgonzalez.html); [CEM Part III-2](https://coastalengineeringmanual.tpub.com/Part_III-Chap_2/Part_III-Chap_20060.htm)
- C0 + C1 + C2 = 1 (so that R = R0 at θ = β). The coefficients are tabulated for β = 20–80° at 2° intervals in Silvester & Hsu (1993), Table 4.2. The fit came from 14 Australian bay beaches and 7 physical models (Ho 1971). One worked example: β ≈ 30° gives C0 = 0.05, C1 = 1.14, C2 = −0.19. — [CEM Part III-2](https://coastalengineeringmanual.tpub.com/Part_III-Chap_2/Part_III-Chap_20061.htm); [Coastal Inlets tech note (Moreno)](https://coastalinlets.tpub.com/cs99-moreno/cs99-moreno0006.htm)
- González & Medina (2001), used in MEPBAY and SMC, set R0 = Y / cos(α_min), with α_min = 90° − β and α_min = atan[ (βr⁴/16 + (βr²/2)·(Y/Ls)) / (Y/Ls) ], βr = 2.13 (from 26 Spanish beaches). Y is the distance from the control point to the downcoast straight alignment. Ls is a wavelength computed from the wave period and the depth at the diffraction point. — [IHSet docs](https://ihcantabria.github.io/IHSetDocs/Model_description/models/static_equilibrium/equilibrium_planform/ihsetgonzalez.html)

### Inferences
- In the González & Medina formula, α_min depends on Y/Ls. Longer periods (larger Ls) lower Y/Ls, which raises α_min and lowers β. In other words, the planform "expects" long-period waves to turn more strongly into the bay. This is consistent with section 2.
- Usable for a beach bot: digitise each beach's planform and fit β to find the dominant equilibrium wave direction at the headland tip. Compare it to the swell directions that actually produce surf. The shadow zone is the part of the beach near the headland at angles inside the diffraction line, and exposure rises toward the straight downcoast tangent. This is qualitative only; for a height gradient, use Kraus K(θ) along the beach.

### Gaps
- I did not obtain the full Silvester & Hsu β-coefficient table or a sourced polynomial fit to it.
- I found no published relation that turns a parabolic-bay fit directly into alongshore wave height.

## 6. Simple parametric "wrap" models outside the window and justified widths for 6/10/14 s

### Takeaway
I found no published "exponential/cosine wrap" model for surf forecasting. The physically justified parametric form is Kraus's tanh law, which is a smoothed step of width about W/smax radians. That gives e-folding-type transition half-widths of about 46° (smax 10), 27° (smax 25) and 19° (smax 75). Mapping period to smax yields roughly 6 s → ~45°, 10 s → ~25–30°, 14 s → ~20° for the diffraction part. Long-period swell's better wrap comes from refraction instead, which shifts the effective incidence angle toward the beach normal.

### Cited Findings
- The functional form K(θ) = sqrt(0.5[tanh(smax·θ/W) + 1]) is a tanh step. The argument reaches 1 at θ = W/smax: 8.0/10 = 0.80 rad (46°); 12.0/25 = 0.48 rad (27°); 24.8/75 = 0.33 rad (19°) (computed). — [CETN-I-18 / Kraus 1984](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content)
- smax categories: 10 wind waves, 25 steep short swell, 75 low-steepness long swell. — [CETN-I-18](https://erdc-library.erdc.dren.mil/server/api/core/bitstreams/81b728f8-7039-4ef8-e053-411ac80adeb3/content)

### Inferences
- Recommended lightweight model per partition: E_factor(θ) = 0.5·[tanh(smax·θ/W) + 1], where θ is the signed angle (radians) between the swell direction and the nearest window edge (positive inside the window). Then H_eff = H0·sqrt(E_factor).
  - Mapping (heuristic): smax ≈ 10 for T ≤ 7 s or wind-sea partitions, ≈ 25 for 8–11 s, ≈ 50–75 for T ≥ 12 s with low steepness.
  - This gives H/H0 = 0.71 exactly at the window edge, which is physically right for random waves. Note that a pure-cosine wrap gives 1.0 at the edge and is too generous.
- Add a refraction/obliquity factor for directions *inside* the window that are oblique to the beach normal: Kr ≈ sqrt(cos θ_rel) with θ_rel capped at about 80°. For long periods the effective θ_rel is reduced by refraction. One heuristic way to do this is to apply Snell's law from deep water to a reference depth h_ref ≈ 10–15 m for the window edges (section 2 table: at 10 m, 45° becomes 37.5° for 6 s, 24.7° for 10 s, 18° for 14 s).
- Full models (SWAN/REF-DIF/phase-resolving) handle refraction over real bathymetry, diffraction (SWAN only approximately, through phase-decoupled diffraction), reflection, and frequency-direction spreading at once. A lightweight model cannot reproduce reef focusing, so per-beach calibration factors fitted against observations are the usual trade-off, as with Surfguru's surfer feedback.

### Gaps
- No source gives exponential or cosine wrap widths for 6/10/14 s. The widths above are derived from the Kraus/Goda tanh law plus my smax-period mapping heuristic.

## 7. Combining multiple wave trains (primary swell, secondary swell, wind sea)

### Takeaway
Combine as energy: Hs_total = sqrt(Σ Hs,i²), applied *after* each partition is transformed with its own direction, period and smax. This follows directly from Hs = 4·sqrt(m0) and the additivity of spectral variance. Breaking-height formulas, however, are non-linear in T, so combine transformed heights, and use the dominant (highest-energy) partition's period for any period-dependent breaking step.

### Cited Findings
- Hs = 4.0·sqrt(total variance), and the total variance is the sum of variance over all spectral bins. — [Oceanweather FIELDSDEF](https://oceanweather.com/about/FIELDSDEF-Website.pdf)
- Hs relates to the zeroth spectral moment m0. — [UN Ocean Prediction wiki](https://unoceanprediction.org/resources/wiki/chapters/382)
- The total Hs is not the simple arithmetic sum of sea and swell heights. Partitioning schemes differ, for example Sofar uses an 8 s cut-off. — [Sofar Ocean](https://www.sofarocean.com/posts/spotter-data-partitioning-for-sea-and-swell); [Portilla et al. 2009](https://data-ww3.ifremer.fr/BIB/Portilla_etal_JTECH2009.pdf)

### Inferences
- Hs_total = sqrt(Σ Hs,i²) follows from the cited definitions when partitions do not overlap. Open-Meteo's wind-wave, swell and secondary-swell partitions are close to this, but their squares may not sum exactly to the total wave_height. Check for that empirically.
- Surf-relevant "face" height is usually driven by the dominant swell. A max(H_i) or an energy sum weighted toward longer period may match surfer perception better than the pure energy sum. That is a calibration choice, not physics.

### Gaps
- I found no source that gives an explicit closed-form equation for this combination; I derived it from the definitions above.

## 8. Breaking wave height and period dependence

### Takeaway
Komar & Gaughan (1972): Hb = 0.39·g^(1/5)·(T·H0²)^(2/5), dimensionally consistent with g^+0.2. For the same offshore height, Hb ∝ T^0.4: going from 6 s to 14 s raises Hb by (14/6)^0.4 ≈ 1.40×. For H0 = 1.5 m, Hb ≈ 1.74 m (6 s), 2.14 m (10 s), 2.45 m (14 s) (computed). H0 here should be the *unrefracted deep-water equivalent* height, i.e. offshore H × sheltering/diffraction × refraction factors.

### Cited Findings
- Komar & Gaughan (1972, ICCE) derived Hb = k·g^(1/5)·(T·H0²)^(2/5) from Airy theory, energy-flux conservation and a breaking index, and fitted k = 0.39 to three laboratory data sets and one field data set. — [Komar & Gaughan 1972, ICCE](https://icce-ojs-tamu.tdl.org/icce/article/view/2763); [TRID record](https://trid.trb.org/View/14064)
- A field study found the formula predicts breaking height adequately within the limits of deep-water inputs, neglecting refraction and friction. — [ICCE paper](https://icce-ojs-tamu.tdl.org/icce/article/download/3282/2946/13988)
- Surfguru uses Komar & Gaughan on WAVEWATCH III output and calls it "very generic", correcting it with surfer observations. — [Surfguru](https://surfguru.com.br/conteudo/estimating-wave-height-at-surf-spots-2024-07-05-29190.html)
- One search-engine summary claimed g^0.2 is a typo for g^−0.2. Checking dimensions shows this is wrong: m^0.2·s^−0.4 from g^0.2 times s^0.4·m^0.8 from (T·H0²)^0.4 gives metres. g^+0.2 is correct (computed check). — [arXiv 1904.06821 (states Hb = 0.39 g^0.2 (T H0²)^0.4)](https://arxiv.org/pdf/1904.06821)
- (Computed) Hb/H0 for H0 = 1.5 m: 1.16 (6 s), 1.30 (8 s), 1.43 (10 s), 1.53 (12 s), 1.63 (14 s), 1.72 (16 s). In general Hb/H0 = 0.39·g^0.2·T^0.4·H0^(−0.2), so smaller waves are amplified relatively more.

### Inferences
- Pipeline per partition i: H0',i = H_i · sqrt(E_window(θ, smax_i)) · Kr_i. Then Hb,i = 0.39·g^0.2·(T_i·H0',i²)^0.4. Combine as Hb = sqrt(Σ Hb,i²), or apply Komar–Gaughan to the energy-combined H0' with the dominant period. The second keeps the T-weighting coherent.
- An alternative check is depth-limited breaking Hb ≈ γ·hb with γ ≈ 0.78 (McCowan). I did not find a fetched source for γ = 0.78.

### Gaps
- I did not verify other breaker formulas (Larson-Kraus, Rattanapitikon & Shibayama) or the CEM's exact rendering of Komar & Gaughan.
- I found no Sydney-specific validation of Komar & Gaughan.
