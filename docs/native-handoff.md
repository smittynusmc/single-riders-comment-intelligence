# Native Windows Handoff

The native bundle is the fallback path now that hosted deployment is the primary internal setup.

This repo now supports a native Windows packaging path in addition to the Docker handoff. The native path is designed for teammates who should not need Python, Node, PostgreSQL, or Redis installed on their computer.

## What the native package includes

- a bundled API executable
- a bundled Next.js standalone server
- a bundled Node runtime
- SQLite for local persistence
- inline processing so no Redis worker service is required
- Windows start and stop scripts

## What the installer user does

1. Install the packaged app or unzip the native portable bundle.
2. Double-click `scripts\start-native.bat`.
3. Wait for the browser to open `http://127.0.0.1:3000/guide`.
4. Upload a TikTok JSON export on the `Imports` page.
5. Double-click `scripts\stop-native.bat` when finished.

The app stores the SQLite database and logs under:

- `%LOCALAPPDATA%\Single Riders Comment Intelligence`

## How to build the native bundle

Builder machine requirements:

- Windows
- Python 3.11+
- Node 20+
- project dependencies installed

Optional for a real `.exe` installer:

- Inno Setup 6

Build command:

- `.\scripts\build-native-installer.bat`

That script:

1. packages the API with PyInstaller
2. builds the web app in Next.js standalone mode
3. stages a native bundle in `dist\native\Single Riders Comment Intelligence`
4. creates `dist\native\single-riders-comment-intelligence-native-portable.zip`
5. builds `single-riders-comment-intelligence-installer.exe` if Inno Setup is installed

## First-run behavior

On first launch, the native API bootstrap creates the SQLite schema automatically. This native handoff path is intended for demos, reviews, and internal testing. For long-lived production environments, keep using the main deployment path with proper migrations and managed services.

## TikTok JSON instructions

Use TikTok's official account data export flow:

1. Open TikTok.
2. Go to `Profile`.
3. Open `Menu`.
4. Open `Settings and privacy`.
5. Open `Account`.
6. Open `Download your data`.
7. Choose `JSON`.
8. Submit the request and wait for TikTok to prepare the export.
9. Download the file when TikTok marks it ready.

Official TikTok help page:

- https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/how-to-download-your-data
