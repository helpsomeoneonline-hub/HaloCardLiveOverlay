# HaloCard Live Overlay

Android screen overlay that calculates the remaining HaloCard balance from the visible dashboard.

## Installing and updating

The APK is built by **GitHub Actions**. After configuring the `HALOCARD_SIGNING_BUNDLE_B64` repository Actions secret, run the **Build HaloCard Overlay APK** workflow. The signed release is published at [GitHub Releases](https://github.com/helpsomeoneonline-hub/HaloCardLiveOverlay/releases).

Keep the keystore backup private and safe. Every future release must use the same signing certificate and application ID, with a larger Android `versionCode`, for upgrades without reinstalling.

The v1.6 app includes an expandable, movable balance bubble and an exportable diagnostics log. Android permissions and Firefox behavior still need testing on the target tablet.
