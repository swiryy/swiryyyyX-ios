# swiryyyyX for iOS — experimental build

Public iOS source patch and build recipe based on [Swiftgram](https://github.com/Swiftgram/Telegram-iOS), pinned to the commit in `ios/UPSTREAM_COMMIT`.

The patch adds experimental hidden chats and reviewed manual forwarding from Saved Messages to selected folder recipients. Scheduled automatic forwarding is excluded. This repository contains no Android source or private repository history.

## Build

Set repository Actions secrets `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` with your own Telegram application credentials. Never commit credentials, provisioning profiles, signing keys or login codes.

Open **Actions → iPhone experimental build → Run workflow**. The default is **release_arm64**, which builds only the iPhone application. `debug_sim_arm64` is available for explicit simulator checks. Builds use a standard macOS 26 runner and Xcode 26.2. Only public dependency downloads are cached; compiled products and generated credential configuration are excluded from the cache.

The iPhone artifact is `swiryyyyX-ios-unsigned`, containing `swiryyyyX-unsigned.ipa`. It needs owner signing before installation. The simulator artifact cannot run on an iPhone.

The feature patch passed simulator compilation in the private preparation project; the unsigned device recipe is still being validated. A successful build does not establish real-device behavior or privacy/performance guarantees. Read [beta limits](ios/TEST_BETA.md) and [installation instructions](ios/INSTALL_TEST.md).

## Source and notices

This repository distributes a patch, not a complete copy of Swiftgram/Telegram. Builds fetch the exact upstream source and recursive dependencies and retain their existing notices. Upstream source and third-party components retain their respective licenses and attribution. No affiliation with Telegram or Swiftgram is claimed. Generated beta artifacts are public and expire after seven days.
