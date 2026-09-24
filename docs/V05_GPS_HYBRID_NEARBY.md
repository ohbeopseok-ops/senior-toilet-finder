# V0.5 GPS Hybrid Nearby Engine

## Goal

Show the nearest usable toilet candidates from the user's actual GPS location without waiting for JUSO geocoding of every public-data row.

## Runtime flow

1. iPhone GPS obtains current latitude/longitude.
2. Frontend calls a Cloudflare Worker `/nearby` endpoint.
3. Worker calls Kakao Local keyword search with:
   - queries: `공중화장실`, `화장실`, `개방화장실`
   - center: current GPS
   - radius: 3 km
   - sort: distance
4. Worker returns candidate name/address/coordinate/distance.
5. Frontend merges Kakao candidates with official public-data rows that already have coordinates.
6. Duplicates are removed using name + proximity rules.
7. Final order is nearest-first, with known-closed toilets pushed to the bottom.
8. Accessibility, emergency bell, stairs, and opening status remain supporting information rather than hard gates.

## Security

The Kakao REST API key must never be placed in browser JavaScript or GitHub Pages.

Cloudflare Worker secret:
- `KAKAO_REST_API_KEY`

GitHub Actions secrets for Worker deployment:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `KAKAO_REST_API_KEY`

## Frontend runtime config

After the Worker is deployed, set `nearby-config.js`:

```js
window.SENIOR_TOILET_CONFIG = {
  nearbyApiBase: "https://senior-toilet-nearby.<workers-subdomain>.workers.dev"
};
```

Do not include a trailing slash.

## Hybrid data priority

- Distance is computed again in the browser from the user's GPS and each candidate coordinate.
- Official public-data rows are preferred when a Kakao result and official row are considered duplicates.
- Kakao results can supply immediate nearby coordinates before JUSO enrichment completes.
- Public data remains the richer source for opening hours, accessibility equipment, emergency bells, and later safety metadata.

## Safety behavior

- No fake `0,0` coordinates.
- No default Anyang coordinate before GPS is available.
- No stairs hard gate.
- No 500 m hard gate.
- If the nearby API is unavailable and official rows have no coordinates, the app shows a waiting/error state instead of a false distant recommendation.
