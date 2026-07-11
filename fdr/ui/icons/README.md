# Application Icons

This directory contains all icon files for the Flight Data Recorder application.

## Icon Files

- `icon.svg` - Source vector icon (edit this to change the application icon)
- `icon.png` - 512x512 PNG version (used as fallback)
- `icon_*.png` - Various sizes for different use cases
- `icon.ico` - Windows icon file (contains multiple sizes)
- `icon.icns` - macOS icon file

## Quick Start

To generate all icon resources for local testing, run:
```bash
cd fdr/ui
python generate_resources.py
```

This will:
1. Generate all PNG sizes from the SVG source
2. Create ICO (Windows) and ICNS (macOS) files
3. Compile the Qt resources file

## Manual Icon Generation

If you prefer to generate icons manually using ImageMagick:

1. Edit `icon.svg` with your preferred vector graphics editor (Inkscape, Adobe Illustrator, etc.)
2. Regenerate all icon formats:
   ```bash
   # Generate PNG files at different sizes
   convert -background none -density 300 icon.svg -resize 16x16 icon_16x16.png
   convert -background none -density 300 icon.svg -resize 32x32 icon_32x32.png
   convert -background none -density 300 icon.svg -resize 64x64 icon_64x64.png
   convert -background none -density 300 icon.svg -resize 128x128 icon_128x128.png
   convert -background none -density 300 icon.svg -resize 256x256 icon_256x256.png
   convert -background none -density 300 icon.svg -resize 512x512 icon_512x512.png
   
   # Generate ICO file for Windows
   convert icon_16x16.png icon_32x32.png icon_64x64.png icon_128x128.png icon_256x256.png -colors 256 icon.ico
   
   # Generate ICNS file for macOS
   convert icon_512x512.png icon_256x256.png icon_128x128.png icon_64x64.png icon_32x32.png icon_16x16.png -colors 256 icon.icns
   
   # Copy 512x512 as default PNG
   cp icon_512x512.png icon.png
   ```

3. Compile Qt resources:
   ```bash
   pyside6-rcc -o resources_rc.py resources.qrc
   ```

4. The Qt resource file (`resources.qrc`) will automatically include all icons
5. During the build process, `resources.qrc` is compiled to `resources_rc.py`

## Current Icon Design

The current icon features:
- A dark blue circle background (#1e3a8a)
- A white stylized airplane
- Simple, clean design suitable for an aviation application

You can replace this with your own design by editing `icon.svg` and regenerating the other formats.

## Build Integration

The GitHub Actions workflow automatically:
1. Compiles `resources.qrc` to `resources_rc.py` using `pyside6-rcc`
2. Uses the appropriate icon format for each platform:
   - Windows: `icon.ico`
   - macOS: `icon.icns`
   - Linux: `icon.png`
