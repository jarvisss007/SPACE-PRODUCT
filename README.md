# Golapada

Interactive space-science labs that run in any browser, built on real mission data and checked against what really happened. Every page shows its sources and a "checks" table comparing the model with published figures.

**Golapada** (गोलपाद) means “the chapter on the sphere”: the fourth part of Aryabhata’s *Aryabhatiya* (499 CE), where he explained the turning Earth, the sky and eclipses. Domains to secure: golapada.com and golapada.in (both unregistered when checked on 18 November 2026). The earlier working name Kaksha Labs was dropped because several Indian edtech companies already use “Kaksha”. Run a trademark search on ipindia.gov.in before launch.

## What is here

Each `*.html` file at the top level is one self-contained lab: one file with no build step, opened directly in a browser. `site/` is the same set joined into one website with a shared menu. `build_site.py` regenerates it.

| Group | Labs |
|---|---|
| Live | Satellite Watch (`satellite-watch.html`) |
| Rockets and Earth orbit | Starship Catch, Rocket Lab, NavIC Lab, Space Debris Lab, Re-entry Lab, Planetary Defense Lab |
| Moon, Mars and planets | Chandrayaan-3 Moon Lab, Mangalyaan Mars Lab, Mars Landing Lab, Mars Campaign, Solar System Lab, Gravity Assist Lab, Ion Engine Lab, Touch the Sun, Lagrange Point Lab |
| Deep space | Voyager Now, Telescope Lab, Milky Way Atlas, Exoplanet Explorer, Black Hole and Wormhole Lab, Spacecraft Archive |
| Ancient astronomy | Aryabhata Lab, Nalanda, Starship Through Time, Clues in Old Books |

## Build the website

```bash
py build_site.py
```

This writes two folders:

- `docs/` is **the public website**: complete pages with an icon and a link-preview description. GitHub Pages serves it.
- `site/` is the same pages in the form claude.ai artifacts expect.

## Hosting (GitHub Pages)

1. On GitHub, open the repository's **Settings → Pages**.
2. Under "Build and deployment", set **Source** to *Deploy from a branch*, **Branch** to `main` and the folder to `/docs`, then **Save**.
3. After a minute the site is live at `https://jarvisss007.github.io/SPACE-PRODUCT/`.

After any change, run `py build_site.py`, then commit and push. Pages updates by itself.

**Own domain (golapada.com):** in the same Pages settings, enter the domain under "Custom domain", which adds a `CNAME` file. Then, at the domain registrar, add the DNS records GitHub shows: four `A` records for the bare domain, and a `CNAME` for `www` pointing to `jarvisss007.github.io`. Tick "Enforce HTTPS" once it appears.

## Updating the satellite data

`satellite-watch.html` carries a snapshot of public orbit data from CelesTrak (celestrak.org), dated on the page. It refreshes itself every day. The GitHub Action in `.github/workflows/refresh-satellites.yml` runs `tools/refresh_tle.py` at 02:17 UTC, rebuilds the site and publishes any change. To refresh now, open **Actions → Refresh satellite data → Run workflow**.

## Third-party pieces and licences

- [satellite.js](https://github.com/shashwatak/satellite-js) 5.0.0 (MIT), loaded from the jsDelivr CDN.
- Coastlines from Natural Earth via world-atlas 2.0.2 (public domain), embedded.
- NASA images in the Spacecraft Archive are public domain; no agency logos are used.
- Mission numbers come from cited public sources listed in each page's footer. The page text is original.

Not affiliated with ISRO, NASA, ESA, SpaceX or CelesTrak.
