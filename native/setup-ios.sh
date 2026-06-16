#!/bin/bash
# One-shot setup for the native iOS build of Sanctum of Ash (Capacitor 8 + Swift Package Manager).
# Re-run any time after you edit the game — it re-copies the latest HTML into the app.
# Requires: Node 22+ (installed) and, to actually build/run, the full Xcode 26+ from the Mac App Store.
set -e
cd "$(dirname "$0")"

echo "==> Copying the game into www/ ..."
mkdir -p www
cp ../sanctum-of-ash.html www/index.html
cp ../icon-180.png ../icon-192.png ../icon-512.png ../manifest.webmanifest ../sw.js www/ 2>/dev/null || true

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

echo "==> Syncing web assets into the native project ..."
npx cap copy ios

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
