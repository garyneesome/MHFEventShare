#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'MHFEventShare-v0.13.3')
main = root / 'app/src/main/java/uk/co/mentalhealthfriends/eventshare/MainActivity.java'
gradle = root / 'app/build.gradle'

text = main.read_text()

old_heading = '        addHeading("Events", "Tap an event to continue or send it. Swipe left for Edit, Duplicate, Delete and other actions.");\n'
new_heading = '        addHeading("Events", "Tap an event to continue or send it. Use Actions for Edit, Duplicate, Delete and more. Swipe left still works as a shortcut.");\n'
if old_heading not in text:
    raise SystemExit('Events heading anchor not found')
text = text.replace(old_heading, new_heading, 1)

old_card = '''        LinearLayout c = cardTint(fill, border);
        LinearLayout titleLine = horizontal();
        titleLine.addView(text(e.title.isEmpty() ? "Untitled event" : e.title, 17, true, CHARCOAL), weight());
        titleLine.addView(badge(eventProgressLabel(e), eventBadgeFill(e)));
        c.addView(titleLine);
        c.addView(text(e.displayDate() + "  •  " + e.displayTime(), 13, false, MUTED));
'''
new_card = '''        LinearLayout c = cardTint(fill, border);
        LinearLayout titleLine = horizontal();
        titleLine.addView(text(e.title.isEmpty() ? "Untitled event" : e.title, 17, true, CHARCOAL), weight());

        Button actions = secondaryButton("Actions", null);
        actions.setTextSize(12);
        LinearLayout.LayoutParams actionParams = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, dp(50));
        actionParams.setMargins(dp(8), 0, 0, 0);
        actions.setLayoutParams(actionParams);
        actions.setOnClickListener(v -> showEventSwipeActions(e));
        titleLine.addView(actions);
        c.addView(titleLine);
        c.addView(badge(eventProgressLabel(e), eventBadgeFill(e)));
        c.addView(text(e.displayDate() + "  •  " + e.displayTime(), 13, false, MUTED));
'''
if old_card not in text:
    raise SystemExit('Event card title block not found')
text = text.replace(old_card, new_card, 1)

picker_pattern = re.compile(r'''    private void showColourPicker\(String title, String initialHex, java\.util\.function\.Consumer<String> onPicked\) \{.*?\n    \}\n\n    private void showBackup\(\) \{''', re.S)
new_picker = r'''    private void showColourPicker(String title, String initialHex, java.util.function.Consumer<String> onPicked) {
        int initial = parseThemeColour(initialHex, YELLOW);
        final float[] hsv = new float[3];
        Color.colorToHSV(initial, hsv);

        final int[] paletteColours = new int[]{
                Color.rgb(247, 201, 40), Color.rgb(255, 213, 79), Color.rgb(255, 252, 239), Color.rgb(32, 33, 36), Color.WHITE,
                Color.rgb(244, 67, 54), Color.rgb(233, 30, 99), Color.rgb(156, 39, 176), Color.rgb(103, 58, 183), Color.rgb(63, 81, 181),
                Color.rgb(33, 150, 243), Color.rgb(3, 169, 244), Color.rgb(0, 150, 136), Color.rgb(76, 175, 80), Color.rgb(139, 195, 74),
                Color.rgb(255, 152, 0), Color.rgb(121, 85, 72), Color.rgb(96, 125, 139), Color.rgb(117, 117, 117), Color.rgb(238, 238, 238)
        };
        final int[] selectedPaletteIndex = {-1};
        for (int i = 0; i < paletteColours.length; i++) {
            if ((paletteColours[i] & 0xFFFFFF) == (initial & 0xFFFFFF)) {
                selectedPaletteIndex[0] = i;
                break;
            }
        }

        LinearLayout panel = dialogBox();
        TextView help = text("Tap a colour below, or fine-tune it with the sliders.", 13, false, MUTED);
        help.setPadding(0, 0, 0, dp(10));
        panel.addView(help);

        TextView preview = text("Colour preview", 16, true, CHARCOAL);
        preview.setGravity(Gravity.CENTER);
        preview.setMinHeight(dp(68));
        panel.addView(preview, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(68)));
        panel.addView(space(dp(10)));

        SeekBar hue = new SeekBar(this);
        hue.setMax(360);
        hue.setProgress(Math.round(hsv[0]));
        SeekBar saturation = new SeekBar(this);
        saturation.setMax(100);
        saturation.setProgress(Math.round(hsv[1] * 100f));
        SeekBar brightness = new SeekBar(this);
        brightness.setMax(100);
        brightness.setProgress(Math.round(hsv[2] * 100f));

        panel.addView(text("Colour palette", 14, true, CHARCOAL));
        TextView paletteHelp = text("Tap a swatch for a quick colour.", 12, false, MUTED);
        paletteHelp.setPadding(0, 0, 0, dp(5));
        panel.addView(paletteHelp);

        ArrayList<Button> paletteButtons = new ArrayList<>();
        final Runnable[] refreshHolder = new Runnable[1];
        for (int row = 0; row < 4; row++) {
            LinearLayout paletteRow = horizontal();
            for (int col = 0; col < 5; col++) {
                final int paletteIndex = row * 5 + col;
                final int swatchColour = paletteColours[paletteIndex];
                Button swatch = new Button(this);
                swatch.setAllCaps(false);
                swatch.setTextSize(18);
                swatch.setTextColor(contrastText(swatchColour));
                swatch.setMinWidth(0);
                swatch.setMinimumWidth(0);
                swatch.setMinHeight(0);
                swatch.setMinimumHeight(0);
                LinearLayout.LayoutParams swatchParams = new LinearLayout.LayoutParams(0, dp(42), 1f);
                swatchParams.setMargins(dp(2), dp(2), dp(2), dp(2));
                swatch.setLayoutParams(swatchParams);
                swatch.setOnClickListener(v -> {
                    selectedPaletteIndex[0] = paletteIndex;
                    Color.colorToHSV(swatchColour, hsv);
                    hue.setProgress(Math.round(hsv[0]));
                    saturation.setProgress(Math.round(hsv[1] * 100f));
                    brightness.setProgress(Math.round(hsv[2] * 100f));
                    if (refreshHolder[0] != null) refreshHolder[0].run();
                });
                paletteButtons.add(swatch);
                paletteRow.addView(swatch);
            }
            panel.addView(paletteRow);
        }

        panel.addView(space(dp(8)));
        panel.addView(text("Custom colour", 14, true, CHARCOAL));
        panel.addView(text("Hue", 13, true, CHARCOAL));
        panel.addView(hue);
        panel.addView(text("Colour strength", 13, true, CHARCOAL));
        panel.addView(saturation);
        panel.addView(text("Brightness", 13, true, CHARCOAL));
        panel.addView(brightness);

        Runnable refresh = () -> {
            hsv[0] = hue.getProgress();
            hsv[1] = saturation.getProgress() / 100f;
            hsv[2] = brightness.getProgress() / 100f;
            int colour = selectedPaletteIndex[0] >= 0 ? paletteColours[selectedPaletteIndex[0]] : Color.HSVToColor(hsv);
            preview.setTextColor(contrastText(colour));
            preview.setBackground(rounded(colour, colour, 14));
            for (int i = 0; i < paletteButtons.size(); i++) {
                Button swatch = paletteButtons.get(i);
                int swatchColour = paletteColours[i];
                boolean selected = i == selectedPaletteIndex[0];
                swatch.setText(selected ? "Selected" : "");
                swatch.setTextSize(selected ? 9 : 18);
                swatch.setTextColor(contrastText(swatchColour));
                swatch.setBackground(rounded(swatchColour, selected ? contrastText(swatchColour) : swatchColour, 10));
            }
        };
        refreshHolder[0] = refresh;
        refresh.run();

        SeekBar.OnSeekBarChangeListener listener = new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (fromUser) selectedPaletteIndex[0] = -1;
                refresh.run();
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) { }
            @Override public void onStopTrackingTouch(SeekBar seekBar) { }
        };
        hue.setOnSeekBarChangeListener(listener);
        saturation.setOnSeekBarChangeListener(listener);
        brightness.setOnSeekBarChangeListener(listener);

        new AlertDialog.Builder(this)
                .setTitle(title)
                .setView(panel)
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Use colour", (dialog, which) -> {
                    int colour = selectedPaletteIndex[0] >= 0 ? paletteColours[selectedPaletteIndex[0]] : Color.HSVToColor(hsv);
                    onPicked.accept(colourToHex(colour));
                })
                .show();
    }

    private void showBackup() {'''
text, n = picker_pattern.subn(new_picker, text, count=1)
if n != 1:
    raise SystemExit('showColourPicker method not found')

text = text.replace('"0.13.3"', '"0.13.4"')
main.write_text(text)

g = gradle.read_text()
g, count_code = re.subn(r'(?m)^\s*versionCode\s+133\s*$', '        versionCode 134', g, count=1)
g, count_name = re.subn(r"(?m)^\s*versionName\s+'0\.13\.3'\s*$", "        versionName '0.13.4'", g, count=1)
if count_code != 1 or count_name != 1:
    raise SystemExit(f'Version bump failed: code={count_code}, name={count_name}')
gradle.write_text(g)

print('Applied v0.13.4 event Actions button and colour palette')
