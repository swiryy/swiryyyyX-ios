# swiryyyyX iOS experimental port

This revision requires compilation and device validation. It is not a tested privacy product or an installable iPhone release yet.

## Manual checks

- Long-press a chat > swiryyyyX: приховати чат. Check main list, pinned chats, archive, folders, local/global search and notification previews while foregrounded and backgrounded.
- Long-press Saved Messages > swiryyyyX: відкрити приховані чати. Authenticate with the device. Tap a chat to restore it. Leaving the app closes the hidden list.
- Hidden settings are scoped by Telegram account peer ID and shared with the notification extension using the application's own App Group.
- Select messages in Saved Messages > Forward > Select > open a specific folder > Уся папка. Review the selected recipients and forwarding options, then confirm sending. Nothing is sent by tests.
- Bulk folder selection refuses incomplete snapshots or more than 1000 recipients. Unwritable peers, Premium-restricted peers and secret chats are excluded with a skipped-recipient count. Paid or scheduled recipients are rejected by the new bulk queue.
- The queue runs one recipient at a time, waits for correlation-ID delivery acknowledgements and adds a 200 ms gap. Telegram's native pending-message mechanism handles the current recipient. An error or 5-minute uncertainty stops further recipients. No automatic replay after process restart.
- Stop future recipients from Saved Messages > swiryyyyX: зупинити пересилання. Already enqueued messages remain Telegram's responsibility and may still be delivered. Switching accounts stops the queue.
- Check 230-chat folder scrolling, folder switching, search, memory and forwarding responsiveness on a real iPhone. No performance result is claimed yet.

## Known beta limits

- While any chats are hidden, the archive summary badge is suppressed to avoid leaking hidden unread activity. Folder counters and the application badge are filtered separately.
- Other discovery surfaces, chat shortcuts, widgets, Siri and received call UI still require a privacy audit. Do not rely on experimental hiding to protect sensitive conversations until that audit and device tests pass.
- The simulator archive cannot be installed on iPhone. After the simulator job passes, a separate release arm64 job attempts to create `swiryyyyX-unsigned.ipa`. Its platform and bundle ID are checked before publishing. The IPA still requires owner signing and device validation; neither is claimed by compilation.
- The initial device build omits app extensions and disables Siri/iCloud integrations. Widgets, system Share, broadcast upload and the notification extension are absent from this sideloading beta. Background push also needs owner-controlled provisioning and infrastructure. The simulator build retains extensions to compile-check their privacy changes.
- The owner currently has no signing/install setup. AltStore Classic is a possible local test path, subject to its App ID and renewal limits; it is not configured by this revision.
- Android and iOS recurring automatic forwarding remain out of scope for this patch. Android files were not modified.
