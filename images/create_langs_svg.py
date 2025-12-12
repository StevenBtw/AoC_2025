import os
import json
import yaml
import requests
import math
import cairo
from pathlib import Path
from collections import defaultdict

LANGUAGE_YML_URL = "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"
COLORS = {
    'dark': {
        'background': [0, 0, 0, 0],
        'gutter': [52/255, 57/255, 65/255],
        'text': [201/255, 209/255, 217/255],
        'percentage': [139/255, 148/255, 158/255],
    },
    'light': {
        'background': [0, 0, 0, 0],
        'gutter': [239/255, 241/255, 243/255],
        'text': [36/255, 41/255, 47/255],
        'percentage': [87/255, 96/255, 106/255],
    }
}

# Common file extensions to language mappings
EXTENSION_TO_LANGUAGE = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.h': 'C',
    '.hpp': 'C++',
    '.rs': 'Rust',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.sh': 'Bash',
    '.bash': 'Bash',
    '.sql': 'SQL',
    '.xlsx': 'Excel',
    '.xls': 'Excel',
    '.r': 'R',
    '.R': 'R',
    '.m': 'MATLAB',
    '.jl': 'Julia',
    '.cu': 'Cuda',
    '.wgsl': 'WGSL',
    '.md': 'Markdown',
    '.json': 'JSON',
    '.xml': 'XML',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.toml': 'TOML',
}

# Directories to ignore
IGNORE_DIRS = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 
               'dist', 'build', '.idea', '.vscode', 'target', 'assets', 'images'}

def fetch_langs() -> str:
    res = requests.get(LANGUAGE_YML_URL)
    return res.text

def get_langs() -> str:
    try:
        with open(".langs.yml") as f:
            return f.read()
    except:
        langs = fetch_langs()
        with open(".langs.yml", "w") as f:
            f.write(langs)
        return langs

def analyze_repository(root_path: str) -> dict:
    """Analyze the repository and count bytes per language"""
    language_bytes = defaultdict(int)
    
    # Languages to exclude from the final report
    EXCLUDED_LANGUAGES = {'YAML', 'TOML', 'Markdown', 'JSON', 'HTML'}
    
    for root, dirs, files in os.walk(root_path):
        # Remove ignored directories from the search
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            ext = Path(file).suffix.lower()
            
            if ext in EXTENSION_TO_LANGUAGE:
                try:
                    size = os.path.getsize(file_path)
                    language = EXTENSION_TO_LANGUAGE[ext]
                    
                    # Apply Excel overhead reduction (xlsx/xls have significant XML overhead)
                    if language == 'Excel':
                        size = int(size * 0.10)  # Reduce to ~10% to account for compression overhead
                    
                    language_bytes[language] += size
                except:
                    continue
    
    # Filter out excluded languages
    language_bytes = {lang: size for lang, size in language_bytes.items() 
                      if lang not in EXCLUDED_LANGUAGES}
    
    # Calculate percentages (totals add to 100% after exclusions)
    total_bytes = sum(language_bytes.values())
    if total_bytes == 0:
        return {}
    
    result = {
        lang: {
            'size': size,
            'percentage': (size / total_bytes) * 100
        }
        for lang, size in language_bytes.items()
    }
    
    return result

def set_color(ctx, color: list[float]):
    if len(color) == 4:
        ctx.set_source_rgba(*color)
    elif len(color) == 3:
        ctx.set_source_rgb(*color)
    elif len(color) == 1:
        ctx.set_source_rgb(color[0], color[0], color[0])
    else:
        raise ValueError("color array isn't of length 4, 3, 2 or 1")

def hex_to_rgb(code: str) -> list[float]:
    if code is None:
        return [0.5, 0.5, 0.5]  # Default gray color
    hex_code = code.lstrip("#")
    return [int(hex_code[i:i+2], base=16) / 255 for i in range(0, len(hex_code), 2)]

def render(path: str, colors: dict, data: dict):
    # SVG generation
    WIDTH, HEIGHT = 410, 500

    HALF_PI = 0.5 * math.pi
    TWO_PI = 2 * math.pi

    GUTTER_WIDTH = 0
    BAR_RADIUS = 5
    PADDING = (5, 20)
    FONT_SIZE = 14
    LINE_HEIGHT = 24
    DOT_RADIUS = 4
    DOT_OFFSET = 4
    DOT_MARGIN = 8
    FONT = 'Arial'
    SPACING = 30

    y_len = PADDING[1] * 2 + 2 * BAR_RADIUS
    x_len = PADDING[0] * 3 + DOT_RADIUS * 2 + DOT_MARGIN

    # Compute canvas size
    surf_sample = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx_sample = cairo.Context(surf_sample)

    ctx_sample.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx_sample.set_font_size(FONT_SIZE)

    for language in data:
        lang_length = ctx_sample.text_extents(language + (" %.2f%%" % (data[language]['fac'] * 100)))[2] + SPACING + 2 * DOT_RADIUS + DOT_MARGIN

        if x_len + lang_length >= WIDTH:
            x_len = PADDING[0] * 4 + 2 * DOT_RADIUS
            y_len += LINE_HEIGHT

        x_len += lang_length

    # Create context with correct size
    surface = cairo.SVGSurface(path, WIDTH, y_len - LINE_HEIGHT)
    ctx = cairo.Context(surface)

    # Background
    ctx.rectangle(0, 0, WIDTH, y_len - LINE_HEIGHT)
    set_color(ctx, colors['background'])
    ctx.fill()

    # Bar
    x = PADDING[0]

    ctx.arc(x + BAR_RADIUS, PADDING[1] + BAR_RADIUS, BAR_RADIUS, HALF_PI, -HALF_PI)
    ctx.arc(WIDTH - PADDING[0] - BAR_RADIUS, PADDING[1] + BAR_RADIUS, BAR_RADIUS, -HALF_PI, HALF_PI)
    ctx.clip()

    last_language = list(data.keys())[-1] if data else None
    
    # Colored rectangles
    for language in data:
        width = data[language]['fac'] * (WIDTH - 2 * PADDING[0])

        set_color(ctx, data[language]['color'])
        ctx.rectangle(x, PADDING[1], width, BAR_RADIUS * 2)
        ctx.fill()

        x += width

        if language != last_language and GUTTER_WIDTH > 0:
            set_color(ctx, colors['gutter'])
            ctx.rectangle(x - GUTTER_WIDTH, PADDING[1], GUTTER_WIDTH, BAR_RADIUS * 2)
            ctx.fill()

    ctx.reset_clip()

    # Text and colored dots
    text_x = PADDING[0] * 3 + DOT_RADIUS * 2 + DOT_MARGIN
    text_y = PADDING[1] * 2 + BAR_RADIUS * 2

    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)
    
    for language in data:
        percentage = "%.2f%%" % (data[language]['fac'] * 100)
        label_width = ctx.text_extents(language + " ")[2]
        percent_width = ctx.text_extents(percentage)[2]
        text_width = label_width + percent_width + SPACING + 2 * DOT_RADIUS + DOT_MARGIN

        if text_x + text_width >= WIDTH:
            text_x = PADDING[0] * 3 + DOT_RADIUS * 2 + DOT_MARGIN
            text_y += LINE_HEIGHT

        # Dot
        set_color(ctx, data[language]['color'])
        ctx.arc(text_x - DOT_RADIUS * 2 - DOT_MARGIN, text_y - DOT_OFFSET, DOT_RADIUS, 0, TWO_PI)
        ctx.fill()

        # Draw the text for that language
        set_color(ctx, colors['text'])
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(FONT_SIZE)

        ctx.move_to(text_x, text_y)
        ctx.show_text(language + " ")

        set_color(ctx, colors['percentage'])
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(FONT_SIZE)
        ctx.show_text(percentage)

        text_x += text_width

    surface.finish()

def main():
    # Get repository root (parent of images directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print(f"Analyzing repository at: {repo_root}")
    
    # Analyze the repository
    analysis_result = analyze_repository(str(repo_root))
    
    if not analysis_result:
        print("No supported language files found!")
        return
    
    print(f"\nLanguages found:")
    for lang, info in sorted(analysis_result.items(), key=lambda x: x[1]['size'], reverse=True):
        print(f"  {lang}: {info['size']} bytes ({info['percentage']:.2f}%)")
    
    # Load language color data
    langs = yaml.safe_load(get_langs())
    
    # Prepare data for rendering
    data = {}
    for lang in sorted(analysis_result, reverse=True, key=lambda k: analysis_result[k]["size"]):
        color = hex_to_rgb(langs.get(lang, {}).get('color'))
        data[lang] = {
            'fac': float(analysis_result[lang]['percentage']) / 100.0,
            'color': color
        }

    # Render SVGs
    print("\nGenerating SVG files...")
    render("langs_dark.svg", COLORS['dark'], data)
    render("langs_light.svg", COLORS['light'], data)
    
    print("✓ Generated langs_dark.svg")
    print("✓ Generated langs_light.svg")
if __name__ == "__main__":
    main()

