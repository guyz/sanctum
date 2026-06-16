# Sanctum of Ash — iPad / iPhone

The game now detects touch devices and switches to a **touch control scheme** automatically
(the desktop/web version is unchanged). On an iPhone/iPad you get:

- a **left-thumb virtual joystick** to move,
- big **right-side action buttons** (attack/talk, the 4 spells, potion, dash, town portal),
- **top utility buttons**: 🎒 inventory · 🌳 skills · 🗺️ map · ⏸️ menu,
- spells auto-aim where you're facing (no mouse needed), melee auto-targets the nearest foe.

The whole game is **one self-contained file** (three.js is inlined; models/textures are embedded),
so it runs fully **offline** once installed. The game is built for **landscape**.

There are two ways to get it on your devices. **Path A needs nothing but Safari.**

---

## Path A — Install from Safari (recommended, no Mac tools)

This uses the PWA build hosted on GitHub Pages. Nothing to compile.

1. On your iPhone/iPad, open **Safari** and go to:
   **https://guyzyskind.com/sanctum/sanctum-of-ash.html**
2. Tap the **Share** button (the square with the ↑ arrow).
3. Tap **Add to Home Screen** → **Add**.
4. Launch it from the new **Sanctum of Ash** icon (the flame).

It opens **fullscreen** (no Safari bars) and works **offline** afterward (a service worker
caches the whole game on first load — the first load is ~20 MB, so use Wi-Fi once).

To update later: I bump the version and push; on the device, open it once on Wi-Fi and it
refreshes itself (or remove + re-add the icon).

---

## Path B — Real native app (Capacitor + Xcode)

A true `.app` installed via Xcode. Same game inside a native WebView. Use this if you want an
actual installed app rather than a home-screen web app.

**One-time prerequisite:** install **Xcode** from the Mac App Store (large, ~15 GB) and open it
once to finish setup. (Node is already installed; Capacitor 8 uses Swift Package Manager, so no
CocoaPods is needed.)

Then, from this folder:

```bash
cd native
./setup-ios.sh        # copies the latest game in, installs Capacitor, builds the iOS project
npx cap open ios      # opens the project in Xcode
```

In Xcode (one-time signing with a **free** Apple ID — no $99 needed):

1. Select the **App** target → **Signing & Capabilities** tab.
2. Tick **Automatically manage signing**.
3. **Team** → pick **"<Your Name> (Personal Team)"**. (If it's not listed: Xcode → Settings →
   Accounts → **+** → sign in with your Apple ID.)
4. The **Bundle Identifier** is `com.guyz.sanctum` — if Xcode complains it's taken, change it to
   something unique like `com.guyz.sanctum2`.
5. Plug your iPhone/iPad into the Mac, unlock it, tap **Trust This Computer**.
6. Pick your device in the destination dropdown (top bar), press **Run** (⌘R).
7. First launch on the device: iOS asks you to trust the app —
   **Settings → General → VPN & Device Management → Apple Development: <your email> → Trust**.
   (If iOS prompts for **Developer Mode**: Settings → Privacy & Security → Developer Mode → on → reboot.)

**Free Apple ID caveat:** a free signing certificate **expires after 7 days** — when the app
stops opening, just plug in and press **Run** again to refresh it for another week. A paid
Apple Developer account ($99/yr) makes it last ~1 year instead. Everything else works on the free tier.

After editing the game later, re-run `./setup-ios.sh` (it re-copies the HTML) then Run again in Xcode.

---

## Notes

- **Default-to-mobile:** detection uses `navigator.maxTouchPoints` + `(any-pointer: coarse)` +
  `ontouchstart`, which correctly flags iPhone **and** iPad (iPadOS reports a Mac UA, so UA sniffing
  would miss it — this doesn't). Desktop stays mouse/keyboard.
- **Testing touch on a desktop browser:** add `?forcetouch` to the URL to force the touch UI on.
- **iOS specifics handled:** `viewport-fit=cover` + safe-area insets (notch / home indicator),
  `black-translucent` status bar for full-bleed, pinch/double-tap-zoom blocked, multitouch so you
  can move and cast at once, `touchcancel` handled so the stick never sticks.
- Files added for mobile: `manifest.webmanifest`, `sw.js`, `icon-180/192/512.png`, `index.html`
  (redirect), `native/` (Capacitor project + `setup-ios.sh`).
