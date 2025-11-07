#!/bin/bash
# Create simple colored PNG icons

for dir in hdpi mdpi xhdpi xxhdpi xxxhdpi; do
    # Create a simple 48x48 colored square as placeholder icon
    convert -size 48x48 xc:#6200EE "/workspace/FakeModMenu/app/src/main/res/mipmap-$dir/ic_launcher.png" 2>/dev/null || {
        # If ImageMagick not available, create XML drawable instead
        continue
    }
    cp "/workspace/FakeModMenu/app/src/main/res/mipmap-$dir/ic_launcher.png" "/workspace/FakeModMenu/app/src/main/res/mipmap-$dir/ic_launcher_round.png"
done

echo "Icons created (if ImageMagick available)"
