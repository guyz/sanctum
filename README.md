# Sanctum of Ash

A kid-friendly, Diablo-style action RPG — the whole game is one self-contained HTML file
(`sanctum-of-ash.html`, three.js with art + audio inlined). The same file runs on desktop,
as a mobile web app, and as a native iOS app.

🎮 **Play:** https://guyzyskind.com/sanctum/sanctum-of-ash.html

## Three ways to play

**1. Desktop (browser)** — open the link above. Mouse + keyboard (WASD · 1–4 · SPACE).

**2. Mobile web / PWA (iPhone · iPad)** — open the link in Safari → **Share → Add to Home
Screen**. Launches fullscreen with touch controls (virtual joystick + tap buttons), works
offline, and **updates itself** whenever a new build ships. Best option for phones.

**3. Native iOS app (Xcode)** — a self-contained app built from the same file:
```bash
cd native
./setup-ios.sh        # bundles the current game into the iOS project
npx cap open ios      # opens it in Xcode
```
In Xcode: under **Signing & Capabilities** pick your Apple ID team, plug in your iPhone,
press **▶ Run**, then trust the app on the phone under *Settings → General → VPN & Device
Management*. A **free** Apple ID expires the app after **7 days** — just re-run the two
steps above to renew (a paid Apple Developer account removes the limit).

## Repo layout
| Path | What |
|---|---|
| `sanctum-of-ash.html` | the entire game — **edit this** |
| `sw.js` | service worker (offline + auto-update); bump `CACHE` each release |
| `index.html` | redirect to the game |
| `manifest.webmanifest`, `icon-*.png` | PWA / home-screen install metadata |
| `native/` | Capacitor iOS wrapper (`setup-ios.sh` re-bundles the game) |
| `MOBILE.md` | deeper notes on the touch UI |

## Develop
1. Edit `sanctum-of-ash.html`.
2. Run it locally:
   ```bash
   python3 -m http.server 8841
   # open http://localhost:8841/sanctum-of-ash.html
   ```
   Append `?forcetouch` to the URL to preview the **mobile touch layout** on desktop.
3. Ship it: bump `CACHE` in `sw.js`, then `git push`. GitHub Pages serves the new build at
   `guyzyskind.com/sanctum/` within ~a minute.

The desktop/web layout is the baseline. All mobile changes are scoped to `body.touch` CSS
and the `game.lowGfx` flag, so they never alter the desktop version. The title screen shows
a `build vN` tag (on touch) so you can confirm which version a device actually loaded.

## Keeping the three in sync
- **Web + mobile web (PWA):** automatic. Push → the next online launch loads the new build
  (the service worker serves the game network-first).
- **Native iOS app:** manual — it bundles a *snapshot*. After shipping a new build, run
  `native/setup-ios.sh` then **▶ Run** in Xcode to push it onto the device.

> Hosting note: this is the `guyz/sanctum` repo, published via GitHub Pages under the
> account's custom domain at `/sanctum/`. It has no `CNAME`, so it never claims the domain
> root — `guyzyskind.com` itself is a separate repo.
