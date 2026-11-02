# Bench Pi 5 hardware order list

Priced bill of materials for the bench capture rig, which is also the staging device (ADR-0025),
with every price and stock status checked live on 2026-11-02; nothing is ordered here.

- Date: 2026-11-02 (issue #132, brick C1)
- Decision owner: the project owner (storage option C validated 2026-11-02)
- Related: [ADR-0017](../decisions/ADR-0017-capture-rig-hardware.md),
  [ADR-0016](../decisions/ADR-0016-acoustic-axis-collect-then-gate.md),
  [ADR-0025](../decisions/ADR-0025-branching-and-promotion-model.md),
  [ICS-43434 lifecycle](2026-11-02-ics-43434-lifecycle.md),
  [spec capture-rig](../architecture/specs/capture-rig.md)

## Storage choice

Memory prices make the ADR-0017 storage line (1 TB 2230 SSD, estimated 70 EUR) cost 270 EUR.
Totals and sensitivity are computed by
[`mcda/research_2026_11_02_bench_order_storage.py`](../decisions/mcda/research_2026_11_02_bench_order_storage.py).
Criteria: cost 25 · capacity 20 · fits the Ø110 head 20 · ADR-0017 conformity 10 · available now
15 · endurance 10.

| Option | Cost | Capacity | Head | ADR | Now | Endurance | Total |
|---|---|---|---|---|---|---|---|
| A. M.2 HAT+ + Kingston NV3 2230 1 TB (284 EUR) | 1 | 5 | 5 | 5 | 4 | 4 | 375 |
| B. Pimoroni NVMe Base + Kingston NV3 2280 1 TB (208 EUR) | 3 | 5 | 3 — longer 2280 board under the Pi | 3 — different carrier | 5 | 4 | 380 |
| **C. M.2 HAT+ + SK hynix 2230 512 GB (160 EUR)** | 4 | 3 — ~5 weeks at 13 GB/day | 5 | 4 | 4 | 3 | **390** |
| D. Official SSD kit 512 GB with M.2 HAT+ (165 EUR) | 4 | 3 | 5 | 4 | 1 — pre-order | 3 | 345 |

Sensitivity: cost 40 → C 390, B and D 360; head 35 → C 410, A 400; **capacity 35 → A 415 > B 410
> C 370 (flips)**. C wins while the bench offloads its disk regularly; A wins only if the bench
must match the field autonomy. The ADR-0017 decision (NVMe on M.2 HAT+) stands; only the capacity
of the bench unit changes.

## Bill of materials

Prices in EUR incl. VAT, shipping excluded, read on the supplier page on 2026-11-02.

| # | Part | Exact reference | Supplier | Unit € | Qty | Total € | Availability | Source |
|---|---|---|---|---|---|---|---|---|
| 1 | Raspberry Pi 5 8 GB | SC1112 | Kubii | 213.00 | 1 | 213.00 | Available | [kubii.com](https://www.kubii.com/fr/cartes-nano-ordinateurs/4106-1832-raspberry-pi-5-3272496315938.html) |
| 2 | Official 27 W USB-C power supply, FR plug | SC1152 | Kubii | 12.90 | 1 | 12.90 | Available | [kubii.com](https://www.kubii.com/fr/alimentations/4107-1818-alimentation-raspberry-pi-27w-usb-c-3272496315761.html) |
| 3 | Official Pi 5 Active Cooler | RASP ACTIVE COOL (360116) | Reichelt | 5.69 | 1 | 5.69 | Listed | [reichelt.com](https://www.reichelt.com/fr/fr/shop/produit/raspberry_pi_-_ventilateur_pour_raspberry_pi_5-360116) |
| 4 | Official RTC battery for Pi 5 | RPI-RTCBAT | BerryBase | 5.70 | 1 | — | **Out of stock** (also Kubii); not in total | [berrybase.de](https://www.berrybase.de/en/rtc-battery-rechargeable-battery-for-raspberry-pi-5) |
| 5 | Camera Module 3, standard 75° | SC0872 | Kubii | 30.90 | 1 | 30.90 | Available | [kubii.com](https://www.kubii.com/fr/cameras-capteurs/3878-1689-module-camera-v3-raspberry-pi-3272496313699.html) |
| 6 | Camera cable standard–mini 200 mm | RPI-CC-SM-20 | BerryBase | 1.20 | 1 | 1.20 | 100+, 1–3 days | [berrybase.de](https://www.berrybase.de/en/raspberry-pi-camera-cable-standard-mini-200mm) |
| 7 | Adafruit ICS-43434 I²S breakout (2 used + 2 spares) | Adafruit 6049 | DigiKey FR | 9.53 | 4 | 38.12 | 999 in stock | [digikey.fr](https://www.digikey.fr/fr/products/detail/adafruit-industries-llc/6049/25589349) |
| 8 | Shielded control cable 6 × 0.14 mm², 10 m ring | LIYCY 06-10 | Reichelt | 11.32 | 1 | 11.32 | Listed | [reichelt.com](https://www.reichelt.com/fr/fr/shop/recherche/liycy%206x0,14) |
| 9 | Connector kit JST SM / Dupont 2.54 mm, 200 pcs | 157011 | BerryBase | 3.90 | 1 | 3.90 | 100+, 1–3 days | [berrybase.de](https://www.berrybase.de/en/berrybase-200-piece-jumper-wire-connector-kit-jst-sm-dupont-2.54mm-2-5-pin-male-female) |
| 10 | Fur windscreens, pack of 3 (fit to be checked on the breakout) | Rode WS9 | Thomann | 19.90 | 1 | 19.90 | Available now | [thomann.fr](https://www.thomann.fr/rode_ws9.htm) |
| 11 | Official M.2 HAT+ (2230/2242) | SC1166 | Kubii | 14.10 | 1 | 14.10 | Available | [kubii.com](https://www.kubii.com/fr/hat-dac-modules/4114-m2-hat-pour-raspberry-pi-5-5056561803463.html) |
| 12 | NVMe SSD 512 GB, M.2 2230 (option C) | SK hynix 2230 NVMe 512 GB | Kubii | 145.95 | 1 | 145.95 | Add to cart offered | [kubii.com](https://www.kubii.com/fr/support-de-stockage/5292-ssd-sk-hynix-m2-2230-nvme-pcie-512-gb-0884116762140.html) |
| 13 | microSD High Endurance 64 GB (OS) | SDSQQNR-064G | Kubii | 35.95 | 1 | 35.95 | Available | [kubii.com](https://www.kubii.com/fr/support-de-stockage/5022-2586-carte-microsd-sandisk-high-endurance-3272496326392.html) |
| 14 | PVC drain pipe Ø100, 2 m (cut to ~0.5 m) | EAN 3396040121018 | Bricodépôt | 7.39 | 1 | 7.39 | Per store | [bricodepot.fr](https://www.bricodepot.fr/p/3396040121018/tube-pvc-compact-pour-l-evacuation-des-eaux-usees-o-100-mm-l-2-m) |
| 15 | PVC end cap Ø100 | EAN 3396047450104 | Bricodépôt | 3.89 | 1 | 3.89 | Per store | [bricodepot.fr](https://www.bricodepot.fr/p/3396047450104/bouchon-pvc-pour-l-evacuation-gravitaire-des-eaux-usees-o-100-mm) |
| 16 | Galvanised round post spike Ø10 cm, 90 cm | 86464708 | Leroy Merlin | 41.18 | 1 | 41.18 | Home delivery | [leroymerlin.fr](https://www.leroymerlin.fr/produits/support-de-poteau-en-bois-10-cm-90-cm-piquet-rond-en-acier-galvanise-ancrages-a-enfoncer-dans-les-bases-de-poteaux-en-bois-86464708.html) |
| 17 | PMMA sheet 3 mm, A4 (camera window) | 83572074 | Leroy Merlin | 9.80 | 1 | 9.80 | Home delivery | [leroymerlin.fr](https://www.leroymerlin.fr/produits/plaque-plexiglas-pmma-transparent-ep-3-mm-l-29-7-x-21-cm-a4-83572074.html) |
| 18 | Cable gland M12 nylon IP68, Ø3–6.5 mm, bag of 10 | RS PRO 214-1063 | RS France | 7.33 | 1 | 7.33 | 221 in stock | [rs-online.com](https://fr.rs-online.com/web/p/presse-etoupes/2141063) |
| 19 | Stainless insect mesh, small piece | — | to choose | — | 1 | — | **Not verified** (ManoMano bot check); buy in store | — |
| 20 | Nylon spacer assortment M2.5, 420 pcs | DBSET-25-NW | BerryBase | 13.90 | 1 | 13.90 | 99, 1–3 days | [berrybase.de](https://www.berrybase.de/en/420-piece-nylon-spacer-assortment-in-plastic-box-m2.5-white) |
| 21 | USB-C power meter (AC9) | FNIRSI FNB58 | BerryBase | 49.90 | 1 | 49.90 | 9, 1–3 days | [berrybase.de](https://www.berrybase.de/en/fnirsi-fnb58-usb-tester-4-28-v-0-7a-140w-schwarz) |
| | **Total (verified lines, shipping excluded)** | | | | | **666.32** | | |

ADR-0017 estimated unit 1 at ~369 EUR (with the #84 spares). The gap comes mostly from the Pi 5
8 GB (213 vs 95) and the SSD (146 vs 70), both driven by 2026 memory prices.

## Order notes

- Group by supplier to limit shipping: Kubii (lines 1, 2, 5, 11, 12, 13: 452.80 EUR, free
  delivery in France from 75 EUR), BerryBase (6, 9, 20, 21), Reichelt (3, 8, shipping from
  7.90 EUR), DigiKey (7), Thomann (10), RS (18), DIY stores (14–17, 19).
- Line 4: order when back in stock; the rig runs without it (time from NTP on the bench).
- Line 7: buy before the breakout stock runs out (#84).
- Line 12: if the bench later needs field autonomy, swap for a 1 TB 2230 (Kingston NV3, LDLC,
  269.95 EUR, [ldlc.com](https://www.ldlc.com/fiche/PB00695269.html)).
- Mouser pages refused automated access; DigiKey was used for the microphones instead.
- Excluded, as in ADR-0017: outdoor mains extension (owner's), solar kit (after AC9), unit 2.
