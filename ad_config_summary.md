# Ad Config Summary — OTT + USA

## Base Config

| Parameter | Value |
|---|---|
| Platforms | OTT (ps4, ps5, xboxone, amazon, androidtv, chromecast, roku, samsung, vizio, lgtv, tivo, tvos, etc.) |
| Countries | US |
| initial-ad-slot | 900s (15 min) |
| min-time-between-breaks | 720s (12 min) — global default |
| final-ad-slot | 0s |
| max-preroll-count | 5 |
| max-preroll-break | 77s |
| max-midroll-count | 5 |
| max-midroll-break | 152s |
| alternate-max-midroll-count | 6 |
| alternate-max-midroll-break | 122s |
| max-creative-duration | 300s |
| budgeted-actuator-threshold | 0 |

The base `min-time-between-breaks = 720s` is the global spacing default. All content-type/fill-rate/ad-load deltas reduce from this baseline. Note: this config controls application-level pod placement only — a separate system-level hard minimum may exist outside this config.

---

## Movies — Effective initial-ad-slot & min-time-between-breaks

| Fill Rate | ATUplift Label | Ad Load | initial-ad-slot | min-time-between-breaks |
|---|---|---|---|---|
| any | — / mid / low / high | 6-8, 8-10, 10+ | 900s | 720s |
| any | high | 4-6 | 810s | 648s |
| any | high | 0-2, 2-4 | 720s | 576s |
| [60,80) | — / mid / low / high | 6-8, 8-10, 10+ | 810s | 660s |
| [60,80) | high | 4-6 | 729s | 594s |
| [60,80) | high | 0-2, 2-4 | 648s | 528s |
| [40,60) | — / mid / low / high | 6-8, 8-10, 10+ | 780s | 630s |
| [40,60) | high | 4-6 | 702s | 567s |
| [40,60) | high | 0-2, 2-4 | 624s | 504s |
| [20,40) | — / mid / low / high | 6-8, 8-10, 10+ | 720s | 540s |
| [20,40) | high | 4-6 | 648s | 486s |
| [20,40) | high | 0-2, 2-4 | 576s | 432s |
| [0,20) | — / mid / low / high | 6-8, 8-10, 10+ | 540s | 420s |
| [0,20) | high | 4-6 | 486s | 378s |
| [0,20) | high | 0-2, 2-4 | 432s | 360s |

---

## Episodes — Effective initial-ad-slot & min-time-between-breaks

| Fill Rate | ATUplift Label | Ad Load | initial-ad-slot | min-time-between-breaks |
|---|---|---|---|---|
| any | — / mid / low / high | 6-8, 8-10, 10+ | 420s | 600s |
| any | high | 4-6 | 378s | 540s |
| any | high | 0-2, 2-4 | 360s | 480s |
| [60,80) | — / mid / low / high | 6-8, 8-10, 10+ | 420s | 540s |
| [60,80) | high | 4-6 | 378s | 486s |
| [60,80) | high | 0-2, 2-4 | 360s | 432s |
| [40,60) | — / mid / low / high | 6-8, 8-10, 10+ | 390s | 510s |
| [40,60) | high | 4-6 | 360s | 459s |
| [40,60) | high | 0-2, 2-4 | 360s | 408s |
| [20,40) | — / mid / low / high | 6-8, 8-10, 10+ | 390s | 480s |
| [20,40) | high | 4-6 | 360s | 432s |
| [20,40) | high | 0-2, 2-4 | 360s | 384s |
| [0,20) | all labels | all | 360s | 360s |

---

## Key Observations

- **Global spacing default:** `min-time-between-breaks = 720s` applies to all OTT/US traffic before any delta. This is the effective ceiling.
- **Episodes vs Movies:** Episodes have a much lower `initial-ad-slot` than movies at every fill rate (~420s vs 900s at baseline) — first ad break comes much earlier in episodes.
- **Floor:** Both content types converge to a `360s` floor for `initial-ad-slot` and `min-time-between-breaks` at the lowest fill rate / lowest ad load combinations.
- **Device fill rate:** Lower fill rate → more aggressive reductions to both parameters (more frequent and earlier breaks).
- **ATUplift label:** Users labeled `high` tolerance with lower ad load (0–4 breaks) see the most aggressive reductions; `mid`/`low` tolerance users are treated the same as unlabeled.
