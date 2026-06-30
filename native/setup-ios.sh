#!/bin/bash
# One-shot setup for the native iOS build of Fableborn (Capacitor 8 + Swift Package Manager).
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

# Inject the cloud config (Supabase URL + anon key) from the gitignored sanctum.config.json into the
# bundled www/index.html so Sign in with Apple + save-sync are LIVE on the device. The committed HTML
# keeps __CFG empty, so the public web build stays cloud-off until we deploy keys there too.
if [ -f sanctum.config.json ]; then
  echo "==> Injecting cloud config (Supabase keys) from sanctum.config.json ..."
  node -e '
    const fs = require("fs");
    const cfg = JSON.parse(fs.readFileSync("sanctum.config.json", "utf8"));
    const f = "www/index.html"; let h = fs.readFileSync(f, "utf8");
    const inj = "window.__CFG={supabaseUrl:" + JSON.stringify(cfg.supabaseUrl || "") +
                ",supabaseAnonKey:" + JSON.stringify(cfg.supabaseAnonKey || "") +
                ",otaUrl:" + JSON.stringify(cfg.otaUrl || "") + "};";
    const re = /window\.__CFG=window\.__CFG\|\|\{[^}]*\};/;
    if (!re.test(h)) { console.error("   !! could not find the __CFG line to replace"); process.exit(1); }
    fs.writeFileSync(f, h.replace(re, inj));
    console.log("   cloud sign-in/sync:", cfg.supabaseUrl ? "ENABLED (" + cfg.supabaseUrl + ")" : "(no url — stays off)");
  '
else
  echo "==> (no sanctum.config.json — cloud sign-in/sync stays OFF in this build)"
fi

echo "==> Installing Capacitor (first run only) ..."
if [ ! -d node_modules ]; then
  npm install @capacitor/core @capacitor/ios
  npm install -D @capacitor/cli
fi

# Patch a Swift Package version conflict: @capacitor-community/apple-sign-in (newest is 7.1.0, no Cap-8
# release yet) pins capacitor-swift-pm to 7.x, but @capgo/capacitor-updater needs 8.x — so SPM can't
# resolve and Xcode shows "Missing package product 'CapApp-SPM'". The plugin's Swift only uses the stable
# Capacitor/Cordova products, so widen its range to allow 8.x. Idempotent; re-applied after any install.
APPLE_PKG="node_modules/@capacitor-community/apple-sign-in/Package.swift"
if [ -f "$APPLE_PKG" ] && grep -q 'capacitor-swift-pm.git", from: "7.0.0"' "$APPLE_PKG"; then
  echo "==> Patching apple-sign-in to allow capacitor-swift-pm 8.x (Cap 7+8 conflict fix) ..."
  /usr/bin/sed -i '' 's#capacitor-swift-pm.git", from: "7.0.0"#capacitor-swift-pm.git", "7.0.0"..<"9.0.0"#' "$APPLE_PKG"
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

# Home-screen name: the ios/ project was first generated as "Sanctum of Ash"; force the current name.
# (Capacitor only sets CFBundleDisplayName at `cap add ios` time, not on sync, so pin it here.)
if [ -f ios/App/App/Info.plist ]; then
  /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName Fableborn" ios/App/App/Info.plist 2>/dev/null \
    || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string Fableborn" ios/App/App/Info.plist 2>/dev/null || true
  echo "==> App display name set to 'Fableborn'"
fi

# Sign in with Apple capability: write the entitlement + wire it into BOTH build configs (idempotent).
# Required for the native Apple sign-in (Supabase cloud sync) to work at all. With automatic signing,
# Xcode registers this capability on the App ID on the next build.
ENT=ios/App/App/App.entitlements
if [ -d ios/App/App ]; then
  if [ ! -f "$ENT" ]; then
    cat > "$ENT" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.developer.applesignin</key>
	<array>
		<string>Default</string>
	</array>
</dict>
</plist>
PLIST
  fi
  PB=ios/App/App.xcodeproj/project.pbxproj
  if [ -f "$PB" ] && ! grep -q "CODE_SIGN_ENTITLEMENTS" "$PB"; then
    perl -0pi -e 's/(\n(\t+)CODE_SIGN_STYLE = Automatic;)/$1\n$2CODE_SIGN_ENTITLEMENTS = App\/App.entitlements;/g' "$PB"
    echo "==> Wired Sign in with Apple entitlement into the project"
  fi
fi

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
