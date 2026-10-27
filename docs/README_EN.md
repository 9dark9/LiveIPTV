# LIVE直播源 (LiveIPTV) — playlist checker for Windows

> Author: **HaiFeng (kele551)** · GitHub (the only host): <https://github.com/kele551/LiveIPTV>
> 中文说明见 [../README.md](../README.md)

A **single-file Windows app** (no installer required). It reads publicly available IPTV playlist URLs
(`.m3u` / `.m3u8` text), merges and de-duplicates the entries, **actually probes each stream** to see whether
it plays right now and at what quality, and exports one clean local M3U you can feed to
PotPlayer / VLC / Kodi / an IPTV box.

## What it does

- Pulls the playlists **you enable** (a handful of public third-party lists ship as defaults; you can turn
  every one of them off and paste your own)
- Merges by channel name and de-duplicates — around 720 channels after the merge
- Re-checks availability every 6 hours by default: connects, rejects HTML responses, then pulls a short
  window to measure **real resolution and bitrate**
- Grades each channel — only 1080p at 2 Mbps or better counts as "达标"; filter by 达标 / 清晰 / 400 KB/s+ /
  4K / 1080P / 720P / bitrate band
- Serves a local console at `http://127.0.0.1:8899` (port auto-increments if taken), with search, group
  filters, favourites and offline channel logos
- Exports a UTF-8 BOM `#EXTM3U` file

## What it deliberately does not do

- ❌ It provides, hosts, proxies, relays or redistributes **no live content whatsoever** — only links it read
  from public lists
- ❌ It does not defeat any encryption, DRM, paywall or access control, and it is not a way to watch a
  specific channel you are not entitled to
- ❌ It does not collect or upload user data: no accounts, no analytics, no ads; everything is written to
  your local data directory
- ❌ It does not touch `hosts`, system DNS or system proxy, and needs no admin rights

Channel names, logos and programme rights belong to their respective owners. This tool is affiliated with
no broadcaster, platform or operator. Availability and legality of any given stream depend on your
jurisdiction and on the source itself — see [COMPLIANCE.md](COMPLIANCE.md).

## Download

- **GitHub (the only host for this one)**: <https://github.com/kele551/LiveIPTV/releases>

Asset name: `LiveIPTV.exe` (single file — double-click to run). Locally, `build_exe.py` emits
`LIVE直播源.exe`; the file published to Releases is renamed to the ASCII `LiveIPTV.exe`, so the two
names are the same build. Unlike the other three apps in this series, LiveIPTV is **not** mirrored on
GitCode / AtomGit.

## Build and verify

```powershell
python LIVE直播源.py            # run from source: console at http://127.0.0.1:8899
python build_exe.py             # produces builds/v<version>/LIVE直播源.exe
python tools/verify_release.py  # checks the published assets byte-for-byte
```

Data directory defaults to `%APPDATA%\LIVE直播源`; set `LIVE_DATA` to point it elsewhere (portable / testing).

## Repository layout & contributing

- Contributing guide: [CONTRIBUTING.md](CONTRIBUTING.md) · Security policy: [SECURITY.md](SECURITY.md) · Compliance: [COMPLIANCE.md](COMPLIANCE.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md) · Code signing policy: [CODE_SIGNING_POLICY.md](CODE_SIGNING_POLICY.md)

## Third-party components

**Zero third-party runtime dependencies** — Python standard library only (`http.server`, `urllib`,
`concurrent.futures`, `ctypes`, …). The Ed25519 signature check is a self-contained `_ed25519.py`.

## License

MIT — see [../LICENSE](../LICENSE).
