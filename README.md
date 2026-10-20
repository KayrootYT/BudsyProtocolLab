# Budsy Protocol Lab

Android BLE GATT exploration project for OnePlus Nord Buds 3 research.

## Upload the project ZIP
The repository setup and GitHub Actions workflow are ready, but the binary ZIP could not be uploaded by the connected GitHub text-file integration. Download `BudsyProtocolLab_with_workflow.zip` from the ChatGPT conversation and upload the actual ZIP file to this repository's root (not a placeholder or extracted folder).

When `BudsyProtocolLab_with_workflow.zip` is pushed, GitHub Actions will extract it, build the debug APK, and upload the artifact named `BudsyProtocolLab-debug-apk`.

Workflow status: https://github.com/KayrootYT/BudsyProtocolLab/actions

## Research limits
This app logs GATT operations it performs; it does not passively intercept HeyMelody's private Bluetooth traffic. Physical testing with OnePlus Nord Buds 3 has not been verified.
