# SmartAsset

SmartAsset is a startup-track hackathon prototype for **autonomous smart asset intelligence**.
It combines simulated AI + computer vision scoring to:

- classify an asset's visible condition,
- estimate short-term failure probability,
- prioritize operational risk,
- and suggest maintenance actions.

## Origin Pitch

> Hi Kevin! I saw you are looking for a team for Hack USU.  
> What type of project or what competition track do you plan to enter?  
> I think I'll do the "startup" track. I have an idea for an autonomous smart asset intelligence system that uses AI + computer vision to classify and keep track of assets and their associated risks (due to factors like wear or corrosion).  
> Let me know if you're interested!

## Run locally

From repo root:

```bash
python3 -m http.server 4173
```

Then open:

- `http://localhost:4173/smartAsset/`

## Project files

- `index.html` – single-page prototype UI.
- `styles.css` – layout + risk visualization styles.
- `app.js` – simulation logic for CV-inspired condition and risk scoring.
