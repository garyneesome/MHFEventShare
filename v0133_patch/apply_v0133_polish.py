#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1])
main = root / 'app/src/main/java/uk/co/mentalhealthfriends/eventshare/MainActivity.java'
text = main.read_text()

old_heading = '        addHeading("Set up private multi-send", "Do this once. After setup, MHF can open one Messages compose screen for all selected text recipients.");\n'
new_heading = '''        addHeading("Set up Fast Text", "Do this once. Fast Text needs three phone settings so each person receives a private SMS.");
        body.addView(infoCard("Before you use Fast Text", "1. Mass text ON   •   2. RCS chats OFF   •   3. Premium text services ALLOWED"));
'''
if old_heading in text:
    text = text.replace(old_heading, new_heading, 1)

old_step1 = '        step1.addView(text("1  Set Messages to Mass text", 16, true, CHARCOAL));\n'
if old_step1 in text:
    text = text.replace(old_step1, '        step1.addView(text("1  Turn on Mass text", 16, true, CHARCOAL));\n', 1)

old_step2 = '''        step2.addView(text("2  If it still creates an RCS group", 16, true, CHARCOAL));
        step2.addView(text("In Google Messages open Messages settings → RCS chats and turn RCS off for this use. Only do this if Mass text still opens as an RCS/group conversation.", 13, false, MUTED));
        body.addView(step2);
'''
new_step2 = '''        step2.addView(text("2  Turn RCS chats off", 16, true, CHARCOAL));
        step2.addView(text("Google Messages → profile picture → Messages settings → RCS chats → turn RCS chats OFF. Fast Text must use normal SMS rather than an RCS group chat.", 13, false, MUTED));
        step2.addView(secondaryButton("Open Google Messages", this::openGoogleMessagesForSmsSetup));
        body.addView(step2);
'''
if old_step2 in text:
    text = text.replace(old_step2, new_step2, 1)

old_step3 = '''        step3.addView(text("3  Allow premium text services if your phone asks", 16, true, CHARCOAL));
        step3.addView(text("Android Settings → Apps → Special app access → Premium SMS / Use premium text message services → choose the messaging app and allow it. Wording varies by phone.", 13, false, MUTED));
        step3.addView(secondaryButton("Open Special app access", this::openSpecialAppAccess));
'''
new_step3 = '''        step3.addView(text("3  Allow Premium text message services", 16, true, CHARCOAL));
        step3.addView(text("Android Settings → Apps → Special app access → Premium SMS / Use premium text message services → choose your Messages app → Always allow. Wording varies by phone.", 13, false, MUTED));
        step3.addView(secondaryButton("Open Android messaging settings", this::openSpecialAppAccess));
'''
if old_step3 in text:
    text = text.replace(old_step3, new_step3, 1)

text = text.replace("I've completed the Mass text setup and tested it", "I've completed all 3 Fast Text settings and tested them")
text = text.replace("Fast private texting enabled", "Fast Text enabled")

pattern = re.compile(r'''    private void showEventSwipeActions\(EventDraft e\) \{.*?\n    \}\n\n    private void showHistory\(\) \{ showEvents\(\); \}\n''', re.S)
replacement = r'''    private void showEventSwipeActions(EventDraft e) {
        final AlertDialog[] holder = new AlertDialog[1];
        LinearLayout box = dialogBox();
        box.addView(text(e.title.isEmpty() ? "Event actions" : e.title, 18, true, CHARCOAL));
        box.addView(text(e.displayDate() + "  •  " + e.displayTime(), 12, false, MUTED));
        box.addView(space(dp(10)));

        String mainLabel = "in_progress".equals(e.deliveryState) ? "▶ Continue"
                : ("completed".equals(e.deliveryState) ? "↻ Send again" : "▶ Send");
        Button mainAction = primaryButton(mainLabel, null);
        mainAction.setOnClickListener(v -> {
            if (holder[0] != null) holder[0].dismiss();
            if ("in_progress".equals(e.deliveryState)) {
                currentEvent = EventDraft.from(e.json()); repo.saveCurrentEvent(currentEvent); continueCurrentEventSend(true);
            } else if ("completed".equals(e.deliveryState)) {
                showResendOptions(e);
            } else {
                currentEvent = EventDraft.from(e.json()); repo.saveCurrentEvent(currentEvent); beginAudienceSelection();
            }
        });
        box.addView(mainAction);

        LinearLayout row1 = horizontal();
        Button edit = secondaryButton("✎  Edit", null);
        edit.setOnClickListener(v -> {
            if (holder[0] != null) holder[0].dismiss();
            currentEvent = EventDraft.from(e.json()); repo.saveCurrentEvent(currentEvent); showEventEditor(false);
        });
        row1.addView(edit, weight());
        row1.addView(space(dp(8)));
        Button duplicate = secondaryButton("⧉  Duplicate", null);
        duplicate.setOnClickListener(v -> {
            if (holder[0] != null) holder[0].dismiss();
            currentEvent = EventDraft.from(e.json());
            currentEvent.id = java.util.UUID.randomUUID().toString();
            currentEvent.createdAt = System.currentTimeMillis();
            currentEvent.deliveryState = "not_started"; currentEvent.lastSendAt = 0L;
            currentEvent.deliveryResults.clear(); currentEvent.deliveryLabels.clear();
            currentEvent.lastAudiencePersonIds.clear(); currentEvent.lastAudienceGroupIds.clear(); currentEvent.lastAudienceWhatsApp = false;
            repo.saveCurrentEvent(currentEvent); showEventEditor(false);
        });
        row1.addView(duplicate, weight());
        box.addView(row1);

        if ("in_progress".equals(e.deliveryState)) {
            Button done = secondaryButton("✓  Mark complete", null);
            done.setOnClickListener(v -> {
                if (holder[0] != null) holder[0].dismiss();
                EventDraft updated = EventDraft.from(e.json()); updated.deliveryState = "completed"; repo.saveEventToHistory(updated); showEvents();
            });
            box.addView(done);
        }

        Button delete = secondaryButton("⌫  Delete event", null);
        delete.setOnClickListener(v -> {
            if (holder[0] != null) holder[0].dismiss();
            new AlertDialog.Builder(this).setTitle("Delete this saved event?").setMessage(e.title)
                    .setNegativeButton("Cancel", null)
                    .setPositiveButton("Delete", (x,w) -> { repo.deleteHistoryEvent(e.id); showEvents(); }).show();
        });
        box.addView(delete);

        holder[0] = new AlertDialog.Builder(this)
                .setView(box)
                .setNegativeButton("Close", null)
                .create();
        holder[0].show();
    }

    private void showHistory() { showEvents(); }
'''
text, n = pattern.subn(replacement, text, count=1)
if n != 1:
    raise SystemExit('showEventSwipeActions method not found')

main.write_text(text)
print('Applied v0.13.3 SMS clarity and event action panel polish')
