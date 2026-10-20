# Budsy Protocol Lab

Android BLE GATT exploration project for OnePlus Nord Buds 3 research.

The source bundle is stored as `BudsyProtocolLab_with_workflow.zip`. GitHub Actions extracts the bundle, builds the debug APK, and uploads it as the `BudsyProtocolLab-debug-apk` artifact.

Open the **Actions** tab to view build status and download the APK artifact after a successful run.

**Research limits:** This app logs GATT operations it performs; it does not passively intercept HeyMelody's private Bluetooth traffic. Physical testing with OnePlus Nord Buds 3 has not yet been verified.
