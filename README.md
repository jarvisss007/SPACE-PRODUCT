# Space Product

Interactive space-science labs that run in any browser, built on real mission data and checked against what really happened. Every page shows its sources and a "checks" table comparing the model with published figures.

The working name in the pages is still **Starship Atlas**. "Starship" is a SpaceX trademark, so the product needs its own name before launch.

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

This writes `site/`. Any static host can serve that folder as is, for example Cloudflare Pages, Netlify or GitHub Pages.

## Updating the satellite data

`satellite-watch.html` carries a snapshot of public orbit data from CelesTrak (celestrak.org), dated on the page. Low orbits drift, so refresh the snapshot every week or two for accurate pass times.

## Third-party pieces and licences

- [satellite.js](https://github.com/shashwatak/satellite-js) 5.0.0 (MIT), loaded from the jsDelivr CDN.
- Coastlines from Natural Earth via world-atlas 2.0.2 (public domain), embedded.
- NASA images in the Spacecraft Archive are public domain; no agency logos are used.
- Mission numbers come from cited public sources listed in each page's footer. The page text is original.

Not affiliated with ISRO, NASA, ESA, SpaceX or CelesTrak.
