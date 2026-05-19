# Prototype foundations — aristech

**Last updated:** 2026-05-19
**Status:** Draft — first complete pass on the three Priority-1 axes
identified after PR #4 (state-of-the-art survey), plus a focused
synthesis of Éric Darrouzet's contributions on the French side.
**Audience:** anyone about to design, source, or build the first
aristech prototype rig (hardware procurement, mechanical layout,
camera/servo/nozzle geometry, perception assumptions).
**Companion files:**

- [state-of-the-art.md](state-of-the-art.md) — narrative literature
  survey (Kaggle, GitHub, papers, auto-aim turrets, legal framework).
- [references.md](references.md) — centralised bibliography.

## Purpose

PR #4 closed the SOTA survey but flagged six second-priority axes that
the prototype design cannot proceed without. The three most blocking
were tackled in parallel: **behavioural biology at the hive entrance
(A)**, **hive geometry and sensor mounting (B)**, **hardware BOM and
energy autonomy (C)**. A fourth focused pass collated **Éric Darrouzet's
body of work (A.bis)** since he is the principal French specialist on
the species. This document consolidates the four passes into the
engineering inputs needed to sign the first BOM and build the first
mechanical rig.

The document is **applied engineering inputs**, not a literature
review. Where a finding directly drives a design constant (FOV, focal
length, strike-rate baseline, selectivity floor), it is called out as
such.

## A. Behavioural biology at the hive entrance

### Predation cycle

| Metric                                                              | Value                                                                                                              | Source                                                                                                                                                                                |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hunting technique                                                   | "Bee-hawking" — hornet hovers facing the landing board, grabs a returning forager mid-air, butchers it nearby      | [Tan et al. 2007](https://link.springer.com/article/10.1007/s00114-006-0210-2) ; [Monceau et al. 2014](https://link.springer.com/article/10.1007/s10340-013-0537-3)                    |
| Hovering position                                                   | Faces the hive, directly in front of the landing board; beekeeper reports ~20-50 cm but **no peer-reviewed value** | [Monceau et al. 2013, PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0066492) — qualitative only                                                          |
| Hover bout duration                                                 | A single hornet can hover near a colony for **> 25 min** trying to capture a bee                                   | [Tan et al. 2007](https://link.springer.com/article/10.1007/s00114-006-0210-2)                                                                                                         |
| Overall strike success                                              | **2.4 %** at hive entrance, density-dependent peak around **~8 simultaneous hornets**                              | [Robinet/Darrouzet group 2023, Sci. Reports](https://pmc.ncbi.nlm.nih.gov/articles/PMC10049882/)                                                                                       |
| Capture success on _A. mellifera_ vs _A. cerana_ (sympatric Yunnan) | ~3× higher on _A. mellifera_                                                                                       | [Tan et al. 2007](https://link.springer.com/article/10.1007/s00114-006-0210-2)                                                                                                         |
| Diet composition (field, France)                                    | Honeybees **38.1 %**, flies **29.9 %**, social wasps **19.7 %**                                                    | [Rome et al. 2021, MNHN/HAL](https://mnhn.hal.science/hal-03180854v1)                                                                                                                  |

**Engineering takeaway**: the target is **slow, persistent, and self-
orienting** toward the hive. A fixed-mount camera can exploit minutes-
long stationary hovers punctuated by sub-second strike events.

### Temporal pattern (diel / seasonal / weather)

| Window                | Activity                                                                                                | Source                                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Diel — overall        | Diurnal flights **07:00–20:00**, peak **14:00–15:00**                                                   | [Poidatz et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6106190/)                                                                     |
| Diel — seasonal shift | Jul–Aug: peaks at non-central hours; Sep–Oct: peaks at central hours (cooler mornings push later start) | [Rojas-Nossa et al. 2025](https://link.springer.com/article/10.1007/s13592-025-01158-z)                                                      |
| Temperature window    | Most numerous between **~15–26 °C**                                                                     | [Rojas-Nossa et al. 2025](https://link.springer.com/article/10.1007/s13592-025-01158-z)                                                      |
| Humidity              | Favoured at RH > 60 %                                                                                   | [Rojas-Nossa et al. 2025](https://link.springer.com/article/10.1007/s13592-025-01158-z)                                                      |
| Wind / rain           | Predation at hives **decreases with wind speed**; rain suppresses hunting                               | [Monceau et al. 2013, Apidologie](https://link.springer.com/article/10.1007/s13592-012-0172-7)                                               |
| Season (France)       | ~5 months activity; peak Aug–Oct, ending Nov                                                            | [Monceau et al. 2013](https://link.springer.com/article/10.1007/s13592-012-0172-7)                                                           |

**Engineering takeaway**: a typical active-detection window is ~6 h/day
(early afternoon, in the temperature band). This bounds the daily Wh
budget (see § C) and means aristech can sleep aggressively outside the
active window — a major win for solar autonomy.

### Flight kinematics

| Quantity                            | Value / range                                                                | Source                                                                                                                                                                                                                                              |
| ----------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ground speed (foraging, unladen)    | **6.66 ± 2.31 m s⁻¹**                                                        | [Sauvard et al. 2018, PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198597)                                                                                                                                          |
| Ground speed (homing, laden)        | **4.06 ± 1.34 m s⁻¹**                                                        | [Sauvard et al. 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198597)                                                                                                                                                    |
| Single-flight distance (tethered)   | 10–30 km                                                                     | [Sauvard et al. 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198597)                                                                                                                                                    |
| Foraging range around nest          | ~1 000 m typical; homing demonstrated to 5 000 m                             | [Poidatz et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6106190/)                                                                                                                                                                            |
| Wingbeat fundamental                | **Not measured for _V. velutina_ specifically.** Inferred ~100–125 Hz from congeners | [Kawakita & Ichikawa 2019 (cited)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10107170/) ; [Hall et al. 2025](https://www.sciencedirect.com/science/article/pii/S0168169925004132). _A. mellifera_ reference ≈ 251 Hz — 2× separation.                  |
| Hover stability, turn radius, reaction latency | **Not measured anywhere** — clear open gap                                   | _unverified_                                                                                                                                                                                                                                        |

**Engineering takeaway**: at 6.7 m s⁻¹ a strike covers ~11 cm per 60-Hz
frame. A 60 Hz capture pipeline keeps temporal smearing under one
hornet body length and is sufficient for a SORT-class tracker. The
wingbeat split (~125 vs ~251 Hz) gives a clean 2× ratio in spectral
space for the audio modality (§ implications for [state-of-the-art.md](state-of-the-art.md)).

### Visual discrimination from _Apis mellifera_

- **Body length** — _V. velutina_ worker **~20 mm** (queen 30 mm), _A.
  mellifera_ worker **~12–14 mm** → 1.5–2× longer and visibly bulkier.
  Source: [MNHN ID sheet](https://sitesv2.anses.fr/en/system/files/private/Vespa%20velutina%20Identification%20Sheet%20MNHN_2.pdf).
- **Colour cues** — dark velvety thorax+abdomen, **orange band on
  tergite 4**, thin yellow on T1, **yellow tarsi** ("pattes jaunes").
  Yellow tarsi are the most reliable far-field colour cue.
- **Posture during hover** — sustained stationary hovering facing the
  hive is itself diagnostic: _A. mellifera_ does not hover in front of
  its own entrance; it lands directly. The "legs dangling during
  hover" cue is widely cited by beekeepers but **not peer-reviewed**.
- **Wingbeat acoustic signature** — sufficient to enable automated
  species discrimination per [Hall et al. 2025](https://www.sciencedirect.com/science/article/pii/S0168169925004132)
  (98.7 % accuracy on hovering sound alone).

**Engineering takeaway**: no single visual cue is robust at 1–2 m.
Aristech's classifier must fuse three weak cues — apparent size (1.5–
2×), yellow-tarsi patch, stationary-hover trajectory — and confirm
with acoustic spectrum when present.

### Colony stress response

- **_A. m. mellifera_ lacks effective heat-balling.** Core ball
  temperatures stay below the wasp's 45.7 °C lethal limit; _A. cerana_
  reaches ~46 °C in ~3 min and kills the hornet. [Ken et al. 2005](https://link.springer.com/article/10.1007/s00114-005-0026-5) ;
  [Arca et al. 2014](https://www.sciencedirect.com/science/article/abs/pii/S0376635714001223).
- **No wing-shimmering, no extra guard recruitment** in _A. mellifera_;
  _A. cerana_ triples guards and shimmers. [Tan et al. 2007](https://link.springer.com/article/10.1007/s00114-006-0210-2) ;
  [Arca et al. 2014](https://www.sciencedirect.com/science/article/abs/pii/S0376635714001223).
- **"Foraging paralysis"** — under sustained hornet pressure,
  _A. mellifera_ foragers cluster on the landing board and stop
  flying, risking winter starvation. [Requier et al. 2019](https://www.researchgate.net/publication/329111215).
- **Sting venom = alarm pheromone**, recruiting more hornets to a
  productive hive. [Cheng et al. 2017](https://journals.biologists.com/jeb/article/220/4/645/18673/).

**Engineering takeaway**: the French honeybee race is essentially
**defenceless** without aristech-class external intervention. A missed
strike that triggers a sting cascades hornet recruitment → the
perception+actuation loop must minimise false negatives, not just
false positives. The deterrent itself must not add stress: brief,
laterally-aimed jet pulses, never sprayed on the hive face.

### Deterrent efficacy in literature

| Stimulus                                                  | Reported effect                                                                          | Habituation?                       | Source                                                                                                                                          |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Electric harp (1 harp per hive)                           | **−89 %** predation pressure at apiary scale; ~68 % of captures are _V. velutina_       | Not reported                       | [Rojas-Nossa et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9825959/)                                                                    |
| Harp (4 359-insect sample, Thiéry & Darrouzet)            | **> 90 %** _V. velutina_ in catch, selectivity **0.75 ± 0.34**; few honeybee escapes via 6 mm mesh | Not reported                       | [Thiéry & Darrouzet 2023, Entomologia Generalis](https://www.schweizerbart.de/papers/entomologia/detail/43/103168/)                            |
| Hive muzzle (entrance grid)                               | **−41 %** foraging paralysis vs control                                                  | n/a                                | [Requier et al. 2020 / MNHN](https://frelonasiatique.mnhn.fr/la-museliere/)                                                                     |
| Baited traps (spring foundresses)                         | Effective only if repeated **4+ consecutive springs**; massive bycatch                   | n/a                                | [ITSAP](https://itsap.asso.fr/articles/frelon-asiatique-evaluation-de-l-efficacite-du-piegeage-de-printemps)                                    |
| Baited traps — best products                              | Catch only **3.65 %** target in spring, **1.35 %** in autumn — bycatch problem severe   | n/a                                | [Rojas-Nossa/Darrouzet et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10778013/)                                                         |
| Auditory / colour / hair stimuli (lab)                    | Trigger defensive aggression in hornets but **no documented deterrent effect**           | Not measured                       | [Cheng et al. 2021, Insects](https://pmc.ncbi.nlm.nih.gov/articles/PMC8034368/)                                                                 |
| Water mist, light strobes, predator decoys                | **No peer-reviewed efficacy data** found                                                 | _unverified_                       | _unverified_                                                                                                                                    |

**Engineering takeaway — the harp is the published benchmark to beat
(or match).** Aristech is non-lethal and non-contact, so it cannot
match the harp's mechanical interception count one-for-one; the value
proposition is **complementary selectivity** (zero non-target kill, no
carcass disposal) and **scalability** (no daily maintenance vs harp
weekly cleaning). Side-by-side evaluation against a harp on the same
rucher is the right validation protocol.

## A.bis — Synthesis of Éric Darrouzet's contributions (IRBI / Université de Tours)

### Profile

Éric Darrouzet is maître de conférences (HDR) at IRBI — Institut de
Recherche sur la Biologie de l'Insecte, UMR CNRS 7261, Université de
Tours — where he leads the FRELON group within the ECEIS team
(Chemical Ecology and Evolution of Social Insects). He has worked on
_Vespa velutina nigrithorax_ since 2008 and is one of France's most-
cited specialists on the species' biology, chemical ecology, and
control. Lab page: [annuaire Université de Tours][d1] ;
project site [frelonasiatique.univ-tours.fr][d2] ; publications index
[frelonasiatique.univ-tours.fr/publications.html][d3].

[d1]: https://www.univ-tours.fr/annuaire/m-eric-darrouzet
[d2]: http://frelonasiatique.univ-tours.fr/
[d3]: http://frelonasiatique.univ-tours.fr/publications.html

### Peer-reviewed publications (selected, V. velutina-relevant)

| Year | Title                                                                                                | Venue                                                                                                                          | Key finding for aristech                                                                                |
| ---- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 2017 | [Rapid spread of the yellow-legged hornet in France][dp1]                                            | J. Applied Ecology 54:205-215                                                                                                  | Control measures have **limited demographic effect**; spread dominated by human-mediated jumps.          |
| 2018 | [Searching for nests of the invasive Asian hornet using radio-telemetry][dp2]                        | Communications Biology / PMC6123801                                                                                            | VHF tags 0.28 g viable when tag:hornet < 0.8; workers fly back up to **1.33 km** to nest.               |
| 2020 | [Characterizing thermal tolerance in _V. velutina nigrithorax_][dp3]                                 | PLOS ONE e0239742                                                                                                              | Steam injection kills all hornets in **~13 s**; biology-friendly nest destruction.                       |
| 2022 | [Designing a sex pheromone blend][dp4]                                                               | Entomologia Generalis — HAL hal-03562571                                                                                       | Blend **4-OOA : 4-ODA : 5-ODA ≈ 2:4:1** attracts males in field.                                         |
| 2023 | [Electrical traps efficient and selective against _V. velutina_ workers at hives (Thiéry & Darrouzet et al.)][dp5] | Entomologia Generalis 43(5)                                                                                                    | **> 90 %** target rate on 4 359 insects; selectivity **0.75 ± 0.34**; few honeybee escapes via 6 mm mesh. |
| 2023 | [Density of predating hornets disturbs honeybee 3D flight][dp6]                                      | Sci. Reports / PMC10049882                                                                                                     | **2.4 %** overall predation success; peaks at ~8 hornets, drops above.                                  |
| 2024 | [Comparison of effectiveness and selectiveness of baited traps][dp7]                                 | Animals 14(1):129 / PMC10778013                                                                                                | Best baited traps catch only **3.65 %** target in spring, **1.35 %** in autumn — bycatch is the problem. |

[dp1]: https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2664.12724
[dp2]: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6123801/
[dp3]: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239742
[dp4]: https://hal.science/hal-03562571/
[dp5]: https://www.schweizerbart.de/papers/entomologia/detail/43/103168/
[dp6]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10049882/
[dp7]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10778013/

### Books and popular-science

| Title                                                                          | Year      | Publisher          | Practical takeaways                                                                                  |
| ------------------------------------------------------------------------------ | --------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| _Le frelon asiatique, un redoutable prédateur — le connaître pour mieux le combattre_ (1st ed.)  | 2019      | Éditions du SNA — ISBN 978-2-901764-02-1 | Biology, hunting behaviour, hive impact; explicit position that **no scientifically validated selective trap exists** as of writing. |
| _Le frelon asiatique, un redoutable prédateur_ (2nd ed., 160 pp.)              | 2023      | Éditions SNApiculture | Updated chapters on harps, pheromones, queen-trapping debate; same prudence about generalised trapping. |
| [The Conversation FR — "Le frelon asiatique, ce dérangeant prédateur"][dpop1] | 2020      | The Conversation   | Plain-language summary; reiterates that **mass spring trapping is not demonstrated effective** and removes competing foundresses. |

[dpop1]: https://theconversation.com/le-frelon-asiatique-ce-derangeant-predateur-147676

### Conferences, interviews, press

| Source                                                                                       | Date          | Topic                                            |
| -------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------ |
| [UNAF webinar — "Frelon asiatique : impacts et luttes"][di1]                                 | 18 Jan 2024   | Control methods, harps, pheromones               |
| [CNRS INEE — "Les phéromones, une solution de lutte"][di2]                                   | 2022          | Sex-pheromone blend & male trapping              |
| [France Bleu Touraine — Darrouzet spécialiste du frelon asiatique (3 parts)][di3]            | 2021          | Biology, spring queens, harps                    |
| [CNRS Vidéothèque — "Asian hornet: chronicle of a death awaited"][di4]                       | 2019          | Documentary featuring IRBI team                  |
| [France 3 Centre — "les chercheurs de l'IRBI délogent les frelons"][di5]                     | 2020          | Nest extraction & steam method                   |

[di1]: https://www.youtube.com/watch?v=fDAD1jNnwfA
[di2]: https://www.inee.cnrs.fr/fr/cnrsinfo/les-pheromones-une-solution-de-lutte-contre-le-frelon-asiatique
[di3]: https://www.francebleu.fr/emissions/9h50-la-touraine-l-honneur/eric-darrouzet-specialiste-du-frelon-asiatique-1
[di4]: https://videotheque.cnrs.fr/doc=4658
[di5]: https://france3-regions.franceinfo.fr/centre-val-de-loire/indre-loire/tours/tours-les-chercheurs-de-l-irbi-delogent-les-frelons-a-domicile-2052877.html

### What Darrouzet says about operational questions

- **Selective trapping** — Repeatedly states (book 2019/2023, The
  Conversation 2020, UNAF 2024) that **no commercial bait-trap is
  sufficiently selective**; quantified in [Rojas-Nossa/Darrouzet 2024][dp7]
  at only 1.35–3.65 % target capture. IRBI roadmap = replace food bait
  with sex-pheromone bait.
- **Spring queen trapping** — Discouraged. Spring is a competition
  phase where foundresses kill each other; trapping removes that
  intraspecific regulation, and Robinet/Suppo/Darrouzet 2017 modelled
  negligible demographic impact.
- **Deterrents (harps, water, sound, light)** — Endorses **electric
  harps** as the most evidence-backed hive-side measure:
  > 90 % target rate, low honeybee bycatch.
  **No peer-reviewed Darrouzet paper on water-jet, sound, or light
  deterrents** — `unverified`.
- **Acoustic / wingbeat** — **No published wingbeat-frequency
  measurement of _V. velutina_ by IRBI Tours** could be verified.
  Relevant optical/acoustic detection work (Sauvage et al. 2022,
  Hadjur et al. 2022) is not from Darrouzet's group. Mark `unverified`
  for any IRBI-sourced wingbeat constant.
- **Nest localisation** — Radio-telemetry ([Kennedy/Darrouzet 2018][dp2]):
  VHF tags 0.28 g, range up to 1.33 km. Thermal imaging viability
  (Lioy et al. 2021) is separate.

### Gaps Darrouzet himself flags as open

- Operational selectivity threshold for bait-traps ("no current trap
  is satisfactory").
- Real-world demographic impact of any trapping campaign (spring or
  summer).
- Field-validated pheromone-trap deployment protocol (dose, density,
  season).
- Long-term habituation / displacement effects of harps (UNAF 2024).

### Synthesis for aristech

1. **Strike-rate constant** — adopt **2.4 % overall predation success,
   density-dependent peak around ~8 simultaneous hornets** as the
   engineering baseline against which aristech's "miss reduction" is
   benchmarked.
2. **Selectivity bar** — Darrouzet's harp paper sets a published
   target: **> 90 % _V. velutina_ in catch, < 2 % non-target**.
   Aristech's vision pipeline must meet or exceed that selectivity to
   be defensible against IRBI's own published standards.
3. **No IRBI-validated wingbeat frequency** for _V. velutina_ — do not
   cite an IRBI-sourced wingbeat number; rely on Sauvage et al. and
   the dedicated bioacoustics literature, and treat the gap as
   `unverified`.
4. **Open in-house measurements** — hover distance / height, turn
   radius, reaction latency are not measured in any Darrouzet paper.
   These remain in-house engineering measurements to perform at the
   prototype rig.
5. **Communication framing** — aristech is a **hive-level deterrent**,
   not a queen-control tool. Align with Darrouzet's published position
   that mass spring trapping is ineffective and harmful to
   intraspecific regulation.
6. **Harp as benchmark, not competitor** — position aristech as a
   **non-contact, non-lethal complement** (no electrocution, no
   carcass disposal) with a side-by-side efficacy comparison planned
   in the validation campaign.

## B. Hive geometry and sensor mounting

### Standard French hive dimensions

| Type                                    | External W × D × H (body, mm) | Planche d'envol W × D (mm)              | Notes                                                                       |
| --------------------------------------- | ----------------------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| **Dadant 10 cadres** (dominant FR)      | 500 × 430 × 315               | floor 540 × 430, board protrudes 80-110 | Icko/Rucheco standard. Entrance slot ~380 × 10 mm. Frame 420 × 270.         |
| **Dadant 12 cadres**                    | 540 × 450 × 315               | similar, slightly wider                 | Less common, pro apiaries.                                                  |
| **Langstroth**                          | 510 × 420 × 238               | floor protrudes 50-80                   | Internal 450 × 380 × 310; world standard, less common in FR.                |
| **Warré**                               | ~360 × 360 × ~210/body        | very small, often none                  | 30×30 internal; vertical stack; tiny landing area — hard target for vision. |
| **Voirnot**                             | ~395 × 395 × 360              | floor ≈ 410 × 430                       | Cubic 360×360 internal; niche in Alsace/Jura.                               |
| **Layens**                              | ~580 × 470 × 380 (20 cadres)  | front-entrance, ~470 wide               | Horizontal hive; long entrance slot.                                        |

Stand height in France: **40-50 cm** above ground. Entrance orientation:
**SE preferred** (morning sun, afternoon shade). Sources: [Icko
Apiculture — Dadant 10][b1], [ApiaRobotics — dimensions et comparaison][b2],
[Apiculture.net — bien organiser votre rucher][b3].

[b1]: https://www.icko-apiculture.com/ruche/ruches-completes/ruche-dadant-10-cadres.html
[b2]: https://apiarobotics.com/fr/connaissances/dimensions-et-comparaison-des-ruches
[b3]: https://www.apiculture.net/blog/bien-organiser-rucher-n12

### Critical positioning constraints

- **Sightline to landing board unobstructed by foragers** — at peak flow
  the planche d'envol is carpeted with bees; a low oblique angle (< 15°)
  is masked. Aim for **30–60° downward** from above.
- **Hovering volume in front of entrance** — _V. velutina_ hawks at
  ~5–30 cm out, hovering 5–20 cm above the board; this cylinder
  (~40 W × 30 D × 30 H cm) must be inside FOV and in focus.
- **No moving shadow on the entrance** — bees alarm on overhead shadows.
  Mount **off-axis** (lateral or above-front), not directly between sun
  and entrance.
- **Bee-touch tolerance** — orientation flights bring bees within 5 cm
  of any near-hive object; the lens window must be flat, smooth, non-
  grippable, and cleanable (propolis, faeces, pollen dust).
- **No perch geometry** — avoid horizontal rods or ledges near the
  entrance; hornets use perches to ambush.
- **South-facing lens kills sensors** — direct sun on a CMOS at midday
  can saturate and, with a focusing lens, scorch the colour filter
  array. Use a sunshade visor.

### Mounting strategies (prior art)

| Project                                            | Mount type                                                          | Camera                | Distance to entrance         | Pros / cons                                                                 |
| -------------------------------------------------- | ------------------------------------------------------------------- | --------------------- | ---------------------------- | --------------------------------------------------------------------------- |
| [BeeAlarmed][bp1] (Hickert)                        | 3D-printed frame screwed to hive front, top-down view of plate      | Pi Cam v2/v3          | ~15-25 cm above board        | + rigid, repeatable, top-down view. − blocks beekeeper inspections.         |
| [Gratheon Entrance Observer][bp2]                  | Hardware unit fixed to hive front, on-edge analysis                 | Pi-class cam          | ~10-20 cm                    | + commercial, weather-managed. − closed hardware, costly per hive.          |
| [VespAI][bp3] (Oxford, Nature 2024)               | Bait-station + overhead camera on separate post                     | Pi 4 + camera         | ~30 cm overhead of bait card | + standardised illumination. − doesn't see hawking at hive entrance.        |
| [vespCV][bp4]                                      | Pi 4 + USB cam, tripod or post near apiary                          | Generic webcam / Pi cam | variable                  | + cheap. − no calibrated geometry, low precision.                          |

[bp1]: https://github.com/BeeAlarmed/BeeAlarmed
[bp2]: https://gratheon.com/about/products/beehive_camera/
[bp3]: https://www.nature.com/articles/s42003-024-05979-z
[bp4]: https://github.com/vespCV/vespcv

**Implication for aristech**: none of the prior art targets a water-
jet turret **co-aligned** with the camera. The closest analog is
BeeAlarmed's hive-mounted bracket. The proposed v1 layout is a **rigid
bar fixed to the hive roof, extending 80 cm forward and 25 cm above
the planche d'envol**, with camera + servo + nozzle at the tip.

### FOV and resolution targets for aristech

Pixel budget: a hornet (~30 mm body, ~45 mm wingspan) must occupy ≥30
px (YOLO-class detectors lose recall below this; VespAI/BeeAlarmed
publish on ≥40 px targets).

At 1080p (1920 horizontal px), for a hornet at distance _d_ (m) and
HFOV _θ_:

```text
px_per_cm = 1920 / (200·d·tan(θ/2))
```

Candidate optics on a Raspberry Pi HQ camera (1/2.3" IMX477,
6.287 × 4.712 mm):

- **6 mm lens, 63° HFOV** — at 1 m, 1.22 m horizontal coverage → hornet
  ≈ 47 px. Covers whole planche + hovering volume **with margin**.
  **Recommended for the v1 single-device layout** because the hovering
  volume must be seen, not just the impact zone.
- **16 mm telephoto, 24° HFOV** — at 1 m, 0.43 m coverage → matches the
  43 cm planche exactly; hornet ≈ 134 px. Excellent classification but
  no margin for hovering hornets above the board. Reject for v1.
- **Pi Cam v3 standard (66° H, 4.74 mm equiv.)** — at 0.6–0.8 m,
  ~0.78–1.04 m wide; hornet ≈ 55–70 px. Autofocus helps for targets at
  0.2–1.5 m. Budget alternative.

**Recommendation**: **Pi HQ + 6 mm wide lens, mounted ~80 cm in front of
the entrance, ~30° downward tilt.** This contradicts the BOM survey's
16 mm telephoto suggestion; reconciliation in § Cross-section synthesis
below — wider FOV wins for v1.

### Outdoor enclosure / IP rating

- **Target IP54 minimum, IP65 realistic for €30-50** (Sixfab-class).
  IP66+ adds cost without real-world gain in an apiary.
- **Lens window** = failure point: use a flat optical-grade acrylic /
  glass disc, not a curved dome (dome refraction distorts calibration).
  Hydrophobic coating helps.
- **Condensation**: pair a **Gore-Tex M12 breather vent** + silica
  desiccant pouch (~10 g, replace yearly).
- **Sun**: 3D-print or aluminium sunshade visor extending 4-5 cm in
  front of lens, secondary outer shell with 1-2 cm air gap.
- **Spider webs / propolis**: flush, screwless front face for 10 s
  cleaning.
- **Cabling**: M12 cable glands, no flying connectors.

### Multi-hive scaling

For a 5-30 hive rucher, **one device per hive** is the only design
that gives per-entrance turret aim (hornet attacks are concurrent at
peak). A shared **base station** (Pi mini-PC) with per-hive low-cost
sensor heads (ESP32-S3 + Grove Vision AI v2, à la `vespCV/gv2-esp32`)
is a cost-efficient alternative: ~€40-60 per head vs €150+ for a full
Pi 4. Tradeoff: edge inference quality drops; aristech must validate
that an ESP32-class NPU can hit ≥10 FPS at 30-px hornet recall before
committing to this topology.

### Calibration during install

Apiarist effort must stay **under 5 minutes per hive**. Recommended
flow:

1. Mount the bar to the hive roof at a fixed geometry (jig-printed for
   Dadant 10).
2. Place a **printed A4 calibration card with ArUco markers** flat on
   the planche d'envol.
3. One-shot CLI: camera detects markers → derives homography (entrance
   plane → image plane) and servo-aim mapping (servo angles ↔ image
   coords) via 4-6 servo sweeps onto marker centres.
4. Store geometry in a per-hive YAML.
5. Optional auto-discovery: the entrance slot is detectable as a dark
   rectangle of known aspect (380 × 10 mm on Dadant); fall back to
   manual ArUco if lighting is poor.

The apiarist does **not** touch focal length, exposure, or model.

### Open mechanical questions

- No published spec gives the exact protrusion of the Dadant 10
  planche d'envol; values vary 80-110 mm. Measure on the physical hive
  before finalising bar length.
- Wet-lens degradation in sustained rain not quantified in any
  V. velutina detection paper (expect -20 to -40 % recall); design
  fallback to "sound-only" or "shut nozzle" mode.
- ESP32-S3 + Grove Vision AI v2 FPS at hive entrance not peer-
  reviewed; aristech must benchmark before committing to the cheap-
  head architecture.

## C. Hardware BOM and energy autonomy

### Compute platform — 3 candidates

| Platform                                                  | Peak W    | Idle W | YOLOv8n@640 latency           | Price €              | EU availability                                                                                                                                                                                          |
| --------------------------------------------------------- | --------- | ------ | ----------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Raspberry Pi 5 8GB + AI HAT+ (Hailo-8L, 13 TOPS)**      | ~12 W     | 3 W    | ~9-12 ms (~85-100 FPS)        | ~85 + ~75 = **~160** | Good — Kubii / Pimoroni / Pi Hut. ([Pi AI HAT+][c1])                                                                                                                                                      |
| **Jetson Orin Nano Super Dev Kit (8GB)**                  | 15-25 W   | 7 W    | ~6-8 ms (~120 FPS, TRT FP16)  | ~280                  | Available via Arrow, Antratek, electrokit; intermittent stock 2025. ([Antratek EU][c2])                                                                                                                  |
| Raspberry Pi 5 8GB + Coral USB Accelerator                | ~10 W     | 3 W    | ~15-25 ms (compile penalty)   | ~160                  | Coral chronically constrained. ([Coral][c3])                                                                                                                                                              |

[c1]: https://www.raspberrypi.com/products/ai-hat/
[c2]: https://www.antratek.com/nvidia-jetson-orin-nano-super-developer-kit
[c3]: https://www.coral.ai/products/accelerator

**Recommendation**: **Pi 5 + AI HAT+ Hailo-8L**. Best perf/€/W;
Jetson wins on raw FPS but doubles power draw and halves solar budget.

### Camera + lens

| Component                                          | Spec                                       | Price €  | URL                                                                                                                  |
| -------------------------------------------------- | ------------------------------------------ | -------- | -------------------------------------------------------------------------------------------------------------------- |
| **Raspberry Pi HQ Camera (IMX477)**                | 12.3 MP, C/CS-mount, swappable optics      | ~50      | [raspberrypi.com][c4]                                                                                                |
| **Arducam M12 wide lens (LK004 kit, 6 mm pick)**   | 6 mm ≈ 63° HFOV (per § B reconciliation)   | ~25-35   | [Arducam docs][c5]                                                                                                   |
| Alternative: Pi Camera v3 (IMX708, fixed 4.74 mm)  | 66° HFOV, autofocus                        | ~30      | [Kubii][c6]                                                                                                          |

[c4]: https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/
[c5]: https://docs.arducam.com/Optics-and-Lenses/Lens-Products-from-Arducam/
[c6]: https://www.kubii.com/en/cameras-sensors/3878-camera-module-v3-raspberry-pi-3272496313699.html

**Pick**: HQ + 6 mm lens ≈ €80 (reconciliation with the BOM agent's
original 16 mm suggestion: § B is authoritative because a wider FOV is
required to see the hovering volume, not just the impact zone).

### Pan/tilt mechanics

**v1 cheap (servo, nozzle-only gimbal — camera on static mast):**

| Component                                              | Price €      |
| ------------------------------------------------------ | ------------ |
| 2× MG996R metal-gear servo ([Pi Hut][c7])              | 2× 8 = 16    |
| PCA9685 16-ch I²C PWM driver ([Gotronic ADA1411][c8])  | 12-18        |
| 3D-printed bracket + M3 hardware                       | ~5           |
| **Subtotal v1**                                        | **~35**      |

**v2 precise (BLDC gimbal):**

| Component                                              | Price €      |
| ------------------------------------------------------ | ------------ |
| 2× iPower GM3506 + AS5048A encoder ([iFlight EU][c9])  | 2× ~45 = 90  |
| SimpleBGC 32-bit controller (Tiny / Extended)          | 80-220       |
| Frame + slip-ring / cable management                   | ~30          |
| **Subtotal v2**                                        | **~200-340** |

[c7]: https://thepihut.com/products/servo-motor-mg996r-high-torque-metal-gear
[c8]: https://www.gotronic.fr/art-shield-i2c-pour-16-servos-ada1411-20672.htm
[c9]: https://iflight-rc.eu/en/products/ipower-gm3506-encoder-combo-set

**Note**: the camera stays on a **static mast**; the gimbal points the
**nozzle only**, so servo jitter does not blur frames.

### Fluid path (physically separated from electronics)

| Component                                                                                                                  | Spec                            | Price €    |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------- |
| 12V diaphragm pump (Shurflo / SEAFLO / [VEVOR][c10] class)                                                                  | 4.5 L/min, ~7 bar, food-grade   | 35-60      |
| 12V solenoid valve, 1/4" NC, brass, food-grade                                                                             | DC 12V, 0-8 bar                 | 10-15      |
| Pressure regulator → 3 bar                                                                                                 | inline diaphragm reg            | 12-20      |
| Pencil-jet nozzle (1.0-1.5 mm)                                                                                             | brass                           | 5          |
| Reservoir 5 L food-grade jerrycan + 6 mm PE tubing 3 m                                                                     |                                 | 15         |
| Fuse + relay (MOSFET 30 A IRLZ44N or auto relay)                                                                           | for pump                        | 5          |
| **Subtotal**                                                                                                               |                                 | **~85-120** |

[c10]: https://eur.vevor.com/water-pumps-accessories-c_12381/vevor-12v-diaphragm-pump-1-8gpm-6-81-l-min-3-chamber-water-pump-pressure-switch-p_010923467134

### Audio sensor

| Component                                  | Spec                                 | Price €      |
| ------------------------------------------ | ------------------------------------ | ------------ |
| [Adafruit SPH0645 I²S MEMS][c11]          | 50 Hz-15 kHz, 24-bit, fits Pi I²S    | ~7-10        |
| INMP441 I²S breakout (cheaper alternative) | 32-44 kHz easy                       | ~3-5         |

[c11]: https://www.adafruit.com/product/3421

**Pick**: SPH0645 or INMP441 (~5-10 €). Both cover the inferred
~100-125 Hz hornet wingbeat fundamental + 3 harmonics up to 1.2 kHz.

### Distance sensor — three options

| Option                                                    | Spec                       | Price €  | Verdict                                                              |
| --------------------------------------------------------- | -------------------------- | -------- | -------------------------------------------------------------------- |
| **VL53L5CX 8×8 ToF** ([Pimoroni][c12])                    | 0-4 m, 8×8 zones, I²C      | ~22      | **Pick this** — perfect range, cheap, low power.                     |
| Stereo Pi cameras                                         | 2× HQ + 2× CSI + calibration | ~100   | Heavy, complicates capture pipeline. Skip.                            |
| RealSense D435i                                           | 0.2-10 m, 1280×720, 3 W    | ~450     | Overkill, too much power. Defer to v2.                                |
| Geometric estimate (known focal + assumed wingspan 25 mm) | 0 € software-only          | 0        | Fallback during ML phase.                                              |

[c12]: https://shop.pimoroni.com/en-us/products/vl53l5cx-time-of-flight-tof-sensor-breakout

### Solar autonomy — worked example

**Assumptions**: Pi 5 + Hailo-8L stack, **6 h/day active detection**
(matches the biological active window from § A), 18 h/day idle. Pump
events ~200/day × 2 s × 36 W = 4.2 Wh.

**Daily Wh**:

- Active: 12 W × 6 h = **72 Wh**
- Idle: 3 W × 18 h = **54 Wh**
- Pump + valve events: ~5 Wh
- Servos (PWM hold): 1 W × 12 h ≈ **12 Wh**
- Comms (4G modem, optional): 1.5 W × 24 h ≈ 36 Wh
- **Total: ~180 Wh/day** (without 4G), **~215 Wh** with 4G

**Battery** (12 V LiFePO4, DoD 80 %): 180 Wh / 12 V / 0.8 = **18.75 Ah
day-1**. For 3-day autonomy (cloudy run): 56 Ah. **Pick 12 V / 100 Ah
LiFePO4** → 5 days reserve, ~€230 ([WattCycle EU][c13]).

**Panel** (South France, season avg 4.5 PSH, derating 0.75):
W = 180 / (4.5 × 0.75) = **53 W min** → **100 W mono** (~€70-90) gives
2× headroom for shoulder-season.

**Controller**: **MPPT mandatory** for LiFePO4 + harvest gain (~20-30 %).
[Victron SmartSolar MPPT 75/15][c14] (~€90 EU) or [VEVOR 20A MPPT][c15]
(~€40). PWM rejected — wastes ~25 % of panel output.

[c13]: https://eu.wattcycle.com/products/wattcycle-12v-100ah-group-24-lifepo4-battery
[c14]: https://www.victronenergy.com/solar-charge-controllers/smartsolar-mppt-75-10-75-15-100-15-100-20
[c15]: https://eur.vevor.com/mppt-solar-charge-controller-c_10732

### Outdoor enclosure / weatherproofing

| Component                                                | Price €  |
| -------------------------------------------------------- | -------- |
| IP65 ABS enclosure 300×200×150 (Hammond / Hylec / Fibox) | 25-40    |
| Cable glands PG7/PG9 ×4                                  | 8        |
| Camera dome window (acrylic + EPDM gasket)               | 15       |
| Marine sealant + ties + mounting bracket                 | 15       |
| **Subtotal**                                             | **~65-80** |

### Total BOM

| Configuration                                                                                                                                                | Subtotal €      | Dominant cost              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- | -------------------------- |
| **v1 minimal** — Pi 5 + AI HAT+, HQ cam + 6 mm, MG996R + PCA9685, VL53L5CX, SPH0645, pump+valve, 100 W panel + 100 Ah LiFePO4 + VEVOR MPPT, IP65 box      | **~720**        | Solar/battery (~50 %)      |
| v1 **without** solar (mains / USB-C PD)                                                                                                                       | **~360**        | Compute (~45 %)            |
| **v2 production** — same compute, GM3506 + SimpleBGC, RealSense, Victron MPPT 75/15, 200 Ah battery                                                          | **~1500-1800**  | Gimbal + RealSense + batt. |

**The < €500 target** is reachable only by dropping solar (run from a
wall socket during prototype) or running on a 30 Ah battery (~€80) +
50 W panel (~€50) — fine for proof-of-concept, not for unattended
deployment.

### Lead-time risks (May 2026)

- **Hailo-8L AI HAT+**: original AI Kit EOL; HAT+ generally in stock,
  check Pimoroni / Kubii.
- **Jetson Orin Nano Super**: intermittent EU stock 2025; Antratek +
  Arrow most reliable, 2-4 weeks.
- **Coral USB**: allocation-constrained since 2023.
- **GM3506 + AS5048A**: iFlight EU (Hungary) ~1 week; Alibaba 3-4 weeks.
- **SimpleBGC 32-bit Extended**: small-batch, 2-3 weeks.
- **Victron MPPT**: 2-5 days.
- **LiFePO4 100 Ah**: WattCycle / Eco-Worthy, 3-7 days.
- **Off-the-shelf** (Pi 5, HQ cam, ToF, mic, servos, enclosure): 2-5 days.

### Phased procurement plan

| Phase                | When        | What                                                                                    | Budget |
| -------------------- | ----------- | --------------------------------------------------------------------------------------- | ------ |
| **1 — bench**        | Week 1      | Pi 5 + AI HAT+, HQ Cam + 6 mm, SPH0645, VL53L5CX, MG996R ×2 + PCA9685                  | ~€250  |
| **2 — wet side**     | Week 3      | Pump + solenoid + regulator + nozzle + tubing + jerrycan + MOSFET driver               | ~€120  |
| **3 — outdoor / autonomous** | Week 6+ | IP65 enclosure + 100 W panel + 100 Ah LiFePO4 + MPPT                                    | ~€430  |

## Cross-section synthesis

### Strike-rate baseline (Darrouzet)

The published baseline is **2.4 % overall predation success at hive
entrance, density-dependent peak around ~8 simultaneous hornets**
([Robinet/Darrouzet 2023][dp6]). Aristech's primary success metric is
**"miss reduction"**: the percentage drop in successful strikes when
the deterrent is active vs the same colony without it. The harp
benchmark is `−89 %` predation pressure at apiary scale ([Rojas-Nossa
2022][drn22]) — that's the floor aristech must approach to be
defensible.

[drn22]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9825959/

### Selectivity floor

Darrouzet's harp paper publishes **> 90 % _V. velutina_ in catch, <
2 % non-target** ([Thiéry & Darrouzet 2023][dp5]). Aristech's vision
classifier must meet or exceed that ratio **without making contact
with any insect**. The legal floor (Art. L411-1 + L415-3 Code env.,
3 years prison + €150 000 for harming a protected pollinator —
see [state-of-the-art.md § Legal framework](state-of-the-art.md)) and
the harp's published selectivity converge on the same architectural
requirement: classifier defaults to abstain; geometric no-spray zone
around the entrance independent of the classifier.

### FOV reconciliation between § B and the BOM survey

The BOM survey originally proposed a 16 mm telephoto on the Pi HQ for
hornet-pixel sharpness (~134 px at 1 m). The geometry survey
recommends a **6 mm wide lens** (~47 px) because the hovering volume
must be observed, not just the impact zone. **§ B wins for v1**: a
hornet about to strike must be seen during the multi-second hover,
not only during the sub-second strike itself. The 47 px target sits
comfortably above the YOLO recall floor (30 px). § C's BOM is updated
to reflect this.

### Power budget vs biological active window

Daily Wh = **180 Wh** with the biologically realistic **6 h/day active**
detection window from § A. A 100 W panel + 100 Ah LiFePO4 in South
France gives 5-day cloudy-weather autonomy. Cutting the active window
to 4 h (afternoon-only deployment) reduces daily Wh to ~165 Wh — no
significant battery saving but a ~10 % gain in solar headroom for
shoulder seasons.

### Aristech's first-publication opportunities

The biology survey explicitly flagged four open measurements that no
peer-reviewed publication has produced:

1. Hover distance / height in front of the planche d'envol (European
   _V. velutina_).
2. Strike rate per minute / per hornet, plus per-attack success rate
   at French hives.
3. Hover jitter (amplitude of stationary-flight noise), turn radius,
   reaction latency to disturbance.
4. Wingbeat fundamental frequency of _V. velutina_ specifically
   (everything published is inferred from congeners).

These are direct outputs of aristech's own annotated video + audio
corpus and would be publishable contributions — strong motivation to
build a serious annotation pipeline from the prototype phase
(LabelStudio / CVAT / Roboflow Annotate are the candidates; choice
deferred to a dedicated PR).

## Open decisions informed by this document

- **Camera + lens choice**: Pi HQ + 6 mm M12 wide for v1 (§ B wins
  over § C's 16 mm telephoto).
- **Pan/tilt tier**: v1 servo + PCA9685 on a nozzle-only gimbal;
  static camera mast. v2 BLDC + AS5048A only if measured jitter
  dominates the error budget.
- **Distance sensing**: VL53L5CX ToF for v1; stereo / RealSense
  deferred to v2 if precision needs it.
- **Multi-hive topology**: defer to a benchmark — full Pi per hive vs
  ESP32 + Grove sensor heads. Test on a single hive first; topology
  decision triggered when the second hive joins the deployment.
- **Solar deployment**: optional for v1 (use mains / USB-C PD during
  prototype); mandatory for v2 unattended field deployment.

## What this document does NOT settle

- The two remaining open product questions from `neutralize-target-deferred`
  (multi-modal fusion confirm policy, fail-safe default) still wait for
  prototype evidence — the prototype must produce false-positive /
  false-negative numbers before they can be locked.
- Field deployment partnerships (which apiarist, which apiary, which
  season) — separate PR.
- Annotation pipeline + dataset license strategy — separate PR.
- Acceptance criteria for the "miss reduction" validation campaign —
  separate PR, drafted with one of ITSAP / ADA / GDS as scientific
  partner.

## Honest caveats

- Several agent runs reported WebFetch failures on specific pages
  (Kaggle reCAPTCHA, Légifrance, some IRBI lab pages). All numbers in
  this document are traceable to the URLs listed but a small number
  rely on converging secondary sources; re-verify the primary papers
  before they are quoted in a publication.
- All EUR prices in § C are anchored to supplier pages visible at the
  time of survey (May 2026). Re-quote at procurement time.
- The 47 px hornet pixel target in § B assumes a 30 mm hornet body and
  a static Pi HQ at 1 m of distance. Real-world measurements may
  diverge if the actual hovering distance turns out to be 50 cm or
  150 cm rather than 100 cm — a measurement aristech itself will
  produce.
