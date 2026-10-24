# Permanently signed APK validation

Requested after updating repository secret `HALOCARD_SIGNING_BUNDLE_B64`.

This commit triggers the Android v1.6 GitHub Actions workflow. Check that `assembleRelease` succeeds and that the published v1.6 APK uses the permanently configured certificate. No private signing material should be committed.
