# Publishing Fableborn — runbook

This is the end-of-line **housekeeping** (accounts, keys, store metadata). All the *code* is already done
and verified — sync + OTA are wired but **inert until you fill in the keys below**, so the game ships
fine right now without any of this.

## What's already built (code complete)
- **Prod/dev channels** — `./setup-ios.sh prod` ships clean (no dev/god, maze-only brain game);
  `./setup-ios.sh dev` is your test build with all tools. (Committed.)
- **Cloud sync** (Supabase) — a "☁ Sign in to sync" button on the title + pause screens; pushes/pulls
  save blobs, newest-wins. Hidden & inert until `window.__CFG` has your Supabase keys.
- **Sign in with Apple** — native flow (`@capacitor-community/apple-sign-in`) + web OAuth fallback, both
  exchanged with Supabase. Plugin is linked into the iOS binary.
- **OTA self-update** (`@capgo/capacitor-updater`) — plugin linked; `notifyAppReady` wired;
  `autoUpdate:false` until you set a host. Web/PWA already auto-updates via the service worker.

---

## Step 1 — Apple (you're already enrolled ✅)
1. Confirm membership is **Active** at developer.apple.com/account; note your **Team ID**.
2. **App Store Connect** → My Apps → **＋ New App**: Bundle ID `com.guyz.sanctum`, name "Fableborn",
   primary language, SKU (anything), category **Games**.
3. **Sign in with Apple setup** (needed for sync login):
   - In the Apple **Developer** portal → Identifiers → your App ID `com.guyz.sanctum` → enable the
     **Sign in with Apple** capability.
   - Create a **Services ID** (e.g. `com.guyz.sanctum.web`) for the web OAuth flow; enable Sign in with
     Apple on it; add return URL `https://<your-project-ref>.supabase.co/auth/v1/callback`.
   - Create a **Sign in with Apple Key** (.p8) — you'll paste its Key ID + the key into Supabase (Step 2).
   - In **Xcode** (Signing & Capabilities, App target): add the **Sign in with Apple** capability.
4. Age rating: **4+**. (Recommend *not* opting into the Kids Category — it adds strict rules; 4+ is enough.)
5. Privacy: host `privacy.html` (e.g. push to GitHub Pages → `https://<you>.github.io/sanctum/privacy.html`),
   put your support email in it, and paste that URL into App Store Connect → App Privacy. Privacy "nutrition
   label": declare **Email** (optional, account) + **Other Data: game saves**, *not used for tracking*.
6. Screenshots: needed for **6.7" iPhone**, **6.5" iPhone**, and **12.9" iPad**. (I can capture these from
   the running app once you say go.)

## Step 2 — Supabase (then send me 2 values)
1. supabase.com → **New Project** (free tier).
2. **SQL Editor** → run:
   ```sql
   create table public.saves (
     user_id  uuid not null references auth.users on delete cascade default auth.uid(),
     slot     int  not null,
     blob     jsonb not null,
     saved_at timestamptz not null default now(),
     primary key (user_id, slot)
   );
   alter table public.saves enable row level security;
   create policy "own saves" on public.saves
     for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
   ```
3. **Authentication → Providers → Apple**: enable it; paste your Services ID, Team ID, Key ID, and the
   .p8 key from Step 1.
4. **Project Settings → API**: send me the **Project URL** and the **anon public** key (NOT `service_role`).
   I'll bake them into `window.__CFG` (one line, near the top of `sanctum-of-ash.html`) — the anon key is
   designed to ship in clients, so it's safe to commit.

## Step 3 — OTA host (optional; can enable after launch)
Capgo self-hosted needs an endpoint the app polls for new web bundles. Simplest: a **Supabase Edge
Function** for the manifest + **Supabase Storage** for the bundle zip. To enable:
1. Set `capacitor.config.json` → `CapacitorUpdater.autoUpdate: true` and `updateUrl` to your function URL.
2. Publish a bundle: `./setup-ios.sh prod` builds `native/www`; zip it and upload per the Capgo self-hosted
   docs (I'll script `setup-ios.sh ota-publish` once the host exists).
> Until then, updates ship the normal way (web auto-updates; native needs an App Store release). OTA is a
> post-launch nice-to-have — don't let it block the first submission.

## Step 4 — build & submit
1. `cd native && ./setup-ios.sh prod` → `npx cap open ios`.
2. Xcode: set the Team (your membership), bump version/build, **Product → Archive** → **Distribute App** →
   App Store Connect.
3. In App Store Connect: attach the build, finish metadata + screenshots + privacy, submit for review.
4. **TestFlight** first (recommended) to try the prod build on your devices before public release.

---

### When you've done Step 2, paste me:
- Supabase **Project URL**
- Supabase **anon public** key

…and I'll wire + test sync end-to-end, then help capture screenshots and walk the submission.
