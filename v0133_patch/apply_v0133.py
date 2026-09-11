#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'MHFEventShare-v0.13.2')
main = root / 'app/src/main/java/uk/co/mentalhealthfriends/eventshare/MainActivity.java'
gradle = root / 'app/build.gradle'

text = main.read_text()

# SeekBar is used by the new visual HSV colour picker.
if 'import android.widget.SeekBar;' not in text:
    anchor = 'import android.widget.ScrollView;\n'
    if anchor not in text:
        raise SystemExit('ScrollView import anchor not found')
    text = text.replace(anchor, anchor + 'import android.widget.SeekBar;\n', 1)

branding_pattern = re.compile(
    r'        addHeading\("Branding & colours",\s*"Use a preset or enter normal #RRGGBB colour values\."\);\n'
    r'.*?'
    r'        body\.addView\(background\);\n',
    re.S,
)

branding_replacement = '''        addHeading("Branding & colours", "Choose colours visually — no colour codes needed.");
        final String[] accentValue = { validColorHex(draft.accentColor, "#F7C928") };
        final String[] backgroundValue = { validColorHex(draft.backgroundColor, "#FFFCEF") };
        body.addView(colourSettingCard(
                "Header & accent colour",
                "Used for the top bar, primary buttons and highlights.",
                accentValue));
        body.addView(colourSettingCard(
                "Page background colour",
                "Used behind cards and page content.",
                backgroundValue));
'''

text, n = branding_pattern.subn(branding_replacement, text, count=1)
if n != 1:
    # Tolerate later wording changes but still replace the legacy input/preset block by anchors.
    start = text.find('        addHeading("Branding & colours"')
    end_anchor = '        body.addView(background);\n'
    end = text.find(end_anchor, start)
    if start < 0 or end < 0:
        raise SystemExit('Branding colour block not found')
    end += len(end_anchor)
    text = text[:start] + branding_replacement + text[end:]

old_accent = '            draft.accentColor = validColorHex(clean(accent), "#F7C928");'
old_background = '            draft.backgroundColor = validColorHex(clean(background), "#FFFCEF");'
if old_accent not in text or old_background not in text:
    raise SystemExit('Settings save colour assignments not found')
text = text.replace(old_accent, '            draft.accentColor = validColorHex(accentValue[0], "#F7C928");', 1)
text = text.replace(old_background, '            draft.backgroundColor = validColorHex(backgroundValue[0], "#FFFCEF");', 1)

helper_anchor = '    private void showBackup() {'
if helper_anchor not in text:
    raise SystemExit('showBackup helper anchor not found')
if 'private LinearLayout colourSettingCard(' not in text:
    helpers = r'''    private LinearLayout colourSettingCard(String title, String description, String[] valueHolder) {
        LinearLayout card = card();
        card.addView(text(title, 17, true, CHARCOAL));
        card.addView(text(description, 13, false, MUTED));
        card.addView(space(dp(9)));

        TextView preview = text("Current colour — tap to change", 14, true, CHARCOAL);
        preview.setGravity(Gravity.CENTER);
        preview.setMinHeight(dp(58));
        LinearLayout.LayoutParams previewParams = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(58));
        previewParams.setMargins(0, 0, 0, dp(8));
        preview.setLayoutParams(previewParams);
        updateColourPreview(preview, valueHolder[0]);
        preview.setOnClickListener(v -> showColourPicker(title, valueHolder[0], chosen -> {
            valueHolder[0] = chosen;
            updateColourPreview(preview, chosen);
        }));
        card.addView(preview);

        Button choose = secondaryButton("Choose colour", null);
        choose.setOnClickListener(v -> showColourPicker(title, valueHolder[0], chosen -> {
            valueHolder[0] = chosen;
            updateColourPreview(preview, chosen);
        }));
        card.addView(choose);
        return card;
    }

    private void updateColourPreview(TextView preview, String hex) {
        int colour = parseThemeColour(hex, YELLOW);
        preview.setTextColor(contrastText(colour));
        preview.setBackground(rounded(colour, colour, 14));
    }

    private int parseThemeColour(String hex, int fallback) {
        try {
            return Color.parseColor(validColorHex(hex, colourToHex(fallback)));
        } catch (Exception ignored) {
            return fallback;
        }
    }

    private String colourToHex(int colour) {
        return String.format(Locale.UK, "#%06X", 0xFFFFFF & colour);
    }

    private void showColourPicker(String title, String initialHex, java.util.function.Consumer<String> onPicked) {
        int initial = parseThemeColour(initialHex, YELLOW);
        final float[] hsv = new float[3];
        Color.colorToHSV(initial, hsv);

        LinearLayout panel = dialogBox();
        TextView help = text("Move the sliders until the preview looks right.", 13, false, MUTED);
        help.setPadding(0, 0, 0, dp(12));
        panel.addView(help);

        TextView preview = text("Colour preview", 16, true, CHARCOAL);
        preview.setGravity(Gravity.CENTER);
        preview.setMinHeight(dp(72));
        panel.addView(preview, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(72)));
        panel.addView(space(dp(12)));

        TextView hueValue = text("Hue", 13, true, CHARCOAL);
        panel.addView(hueValue);
        SeekBar hue = new SeekBar(this);
        hue.setMax(360);
        hue.setProgress(Math.round(hsv[0]));
        panel.addView(hue);

        TextView saturationValue = text("Colour strength", 13, true, CHARCOAL);
        panel.addView(saturationValue);
        SeekBar saturation = new SeekBar(this);
        saturation.setMax(100);
        saturation.setProgress(Math.round(hsv[1] * 100f));
        panel.addView(saturation);

        TextView brightnessValue = text("Brightness", 13, true, CHARCOAL);
        panel.addView(brightnessValue);
        SeekBar brightness = new SeekBar(this);
        brightness.setMax(100);
        brightness.setProgress(Math.round(hsv[2] * 100f));
        panel.addView(brightness);

        Runnable refresh = () -> {
            hsv[0] = hue.getProgress();
            hsv[1] = saturation.getProgress() / 100f;
            hsv[2] = brightness.getProgress() / 100f;
            int colour = Color.HSVToColor(hsv);
            preview.setTextColor(contrastText(colour));
            preview.setBackground(rounded(colour, colour, 14));
        };
        refresh.run();

        SeekBar.OnSeekBarChangeListener listener = new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) { refresh.run(); }
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
                    int colour = Color.HSVToColor(hsv);
                    onPicked.accept(colourToHex(colour));
                })
                .show();
    }

'''
    text = text.replace(helper_anchor, helpers + helper_anchor, 1)

# Bump any user-visible in-code version string if a later branch introduced one.
text = text.replace('"0.13.2"', '"0.13.3"')
main.write_text(text)

g = gradle.read_text()
g, count_code = re.subn(r'(?m)^\s*versionCode\s+132\s*$', '        versionCode 133', g, count=1)
g, count_name = re.subn(r"(?m)^\s*versionName\s+'0\.13\.2'\s*$", "        versionName '0.13.3'", g, count=1)
if count_code != 1 or count_name != 1:
    raise SystemExit(f'Version bump failed: code={count_code}, name={count_name}')
gradle.write_text(g)

print('Applied v0.13.3 visual colour picker and version bump')
