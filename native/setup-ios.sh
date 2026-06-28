#!/bin/bash
# One-shot setup for the native iOS build of Sanctum of Ash (Capacitor 8 + Swift Package Manager).
# Re-run any time after you edit the game — it re-copies the latest HTML into the app.
# Requires: Node 22+ (installed) and, to actually build/run, the full Xcode 26+ from the Mac App Store.
set -e
cd "$(dirname "$0")"

# Build channel: "prod" (default — clean public/App-Store build) or "dev" (cheats + all brain games, for your own device).
CHANNEL="${1:-prod}"
if [ "$CHANNEL" != "prod" ] && [ "$CHANNEL" != "dev" ]; then echo "usage: ./setup-ios.sh [prod|dev]"; exit 1; fi
echo "==> BUILD CHANNEL: $CHANNEL"

echo "==> Regenerating PWA home-screen icons from ../appicon.png (keeps them identical to the native icon) ..."
# Single source of truth: appicon.png. Do this BEFORE the www copy so www gets the fresh icons.
if [ -f ../appicon.png ]; then
  sips -s format png -z 180 180 ../appicon.png --out ../icon-180.png >/dev/null 2>&1 || true
  sips -s format png -z 192 192 ../appicon.png --out ../icon-192.png >/dev/null 2>&1 || true
  sips -s format png -z 512 512 ../appicon.png --out ../icon-512.png >/dev/null 2>&1 || true
fi

echo "==> Copying the game into www/ ..."
mkdir -p www
cp ../sanctum-of-ash.html www/index.html
cp ../icon-180.png ../icon-192.png ../icon-512.png ../manifest.webmanifest ../sw.js www/ 2>/dev/null || true
if [ "$CHANNEL" = "dev" ]; then
  echo "==> DEV channel: enabling dev/god tools + all brain games"
  /usr/bin/sed -i '' "s/window.__CHANNEL='prod'/window.__CHANNEL='dev'/" www/index.html
else
  echo "==> PROD channel: dev/god hidden, brain games = maze only"
fi

echo "==> Installing Capacitor (first run only) ..."
if [ ! -d node_modules ]; then
  npm install @capacitor/core @capacitor/ios
  npm install -D @capacitor/cli
fi

echo "==> Generating the native iOS project (first run only) ..."
if [ ! -d ios ]; then
  npx cap add ios
  # lock the iPhone app to landscape (the game's orientation); iPad keeps both
  PLIST=ios/App/App/Info.plist
  /usr/libexec/PlistBuddy -c "Delete :UISupportedInterfaceOrientations" "$PLIST" 2>/dev/null || true
  /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations array" "$PLIST"
  /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations: string UIInterfaceOrientationLandscapeLeft" "$PLIST"
  /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations: string UIInterfaceOrientationLandscapeRight" "$PLIST"
fi

echo "==> Setting the app icon (from ../appicon.png) ..."
[ -f ../appicon.png ] && [ -d ios/App/App/Assets.xcassets/AppIcon.appiconset ] && sips -z 1024 1024 ../appicon.png --out ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png >/dev/null 2>&1 || true

echo "==> Setting the launch screen (from ../splash-screen.png) ..."
# Storyboard shows this 'Splash' scaleAspectFill. Scale to height 2732 then centre-crop to a square,
# so a WIDE source image is not squashed (works for square sources too).
if [ -f ../splash-screen.png ] && [ -d ios/App/App/Assets.xcassets/Splash.imageset ]; then
  sips --resampleHeight 2732 ../splash-screen.png --out /tmp/_sanctum_splash_h.png >/dev/null 2>&1
  sips -c 2732 2732 /tmp/_sanctum_splash_h.png --out /tmp/_sanctum_splash_sq.png >/dev/null 2>&1
  for f in splash-2732x2732.png splash-2732x2732-1.png splash-2732x2732-2.png; do
    cp /tmp/_sanctum_splash_sq.png "ios/App/App/Assets.xcassets/Splash.imageset/$f" >/dev/null 2>&1 || true
  done
fi

echo "==> Syncing web assets + native plugins into the project ..."
npx cap sync ios   # copy web assets AND link native plugins (e.g. the OTA updater)

echo ""
echo "============================================================"
echo " DONE. Now open it in Xcode:"
echo "     cd native && npx cap open ios"
echo ""
echo " In Xcode (one-time signing):"
echo "  1. Select the 'App' target  >  Signing & Capabilities tab"
echo "  2. Tick 'Automatically manage signing'"
echo "  3. Team: pick '<Your Name> (Personal Team)' (add your Apple ID"
echo "     under Xcode > Settings > Accounts if it isn't there)"
echo "  4. Plug in your iPhone/iPad, unlock it, pick it as the destination"
echo "  5. Press Run (Cmd+R). First time: on the device trust the app under"
echo "     Settings > General > VPN & Device Management."
echo "============================================================"
