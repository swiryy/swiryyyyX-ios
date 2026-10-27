# Installing the experimental iPhone build

No installable release is confirmed until the device CI job passes and a signed build opens on the owner's iPhone.

## Get the right file

Open the successful iOS Actions run and download the **swiryyyyX-ios-unsigned** artifact. Extract it to obtain **swiryyyyX-unsigned.ipa**. Do not use **swiryyyyX-ios-simulator** on an iPhone.

The IPA is unsigned. A browser download alone cannot install it. Do not upload Apple ID credentials, private signing keys, provisioning profiles or session data to this repository or a chat.

## Local test installation

AltStore Classic with AltServer is one possible test route for an owner without a paid developer account. Use its official instructions and current downloads:

- https://altstore.io/
- https://faq.altstore.io/altstore-classic/how-to-install-altstore-macos
- https://faq.altstore.io/altstore-classic/your-altstore

The documented macOS route requires connecting and unlocking the iPhone, trusting the Mac, signing in locally with an Apple ID and enabling Developer Mode when applicable. The owner must handle device trust, Apple authentication and any agreements. A normal free-account installation needs periodic renewal; AltStore documents seven-day expiration and a three-active-app limit. This project does not configure that connection automatically.

The first device beta omits app extensions and disables Siri/iCloud integrations. Background push is not configured. Keep an existing working Telegram client while testing this independent application; do not erase its data to fix a signing problem.

## Start with a small functional test

1. Open swiryyyyX and log in through Telegram's ordinary UI.
2. Check ordinary chats, folders and Saved Messages.
3. Hide an expendable test chat, restart the app and verify the list/search behavior. Restore it through the authenticated menu on Saved Messages.
4. Create a folder containing two test chats you control. Forward one harmless Saved Messages item with reviewed recipients. Verify actual delivery once in each chat.
5. Test cancellation and account switching before using larger folders.
6. Only then compare launch, scrolling, search, folder switching and memory with a 230-chat folder. Record iPhone model, iOS version, build number and exact reproduction steps. Do not include private messages, phone numbers or login codes in reports.

Hiding remains experimental; review TEST_BETA.md before relying on it.
