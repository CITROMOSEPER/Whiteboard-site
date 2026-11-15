# Whiteboard site

The landing page for [Whiteboard](https://github.com/CITROMOSEPER/Whiteboard), the free whiteboard that runs in your browser. The app itself lives at **https://citromoseper.github.io/Whiteboard/**; this repository is only the page that introduces it. It is kept separate, so an installed copy of the app always opens on the whiteboard, never on this page.

A plain static site: no build step, no trackers, nothing loaded from other servers.

- `index.html`: the page. Its English text is also the fallback when scripts are off.
- `css/site.css`: styles, with a light and a dark colour set.
- `js/i18n.js`: the text in the app's 14 languages. Menu names in the tutorials match the app's own wording.
- `js/site.js`:
  - Language: chosen in the header, otherwise detected from the browser.
  - Theme: follows the system until the switch in the header is used.
  - Tutorials: tabs and steps.
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
