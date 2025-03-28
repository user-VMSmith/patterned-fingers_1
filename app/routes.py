from flask import render_template, request, redirect, url_for
from app import app

# in-memory message + pattern storage
patterns = []  # messages
defined_patterns = []  # patterns for b-lang, f-lang, t-lang

@app.route("/")
def index():
    return redirect(url_for("view_patterns"))

@app.route("/patterns", methods=["GET", "POST"])
def view_patterns():
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "message":
            # handle chat message
            title = request.form.get("title", "").strip()
            speaker = request.form.get("speaker", "").strip()
            language = request.form.get("language", "").strip()
            body = request.form.get("body", "").strip()

            if title and speaker and language and body:
                patterns.append({
                    "title": title,
                    "speaker": speaker,
                    "language": language,
                    "body": body
                })

        elif form_type == "pattern":
            # handle new defined pattern
            title = request.form.get("title", "").strip()
            definition = request.form.get("definition", "").strip()
            language = request.form.get("language", "").strip()

            if title and definition and language:
                defined_patterns.append({
                    "title": title,
                    "definition": definition,
                    "language": language
                })

        return redirect(url_for("view_patterns"))

    return render_template(
        "patterns.html",
        patterns=patterns,
        defined_patterns=defined_patterns
    )

@app.template_filter('mark_patterns')
def mark_patterns(text):
    import re
    from markupsafe import Markup

    # use title → language map
    pattern_map = {p['title']: p['language'] for p in defined_patterns}
    if not pattern_map:
        return text

    # escape titles for regex
    titles = [re.escape(title) for title in pattern_map.keys()]
    pattern = re.compile(r'\b(' + '|'.join(titles) + r')\b', re.IGNORECASE)

    emoji_for_lang = {
        'BENJA': '🧠',
        'TEMP-FAMILECT': '🌱',
        'TORI': '🐚'
    }

    def replacer(match):
        raw_title = match.group(0)
        # find the actual pattern title used (case-insensitive match)
        title = next((t for t in pattern_map if t.lower() == raw_title.lower()), raw_title)
        lang = pattern_map.get(title, '')
        emoji = emoji_for_lang.get(lang, '❔')
        return f'<span class="pattern-ref">{emoji} {title}</span>'

    result = pattern.sub(replacer, text)
    return Markup(result)


