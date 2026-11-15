# Whiteboard site

The landing page for [Whiteboard](https://github.com/CITROMOSEPER/Whiteboard), the free whiteboard that runs in your browser. The app itself lives at **https://citromoseper.github.io/Whiteboard/**; this repository is only the page that introduces it. It is kept separate, so an installed copy of the app always opens on the whiteboard, never on this page.

A plain static site: no trackers, nothing loaded from other servers. Every page exists in each of the app's 14 languages as real HTML, so search engines can read all of them.

- `content/`: the text, in 14 languages (`strings.json`, `strings-pages.json`) and the list of tutorials (`site.json`). Menu names in the tutorials match the app's own wording.
- `tools/build.py`: writes the pages from `content/`. Home, Features, Tutorials and Support, English at the top level and the other languages under `hu/`, `de/`, and so on, plus `sitemap.xml`. Run `python tools/build.py` after changing any text, and commit the result.
- `css/site.css`: styles, with a light and a dark colour set.
- `js/site.js`:
  - Language: a language picked in the header is remembered; on a first visit, the English page goes to the browser's language.
  - Theme: follows the system until the switch in the header is used.
  - Tutorials: tabs and steps; `tutorials/#tutPdf` opens a topic directly.
- `img/shots/`: the tutorial screenshots, in light and dark versions.
- `fonts/`: Bricolage Grotesque, Inter and Caveat, self-hosted (SIL Open Font License, see `fonts/OFL.txt`).

## Remaking the tutorial screenshots

The screenshots are taken from the real app. A script opens it in headless Chrome, builds each scene with the app's own objects and windows, and draws the red circles and arrows. Run it again after the app changes:

```
pip install playwright pillow
python tools/shots.py                      # uses the published app
python tools/shots.py http://localhost:5173/ start-tools pdf-menu   # a local copy, only some scenes
```

The scenes are defined in `tools/shots.py`; the drawing helpers are in `tools/shots.js`.

## Trying it locally

```
python -m http.server 5174
```

Then open http://localhost:5174/.

## Licence

MIT, see `LICENSE`. The fonts keep their own licence (`fonts/OFL.txt`).
