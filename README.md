# Mental Health Friends – Event Share v0.2.0

A local-first Android app for community groups that create events on Facebook but also need to reach people through WhatsApp, SMS, email, calendar files, posters and other Android sharing apps.

## What this release does

### Simple guided workflow
1. **Event** – type an event or use Facebook/another app's **Share** action and choose MHF Event Share.
2. **Audience** – choose one or more reusable groups, or everyone who is not Facebook-only.
3. **Review** – see deduplicated WhatsApp/SMS/email counts and the exact message before anything opens.
4. **Send** – work through the safe send methods.

### People and recipient groups
- Add people manually.
- Import a mobile number/name through the Android Contacts picker.
- Save phone and email separately.
- Set a preferred method: WhatsApp, SMS, Email or Facebook only.
- Set **event-update consent** on/off; new/imported contacts default to off until explicitly confirmed.
- Set a person **active/inactive** without deleting them.
- Create reusable groups such as:
  - People not on Facebook
  - Coffee Morning
  - Thursday Group
  - Volunteers
- A person can be in several groups and is still included only once per send.

### Privacy-friendly sending
- **WhatsApp:** one-person-at-a-time queue. The app opens the person's WhatsApp chat with the event pre-filled. The user taps Send, returns to MHF Event Share and taps Next.
- **SMS:** also one-person-at-a-time so a multi-recipient group message cannot reveal everyone else's phone numbers.
- **Email:** one prepared email using **BCC** so recipients do not see the full mailing list.
- Facebook-only, inactive, non-consented, or incomplete recipients are automatically skipped from direct sending.
- There is no code that silently presses Send or bulk-automates WhatsApp.

### Event tools
- Event title, date, start/end time, venue, description and optional Facebook link.
- Message preview before sending.
- Event history (latest 20) with reuse/delete.
- Copy event text.
- Generic Android Sharesheet.
- Generate and share a branded **1080×1350 event poster PNG**.
- Generate and share an **`.ics` calendar file**.
- Open Android's Calendar event editor with the event details already filled in.

### Backup and settings
- Organisation name, website, extra signature and default phone country code.
- UK number handling: e.g. `07123...` becomes `447123...` for WhatsApp when country code is `44`.
- Export all app data to a user-chosen JSON backup file.
- Restore a backup only after an explicit confirmation.
- Android automatic/cloud app backup is disabled; the manual backup remains under the user's control.

## Cost and network use

The app has **no server, account, subscription or paid API** and does not request the Android `INTERNET` permission.

It hands prepared content to apps already installed on the phone, such as WhatsApp, Messages, Email and Calendar. Normal mobile-network/SMS charges from the phone provider can still apply to SMS messages.

## Android support

- Minimum Android: API 26 (Android 8.0)
- Compile/target SDK: API 36 (Android 16)
- Java 17
- Android Gradle Plugin 8.13.2
- AndroidX Core 1.17.0 (used for secure `FileProvider` sharing of generated poster/calendar files)

## Build in Android Studio (recommended)

1. Install a current Android Studio.
2. Extract this project ZIP.
3. In Android Studio choose **Open** and select the project folder.
4. If prompted, install Android SDK Platform 36 and the required build tools.
5. Let Gradle sync finish.
6. Connect an Android phone with USB debugging enabled, or use an emulator.
7. Click **Run** to test.
8. To create an installable debug APK choose **Build > Build App Bundle(s) / APK(s) > Build APK(s)**.
9. The APK will normally be under `app/build/outputs/apk/debug/app-debug.apk`.

For a release APK, configure your own Android signing key before distribution.

## Free GitHub Actions build option

A workflow is included at `.github/workflows/build-apk.yml`. If the source is put in a GitHub repository, the **Build Android APK** action can compile a debug APK and attach it as an Actions artifact. It uses GitHub-hosted build tooling; check the GitHub plan/usage limits for the account before relying on it.

## Suggested first test

1. Add 3 test people: one WhatsApp, one SMS and one email.
2. Create a group named `Test group` and add all three.
3. Create an event.
4. Choose `Test group` in Send.
5. Confirm the Review screen shows one recipient for each method.
6. Test WhatsApp/SMS with your own spare/test numbers before entering real community member data.
7. Export a backup and verify it can be restored on a test installation.

## Important operational notes

- Do not use the app as an emergency-alert system. Delivery is dependent on the recipient's chosen messaging service and the user completing the send action.
- Keep recipient consent records appropriate for the community group's own privacy/data-protection process.
- The app stores names/contact details locally, so protect the phone with a screen lock and treat exported backups as private data.
