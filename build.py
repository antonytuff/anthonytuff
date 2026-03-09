#!/usr/bin/env python3
"""Static site builder for hackerblog - converts markdown to themed HTML."""

import os
import re
import shutil
import markdown
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "output"

SITE_NAME = "anthonytuff"

ASCII_BANNER = r"""
 _   _    _    ____ _  _______ ____    ____  _     ___   ____
| | | |  / \  / ___| |/ / ____|  _ \  | __ )| |   / _ \ / ___|
| |_| | / _ \| |   | ' /|  _| | |_) | |  _ \| |  | | | | |  _
|  _  |/ ___ \ |___| . \| |___|  _ <  | |_) | |__| |_| | |_| |
|_| |_/_/   \_\____|_|\_\_____|_| \_\ |____/|_____\___/ \____|
"""


def parse_frontmatter(text):
    """Extract YAML-like frontmatter and body from markdown."""
    meta = {}
    body = text
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if match:
        for line in match.group(1).strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip().strip('"\'')
        body = match.group(2)
    return meta, body


def render_template(template_name, **kwargs):
    """Render an HTML template with variable substitution."""
    tmpl = (TEMPLATES / template_name).read_text()
    for key, val in kwargs.items():
        tmpl = tmpl.replace('{{' + key + '}}', str(val))
    # Clean any remaining template vars
    tmpl = re.sub(r'\{\{[^}]+\}\}', '', tmpl)
    return tmpl


def md_to_html(text):
    """Convert markdown to HTML with extensions."""
    return markdown.markdown(text, extensions=['tables', 'fenced_code', 'codehilite', 'toc'])


def build_post(md_path, section, root=""):
    """Build a single post page and return its metadata."""
    text = md_path.read_text()
    meta, body = parse_frontmatter(text)
    html_body = md_to_html(body)

    back_url = f"{root}{section}.html"
    back_label = "blog" if section == "blog" else "writeups"

    difficulty_badge = ""
    if meta.get("difficulty"):
        d = meta["difficulty"]
        difficulty_badge = f' <span class="difficulty {d}">{d.upper()}</span>'

    article = f"""
    <a href="{back_url}" class="back-link">back to {back_label}</a>
    <article class="article-content">
      <h1>{meta.get('title', 'Untitled')}{difficulty_badge}</h1>
      <div class="article-meta">
        <span class="date">{meta.get('date', '')}</span>
      </div>
      {html_body}
    </article>
    """

    nav_active = {f"nav_{section}": "active"}
    page = render_template("base.html",
        title=meta.get("title", "Untitled"),
        site_name=SITE_NAME,
        description=meta.get("description", ""),
        root=root,
        content=article,
        **nav_active
    )

    slug = md_path.stem
    out_dir = OUTPUT / section
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{slug}.html").write_text(page)

    meta["slug"] = slug
    meta["url"] = f"{section}/{slug}.html"
    return meta


def build_listing(posts, section, title, description):
    """Build a listing page for blog or writeups."""
    posts_sorted = sorted(posts, key=lambda p: p.get("date", ""), reverse=True)

    cards = []
    for p in posts_sorted:
        tags_html = ""
        if p.get("tags"):
            for tag in p["tags"].split(","):
                tag = tag.strip()
                cls = "htb" if tag == "htb" else "ctf" if tag == "ctf" else "red" if tag in ("red-team", "exploit") else ""
                tags_html += f'<span class="tag {cls}">{tag}</span>'

        diff_html = ""
        if p.get("difficulty"):
            d = p["difficulty"]
            diff_html = f'<span class="difficulty {d}">{d.upper()}</span>'

        cards.append(f"""
        <a href="{p['url']}" class="post-card">
          <div class="meta">
            <span class="date">{p.get('date', '')}</span>
            {tags_html} {diff_html}
          </div>
          <h2>{p.get('title', 'Untitled')}</h2>
          <p>{p.get('description', '')}</p>
        </a>
        """)

    content = f"""
    <div class="section-header">
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
    <div class="post-list">
      {''.join(cards) if cards else '<p style="color:var(--text-dim)">No posts yet. Add .md files to content/{section}/ and rebuild.</p>'}
    </div>
    """

    nav_active = {f"nav_{section}": "active"}
    page = render_template("base.html",
        title=title,
        site_name=SITE_NAME,
        description=description,
        root="",
        content=content,
        **nav_active
    )
    (OUTPUT / f"{section}.html").write_text(page)


def build_resume():
    """Build the resume page."""
    resume_path = CONTENT / "resume.md"
    if not resume_path.exists():
        return

    text = resume_path.read_text()
    meta, body = parse_frontmatter(text)
    html_body = md_to_html(body)

    content = f"""
    <article class="article-content resume-section">
      <h1>{meta.get('title', 'Resume')}</h1>
      {html_body}
    </article>
    """

    page = render_template("base.html",
        title="Resume",
        site_name=SITE_NAME,
        description=meta.get("description", ""),
        root="",
        content=content,
        nav_resume="active"
    )
    (OUTPUT / "resume.html").write_text(page)


def build_index(blog_posts, writeup_posts):
    """Build the homepage."""
    recent = sorted(blog_posts + writeup_posts, key=lambda p: p.get("date", ""), reverse=True)[:5]

    cards = []
    for p in recent:
        cards.append(f"""
        <a href="{p['url']}" class="post-card">
          <div class="meta"><span class="date">{p.get('date', '')}</span></div>
          <h2>{p.get('title', 'Untitled')}</h2>
          <p>{p.get('description', '')}</p>
        </a>
        """)

    content = f"""
    <div class="hero">
      <pre class="ascii-banner">{ASCII_BANNER}</pre>
      <p class="subtitle">Cybersecurity blog, HackTheBox writeups, and more.</p>
      <div class="links">
        <a href="blog.html">Blog</a>
        <a href="writeups.html">Writeups</a>
        <a href="resume.html">Resume</a>
      </div>
    </div>
    <div class="section-header">
      <h1>latest</h1>
    </div>
    <div class="post-list">
      {''.join(cards) if cards else '<p style="color:var(--text-dim)">No posts yet.</p>'}
    </div>
    """

    page = render_template("base.html",
        title="Home",
        site_name=SITE_NAME,
        description="Cybersecurity blog and HTB writeups",
        root="",
        content=content
    )
    (OUTPUT / "index.html").write_text(page)


def build():
    """Main build function."""
    # Clean and recreate output
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    # Copy static files
    if STATIC.exists():
        shutil.copytree(STATIC, OUTPUT / "static")

    # Build blog posts
    blog_posts = []
    blog_dir = CONTENT / "blog"
    if blog_dir.exists():
        for md in blog_dir.glob("*.md"):
            meta = build_post(md, "blog", root="../")
            blog_posts.append(meta)

    # Build writeup posts
    writeup_posts = []
    writeup_dir = CONTENT / "writeups"
    if writeup_dir.exists():
        for md in writeup_dir.glob("*.md"):
            meta = build_post(md, "writeups", root="../")
            writeup_posts.append(meta)

    # Build listing pages
    build_listing(blog_posts, "blog", "cat /blog/*", "Cybersecurity articles, tutorials, and research")
    build_listing(writeup_posts, "writeups", "cat /writeups/*", "HackTheBox and CTF writeups")

    # Build resume
    build_resume()

    # Build index
    build_index(blog_posts, writeup_posts)

    print(f"[+] Built {len(blog_posts)} blog posts")
    print(f"[+] Built {len(writeup_posts)} writeups")
    print(f"[+] Output: {OUTPUT}")


def serve(port=8000):
    """Serve the output directory for local preview."""
    os.chdir(OUTPUT)
    handler = SimpleHTTPRequestHandler
    server = HTTPServer(("0.0.0.0", port), handler)
    print(f"[*] Serving at http://localhost:{port}")
    print("[*] Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopped")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        build()
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8000)
    else:
        build()
