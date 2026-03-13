#!/usr/bin/env python3
"""Static site builder for anthonytuff - converts markdown to themed HTML."""

import os
import re
import shutil
import markdown
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import json

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "output"

SITE_NAME = "anthonytuff"

ASCII_BANNER = r"""
    ___    _   ____________  ____  _   ____  __________  ____________
   /   |  / | / /_  __/ / / / __ \/ | / /\ \/ /_  __/ / / / ____/ __/
  / /| | /  |/ / / / / /_/ / / / /  |/ /  \  / / / / / / / /_  / /_
 / ___ |/ /|  / / / / __  / /_/ / /|  /   / / / / / /_/ / __/ / __/
/_/  |_/_/ |_/ /_/ /_/ /_/\____/_/ |_/   /_/ /_/  \____/_/   /_/
"""

# All available tag categories for filter UI
ALL_TAGS = [
    "all", "recon", "tools", "web", "exploit", "privesc",
    "htb", "ctf", "linux", "windows", "osint",
    "forensics", "crypto", "reverse", "red-team",
    "networking", "malware", "scripting", "cloud"
]

SOCIAL_ICONS_HTML = """
<div class="social-icons">
  <a href="https://github.com/antonytuff" target="_blank" title="GitHub">
    <svg viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
  </a>
  <a href="https://linkedin.com/in/anthony-mabi-9bb18b174" target="_blank" title="LinkedIn">
    <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
  </a>
  <a href="mailto:inert.fingers-0m@icloud.com" title="Email">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
  </a>
</div>
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
    tmpl = re.sub(r'\{\{[^}]+\}\}', '', tmpl)
    return tmpl


def md_to_html(text):
    """Convert markdown to HTML with extensions."""
    return markdown.markdown(text, extensions=['tables', 'fenced_code', 'codehilite', 'toc'])


def get_tag_class(tag):
    """Return CSS class for a given tag."""
    tag = tag.strip().lower()
    colored = ['htb', 'ctf', 'red-team', 'exploit', 'linux', 'windows',
               'web', 'osint', 'forensics', 'crypto', 'privesc', 'reverse']
    return tag if tag in colored else ''


def build_tag_html(tags_str):
    """Build tag span HTML from comma-separated tags string."""
    if not tags_str:
        return ""
    html = ""
    for tag in tags_str.split(","):
        tag = tag.strip()
        cls = get_tag_class(tag)
        html += f'<span class="tag {cls}">{tag}</span>'
    return html


def build_sidebar_html(all_posts, current_tags, root):
    """Build sidebar with categories and tags for blog/writeup post pages."""
    # Collect categories (sections)
    blog_count = sum(1 for p in all_posts if 'blog/' in p.get('url', ''))
    writeup_count = sum(1 for p in all_posts if 'writeups/' in p.get('url', ''))

    # Collect all tags with counts
    tag_counts = {}
    for p in all_posts:
        if p.get("tags"):
            for t in p["tags"].split(","):
                t = t.strip().lower()
                tag_counts[t] = tag_counts.get(t, 0) + 1

    # Recent posts
    recent = sorted(all_posts, key=lambda p: p.get("date", ""), reverse=True)[:5]
    recent_html = ""
    for p in recent:
        recent_html += f'<a href="{root}{p["url"]}" class="sidebar-post">{p.get("title", "Untitled")}</a>\n'

    # Tags cloud
    tags_html = ""
    for tag in sorted(tag_counts.keys()):
        cls = get_tag_class(tag)
        active = "active" if tag in current_tags else ""
        tags_html += f'<span class="sidebar-tag {cls} {active}">{tag} <span class="tag-count">{tag_counts[tag]}</span></span>\n'

    return f"""
    <aside class="sidebar">
      <div class="sidebar-section">
        <div class="sidebar-title">categories</div>
        <a href="{root}blog.html" class="sidebar-cat">
          <span>Blog</span><span class="cat-count">{blog_count}</span>
        </a>
        <a href="{root}writeups.html" class="sidebar-cat">
          <span>Writeups</span><span class="cat-count">{writeup_count}</span>
        </a>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-title">tags</div>
        <div class="sidebar-tags">{tags_html}</div>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-title">recent posts</div>
        <div class="sidebar-recent">{recent_html}</div>
      </div>
    </aside>
    """


def extract_toc(html_body):
    """Extract headings from HTML and build a table of contents + add IDs."""
    toc_items = []

    def collect_heading(match):
        level = match.group(1)
        attrs = match.group(2)
        content = match.group(3)
        clean = re.sub(r'<[^>]+>', '', content)
        # Get existing id or generate one
        id_match = re.search(r'id="([^"]+)"', attrs)
        slug = id_match.group(1) if id_match else re.sub(r'[^a-z0-9]+', '-', clean.lower()).strip('-')
        toc_items.append((int(level), clean, slug))
        # Ensure id is present
        if not id_match:
            return f'<h{level} id="{slug}"{attrs}>{content}</h{level}>'
        return match.group(0)

    modified_html = re.sub(r'<h([2-4])(\s[^>]*)?>(.+?)</h[2-4]>', collect_heading, html_body)
    return modified_html, toc_items


def build_toc_html(toc_items):
    """Build clickable table of contents HTML."""
    if not toc_items:
        return ""
    html = '<div class="toc">\n'
    html += '  <div class="toc-title">Table of Contents</div>\n'
    html += '  <nav class="toc-nav">\n'
    for level, text, slug in toc_items:
        indent_class = f"toc-h{level}"
        html += f'    <a href="#{slug}" class="toc-link {indent_class}">{text}</a>\n'
    html += '  </nav>\n</div>\n'
    return html


def build_post(md_path, section, all_posts, root=""):
    """Build a single post page and return its metadata."""
    text = md_path.read_text()
    meta, body = parse_frontmatter(text)
    html_body = md_to_html(body)

    # Add IDs to headings and extract TOC
    html_body, toc_items = extract_toc(html_body)
    toc_html = build_toc_html(toc_items)

    back_url = f"{root}{section}.html"
    back_label = "blog" if section == "blog" else "writeups"

    difficulty_badge = ""
    if meta.get("difficulty"):
        d = meta["difficulty"]
        difficulty_badge = f' <span class="difficulty {d}">{d.upper()}</span>'

    tags_html = build_tag_html(meta.get("tags", ""))
    current_tags = [t.strip().lower() for t in meta.get("tags", "").split(",") if t.strip()]

    sidebar = build_sidebar_html(all_posts, current_tags, root) if all_posts else ""

    # Reading time estimate
    word_count = len(body.split())
    read_time = max(1, round(word_count / 200))

    article = f"""
    <a href="{back_url}" class="back-link">back to {back_label}</a>
    <div class="post-layout">
      <article class="article-content" id="article-body">
        <h1>{meta.get('title', 'Untitled')}{difficulty_badge}</h1>
        <div class="article-meta">
          <span class="date">{meta.get('date', '')}</span>
          <span class="read-time">{read_time} min read</span>
          {tags_html}
        </div>
        <div class="post-search-bar">
          <input type="text" id="post-search" placeholder="Search in this post..." autocomplete="off">
        </div>
        {toc_html}
        <div id="article-text">
        {html_body}
        </div>
      </article>
      {sidebar}
    </div>
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


def collect_used_tags(posts):
    """Get sorted list of unique tags used across posts."""
    tags = set()
    for p in posts:
        if p.get("tags"):
            for t in p["tags"].split(","):
                tags.add(t.strip().lower())
    return sorted(tags)


def build_search_filter_html(posts):
    """Build the search bar and tag filter buttons."""
    used_tags = collect_used_tags(posts)

    tag_buttons = '<button class="tag-filter active" data-tag="all">all</button>\n'
    for tag in used_tags:
        cls = get_tag_class(tag)
        tag_buttons += f'          <button class="tag-filter {cls}" data-tag="{tag}">{tag}</button>\n'

    return f"""
    <div class="search-filter-bar">
      <div class="search-box">
        <input type="text" id="search-input" placeholder="grep -i 'search posts...'" autocomplete="off">
      </div>
      <div class="tag-filters">
        {tag_buttons}
      </div>
    </div>
    """


def build_listing(posts, section, title, description):
    """Build a listing page for blog or writeups."""
    posts_sorted = sorted(posts, key=lambda p: p.get("date", ""), reverse=True)

    search_html = build_search_filter_html(posts_sorted)

    cards = []
    for p in posts_sorted:
        tags_str = p.get("tags", "")
        tags_html = build_tag_html(tags_str)

        diff_html = ""
        if p.get("difficulty"):
            d = p["difficulty"]
            diff_html = f'<span class="difficulty {d}">{d.upper()}</span>'

        cards.append(f"""
        <a href="{p['url']}" class="post-card" data-tags="{tags_str}">
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
    {search_html}
    <div class="post-list">
      {''.join(cards) if cards else '<p style="color:var(--text-dim)">No posts yet. Add .md files to content/' + section + '/ and rebuild.</p>'}
    </div>
    <div class="no-results">
      <p>root@blog:~# No matching posts found.</p>
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
    """Build the resume page with creative layout, badges, links, and CV download."""
    resume_path = CONTENT / "resume.md"
    if not resume_path.exists():
        return

    text = resume_path.read_text()
    meta, body = parse_frontmatter(text)

    # Parse sections from markdown
    sections = {}
    current_section = None
    current_content = []

    for line in body.strip().split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip().lower()
            current_content = []
        else:
            current_content.append(line)
    if current_section:
        sections[current_section] = '\n'.join(current_content)

    # CV download button
    cv_path = meta.get("cv_download", "")
    cv_button = ""
    if cv_path:
        cv_button = f"""
        <a href="{cv_path}" class="cv-download" download>
          <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Download CV
        </a>
        """

    # Resume header
    header_html = f"""
    <div class="resume-header">
      <div>
        <h1>Anthony Tuff</h1>
        <p>{meta.get('description', '')}</p>
      </div>
      {cv_button}
    </div>
    """

    # whoami / about
    whoami_html = ""
    if 'whoami' in sections:
        whoami_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">~$</span> whoami</div>
      <div class="article-content">{md_to_html(sections['whoami'])}</div>
    </div>
    """

    # Skills as styled grid
    skills_html = ""
    if 'skills' in sections:
        items = []
        for line in sections['skills'].strip().split('\n'):
            line = line.strip()
            if line.startswith('- '):
                line = line[2:]
                if '**' in line:
                    parts = line.split('**')
                    label = parts[1] if len(parts) > 1 else ''
                    desc = parts[2].lstrip(':').strip() if len(parts) > 2 else ''
                    items.append(f'<div class="skill-item"><strong>{label}</strong><span>{desc}</span></div>')
                else:
                    items.append(f'<div class="skill-item"><strong>{line}</strong></div>')
        skills_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">&gt;_</span> skills</div>
      <div class="skill-grid">{''.join(items)}</div>
    </div>
    """

    # Certifications as badges
    certs_html = ""
    if 'certifications' in sections:
        badge_map = {
            'ceh': ('CEH', 'EC-Council', 'ceh', 'static/badge-ceh.png'),
            'ewptx': ('eWPTX', 'eLearnSecurity', 'ewptx', 'static/badge-ewptx.png'),
            'crte': ('CRTE', 'Altered Security', 'crte', 'static/badge-crte.png'),
            'crto': ('CRTO', 'Zero Point Security', 'crto', 'static/badge-crto.png'),
            'ctia': ('CTIA', 'EC-Council', 'ctia', 'static/badge-ctia.png'),
            'cnss': ('CNSS', 'ICSI, UK', 'cnss', 'static/badge-cnss.png'),
            'iso 22301': ('CLI', 'Datasec', 'cli', 'static/badge-cli.png'),
            'cscu': ('CSCU', 'EC-Council', 'cscu', 'static/badge-cscu.png'),
            'cei': ('CEI', 'EC-Council', 'cei', 'static/badge-cei.png'),
            'ccna': ('CCNA', 'Cisco', 'ccna', 'static/badge-ccna.png'),
        }
        badges = []
        for line in sections['certifications'].strip().split('\n'):
            line = line.strip()
            if line.startswith('- '):
                cert_text = line[2:].strip()
                verify_url = ''
                if ' | ' in cert_text:
                    cert_text, verify_url = cert_text.rsplit(' | ', 1)
                    verify_url = verify_url.strip()
                icon_cls = 'default'
                short = cert_text[:4]
                issuer = ''
                badge_img = ''
                for key, (abbr, iss, cls, img) in badge_map.items():
                    if key in cert_text.lower():
                        short = abbr
                        issuer = iss
                        icon_cls = cls
                        badge_img = img
                        break
                if badge_img and (ROOT / badge_img).exists():
                    icon_html = f'<img src="{badge_img}" alt="{short}" class="badge-img">'
                else:
                    icon_html = f'<div class="badge-icon {icon_cls}">{short}</div>'
                verify_html = f'<a href="{verify_url}" target="_blank" class="badge-verify">Verify</a>' if verify_url else ''
                badges.append(f"""
                <div class="badge">
                  {icon_html}
                  <div class="badge-info">
                    <span class="badge-name">{cert_text}</span>
                    {f'<span class="badge-issuer">{issuer}</span>' if issuer else ''}
                    {verify_html}
                  </div>
                </div>""")
        certs_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">[*]</span> certifications</div>
      <div class="badge-grid">{''.join(badges)}</div>
    </div>
    """

    # Experience as timeline
    exp_html = ""
    if 'experience' in sections:
        items = []
        current_title = ""
        current_date = ""
        current_bullets = []

        for line in sections['experience'].strip().split('\n'):
            line = line.strip()
            if line.startswith('### '):
                if current_title:
                    bullets = ''.join(f'<li>{b}</li>' for b in current_bullets)
                    items.append(f"""
                    <div class="timeline-item">
                      <h3>{current_title}</h3>
                      <div class="timeline-date">{current_date}</div>
                      <ul>{bullets}</ul>
                    </div>""")
                current_title = line[4:].strip()
                current_date = ""
                current_bullets = []
            elif line.startswith('*') and line.endswith('*'):
                current_date = line.strip('*')
            elif line.startswith('- '):
                current_bullets.append(line[2:])

        if current_title:
            bullets = ''.join(f'<li>{b}</li>' for b in current_bullets)
            items.append(f"""
            <div class="timeline-item">
              <h3>{current_title}</h3>
              <div class="timeline-date">{current_date}</div>
              <ul>{bullets}</ul>
            </div>""")

        exp_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">#!/</span> experience</div>
      <div class="timeline">{''.join(items)}</div>
    </div>
    """

    # Achievements
    ach_html = ""
    if 'achievements' in sections:
        ach_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">[+]</span> achievements</div>
      <div class="article-content">{md_to_html(sections['achievements'])}</div>
    </div>
    """

    # Education
    edu_html = ""
    if 'education' in sections:
        edu_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">0x</span> education</div>
      <div class="article-content">{md_to_html(sections['education'])}</div>
    </div>
    """

    # Links as styled buttons
    links_html = ""
    if 'links' in sections:
        link_items = []
        for line in sections['links'].strip().split('\n'):
            line = line.strip()
            if line.startswith('- '):
                line = line[2:]
                # Parse markdown links
                match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
                if match:
                    label_text = line.split(':')[0].strip() if ':' in line else match.group(1)
                    url = match.group(2)
                    icon_svg = ''
                    ll = label_text.lower()
                    if 'github' in ll:
                        icon_svg = '<svg viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>'
                    elif 'linkedin' in ll:
                        icon_svg = '<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
                    link_items.append(f'<a href="{url}" target="_blank" class="resume-link">{icon_svg} {label_text}</a>')
                elif 'email' in line.lower() or '@' in line:
                    email = line.split(':')[-1].strip() if ':' in line else line
                    link_items.append(f'<a href="mailto:{email}" class="resume-link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg> {email}</a>')

        links_html = f"""
    <div class="resume-block reveal">
      <div class="resume-block-title"><span class="section-icon">@</span> links</div>
      <div class="resume-links">{''.join(link_items)}</div>
    </div>
    """

    content = f"""
    <div class="resume-page">
      {header_html}
      {whoami_html}
      {skills_html}
      {certs_html}
      {exp_html}
      {ach_html}
      {edu_html}
      {links_html}
    </div>
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
    all_posts = blog_posts + writeup_posts
    recent = sorted(all_posts, key=lambda p: p.get("date", ""), reverse=True)[:5]

    search_html = build_search_filter_html(all_posts)

    cards = []
    for p in recent:
        tags_str = p.get("tags", "")
        tags_html = build_tag_html(tags_str)

        diff_html = ""
        if p.get("difficulty"):
            d = p["difficulty"]
            diff_html = f'<span class="difficulty {d}">{d.upper()}</span>'

        cards.append(f"""
        <a href="{p['url']}" class="post-card" data-tags="{tags_str}">
          <div class="meta">
            <span class="date">{p.get('date', '')}</span>
            {tags_html} {diff_html}
          </div>
          <h2>{p.get('title', 'Untitled')}</h2>
          <p>{p.get('description', '')}</p>
        </a>
        """)

    content = f"""
    <div class="hero">
      <pre class="ascii-banner">{ASCII_BANNER}</pre>
      <p class="subtitle"><span class="typing-text"></span></p>
      <div class="links">
        <a href="blog.html">Blog</a>
        <a href="writeups.html">Writeups</a>
        <a href="resume.html">Resume</a>
      </div>
      <div class="hero-socials">
        <a href="https://github.com/antonytuff" target="_blank" title="GitHub">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
        </a>
        <a href="https://linkedin.com/in/anthony-mabi-9bb18b174" target="_blank" title="LinkedIn">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
        <a href="mailto:inert.fingers-0m@icloud.com" title="Email">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
        </a>
      </div>
    </div>

    <div class="about-section reveal">
      <p>Cybersecurity Engineer with 7+ years of experience across offensive security, DevSecOps, cloud security, and security automation. Specialized in red teaming, penetration testing, and building automated security tooling — with a growing focus on AI-driven security solutions and LLM security research. 200+ engagements delivered across enterprise, government, and financial sectors.</p>
      <div class="about-stats">
        <div class="stat-box">
          <span class="stat-num">200+</span>
          <span class="stat-label">Engagements</span>
        </div>
        <div class="stat-box">
          <span class="stat-num">7+</span>
          <span class="stat-label">Years Exp</span>
        </div>
        <div class="stat-box">
          <span class="stat-num">11</span>
          <span class="stat-label">Certifications</span>
        </div>
        <div class="stat-box">
          <span class="stat-num">{len(all_posts)}</span>
          <span class="stat-label">Posts</span>
        </div>
      </div>
    </div>

    <!-- Certifications Section -->
    <div class="section-header reveal">
      <h1>[*] certifications</h1>
      <p>Professional credentials and qualifications</p>
    </div>
    <div class="home-certs-grid reveal">
      <div class="home-cert-card">
        <img src="static/badge-ceh.png" alt="CEH" class="home-cert-img">
        <div class="home-cert-info">
          <span class="home-cert-name">CEH v10 + Practical & Master</span>
          <span class="home-cert-issuer">EC-Council</span>
        </div>
      </div>
      <div class="home-cert-card">
        <img src="static/badge-oscp.png" alt="eWPTX" class="home-cert-img">
        <div class="home-cert-info">
          <span class="home-cert-name">eWPTXv2</span>
          <span class="home-cert-issuer">eLearnSecurity</span>
        </div>
      </div>
      <div class="home-cert-card">
        <div class="home-cert-icon crte">CRTE</div>
        <div class="home-cert-info">
          <span class="home-cert-name">Certified Red Team Expert</span>
          <span class="home-cert-issuer">Altered Security</span>
        </div>
      </div>
      <div class="home-cert-card">
        <div class="home-cert-icon crto">CRTO</div>
        <div class="home-cert-info">
          <span class="home-cert-name">Certified Red Team Operator</span>
          <span class="home-cert-issuer">Zero Point Security</span>
        </div>
      </div>
      <div class="home-cert-card">
        <img src="static/badge-ctia.png" alt="CTIA" class="home-cert-img">
        <div class="home-cert-info">
          <span class="home-cert-name">CTIA</span>
          <span class="home-cert-issuer">EC-Council</span>
        </div>
      </div>
      <div class="home-cert-card">
        <div class="home-cert-icon csa">CSA</div>
        <div class="home-cert-info">
          <span class="home-cert-name">Certified SOC Analyst</span>
          <span class="home-cert-issuer">EC-Council</span>
        </div>
      </div>
      <div class="home-cert-card">
        <div class="home-cert-icon cnss">CNSS</div>
        <div class="home-cert-info">
          <span class="home-cert-name">Network Security Specialist</span>
          <span class="home-cert-issuer">ICSI, UK</span>
        </div>
      </div>
      <div class="home-cert-card">
        <div class="home-cert-icon cei">CEI</div>
        <div class="home-cert-info">
          <span class="home-cert-name">Certified EC-Council Instructor</span>
          <span class="home-cert-issuer">EC-Council</span>
        </div>
      </div>
    </div>
    <div style="text-align:center;margin-top:1rem;" class="reveal">
      <a href="resume.html" style="color:var(--cyan);font-size:0.85rem;">View all certifications &rarr;</a>
    </div>

    <!-- Projects Section -->
    <div class="section-header reveal">
      <h1>[+] projects</h1>
      <p>Current and featured work</p>
    </div>
    <div class="home-projects-grid reveal">
      <a href="https://github.com/antonytuff/attack-surface-dashboard" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Python</span>
        </div>
        <h3>Attack Surface Dashboard</h3>
        <p>AI-powered vulnerability management with multi-tenant architecture & scan parsers (Nmap, Burp, ZAP, Nessus, Nuclei, Shodan)</p>
        <div class="home-project-tags">
          <span class="tag">vuln-mgmt</span><span class="tag red-team">ai</span><span class="tag">automation</span>
        </div>
      </a>
      <a href="https://github.com/antonytuff/threat-carver" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Python</span>
        </div>
        <h3>Threat Carver</h3>
        <p>Threat intelligence tool leveraging MITRE ATT&CK for surgical precision in adversary tactics analysis</p>
        <div class="home-project-tags">
          <span class="tag">threat-intel</span><span class="tag">mitre</span>
        </div>
      </a>
      <a href="https://github.com/antonytuff/MITRE_ATT-CK_Explorer" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Python</span>
        </div>
        <h3>MITRE ATT&CK Explorer</h3>
        <p>Streamlit-based web app for exploring and analyzing the MITRE ATT&CK framework</p>
        <div class="home-project-tags">
          <span class="tag">mitre</span><span class="tag">streamlit</span>
        </div>
      </a>
      <a href="https://github.com/antonytuff/Red-Team-Notes" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Markdown</span>
        </div>
        <h3>Red Team Notes</h3>
        <p>OSCP guide and Red Team assessment reference — cheatsheets, techniques, and methodology</p>
        <div class="home-project-tags">
          <span class="tag red-team">red-team</span><span class="tag">oscp</span>
        </div>
      </a>
      <a href="https://github.com/antonytuff/Automation" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Python</span>
        </div>
        <h3>Automation</h3>
        <p>Automating boring stuff with Python — security scripts, recon tools, and workflow automation</p>
        <div class="home-project-tags">
          <span class="tag">python</span><span class="tag">automation</span>
        </div>
      </a>
      <a href="https://github.com/antonytuff/anthonytuff" target="_blank" class="home-project-card">
        <div class="home-project-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="home-project-lang">Python/CSS</span>
        </div>
        <h3>anthonytuff blog</h3>
        <p>Hacker-themed cybersecurity blog, HTB writeups, and online resume</p>
        <div class="home-project-tags">
          <span class="tag">blog</span><span class="tag">writeups</span>
        </div>
      </a>
    </div>

    <!-- Achievements Section -->
    <div class="section-header reveal">
      <h1>~/achievements</h1>
      <p>Milestones and accomplishments</p>
    </div>
    <div class="home-achievements reveal">
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Completed <strong>200+</strong> cybersecurity engagements across enterprise, government, and financial sectors</span>
      </div>
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Achieved <strong>HackTheBox Pro Hacker</strong> rank</span>
      </div>
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Multiple <strong>CTF competition podiums</strong> across national and international events</span>
      </div>
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Active security researcher and blogger at <a href="https://antonytuff.github.io" style="color:var(--cyan)">sploitony.com</a></span>
      </div>
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Built AI-powered <strong>Attack Surface Dashboard</strong> with multi-scanner integration</span>
      </div>
      <div class="home-achievement-item">
        <span class="achievement-icon">+</span>
        <span>Hold <strong>11 professional certifications</strong> including CEH Master, CRTE, CRTO, eWPTXv2</span>
      </div>
    </div>

    <!-- Latest Posts Section -->
    <div class="section-header reveal">
      <h1>latest</h1>
      <p>Recent posts and writeups</p>
    </div>
    {search_html}
    <div class="post-list">
      {''.join(cards) if cards else '<p style="color:var(--text-dim)">No posts yet.</p>'}
    </div>
    <div class="no-results">
      <p>root@blog:~# No matching posts found.</p>
    </div>
    """

    page = render_template("base.html",
        title="Home",
        site_name=SITE_NAME,
        description="Cybersecurity blog and HTB writeups",
        root="",
        content=content,
        nav_home="active"
    )
    (OUTPUT / "index.html").write_text(page)


def build_contact():
    """Build the contact page with a form that sends emails via Formspree."""
    content = """
    <div class="contact-page">
      <div class="contact-header">
        <h1 class="contact-title">Get in Touch</h1>
        <p class="contact-subtitle">Have a question, want to collaborate, or just want to say hello? Drop me a message.</p>
      </div>

      <div class="contact-grid">
        <div class="contact-form-wrap">
          <div class="contact-form-terminal">
            <div class="terminal-bar">
              <span class="terminal-dot red"></span>
              <span class="terminal-dot yellow"></span>
              <span class="terminal-dot green"></span>
              <span class="terminal-title">root@anthonytuff:~/contact</span>
            </div>
            <form class="contact-form" id="contact-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
              <div class="form-group">
                <label for="name">$ echo $NAME</label>
                <input type="text" id="name" name="name" placeholder="Your name" required>
              </div>
              <div class="form-group">
                <label for="email">$ echo $EMAIL</label>
                <input type="email" id="email" name="email" placeholder="your@email.com" required>
              </div>
              <div class="form-group">
                <label for="subject">$ echo $SUBJECT</label>
                <input type="text" id="subject" name="subject" placeholder="What's this about?">
              </div>
              <div class="form-group">
                <label for="message">$ cat << EOF</label>
                <textarea id="message" name="message" rows="6" placeholder="Your message..." required></textarea>
              </div>
              <button type="submit" class="form-submit">
                <span class="submit-text">$ send_message --to anthonytuff</span>
                <span class="submit-sending" style="display:none">Sending...</span>
                <span class="submit-done" style="display:none">Message sent!</span>
              </button>
            </form>
          </div>
        </div>

        <div class="contact-info">
          <div class="contact-card">
            <div class="contact-card-title">Other ways to reach me</div>
            <a href="https://github.com/antonytuff" target="_blank" class="contact-method">
              <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
              <div>
                <span class="method-label">GitHub</span>
                <span class="method-value">antonytuff</span>
              </div>
            </a>
            <a href="https://linkedin.com/in/anthony-mabi-9bb18b174" target="_blank" class="contact-method">
              <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              <div>
                <span class="method-label">LinkedIn</span>
                <span class="method-value">anthony-mabi</span>
              </div>
            </a>
            <a href="mailto:inert.fingers-0m@icloud.com" class="contact-method">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
              <div>
                <span class="method-label">Email</span>
                <span class="method-value">inert.fingers-0m@icloud.com</span>
              </div>
            </a>
          </div>

          <div class="contact-card">
            <div class="contact-card-title">Response time</div>
            <p style="color:var(--text-dim);font-size:0.85rem;line-height:1.6;">
              I typically respond within 24-48 hours. For urgent matters, reach out via LinkedIn or Twitter DM.
            </p>
          </div>
        </div>
      </div>
    </div>
    """

    page = render_template("base.html",
        title="Contact",
        site_name=SITE_NAME,
        description="Get in touch with Anthony Tuff",
        root="",
        content=content,
        nav_contact="active"
    )
    (OUTPUT / "contact.html").write_text(page)


def build():
    """Main build function - two-pass: collect metadata, then build with sidebar."""
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    if STATIC.exists():
        shutil.copytree(STATIC, OUTPUT / "static")

    # Copy CNAME to output root for GitHub Pages custom domain
    cname = STATIC / "CNAME"
    if cname.exists():
        shutil.copy(cname, OUTPUT / "CNAME")

    # Pass 1: collect metadata from all posts (no sidebar yet)
    blog_posts = []
    blog_dir = CONTENT / "blog"
    if blog_dir.exists():
        for md in blog_dir.glob("*.md"):
            text = md.read_text()
            meta, _ = parse_frontmatter(text)
            meta["slug"] = md.stem
            meta["url"] = f"blog/{md.stem}.html"
            meta["_path"] = md
            blog_posts.append(meta)

    writeup_posts = []
    writeup_dir = CONTENT / "writeups"
    if writeup_dir.exists():
        for md in writeup_dir.glob("*.md"):
            text = md.read_text()
            meta, _ = parse_frontmatter(text)
            meta["slug"] = md.stem
            meta["url"] = f"writeups/{md.stem}.html"
            meta["_path"] = md
            writeup_posts.append(meta)

    all_posts = blog_posts + writeup_posts

    # Pass 2: build posts with sidebar using all_posts for context
    for p in blog_posts:
        build_post(p["_path"], "blog", all_posts, root="../")

    for p in writeup_posts:
        build_post(p["_path"], "writeups", all_posts, root="../")

    build_listing(blog_posts, "blog", "cat /blog/*", "Cybersecurity articles, tutorials, and research")
    build_listing(writeup_posts, "writeups", "cat /writeups/*", "HackTheBox and CTF writeups")
    build_resume()
    build_contact()
    build_index(blog_posts, writeup_posts)

    # Generate search index JSON
    search_data = []
    for p in all_posts:
        section = "blog" if "blog/" in p.get("url", "") else "writeups"
        search_data.append({
            "title": p.get("title", "Untitled"),
            "url": p.get("url", ""),
            "date": p.get("date", ""),
            "tags": p.get("tags", ""),
            "description": p.get("description", ""),
            "section": section,
            "difficulty": p.get("difficulty", "")
        })
    (OUTPUT / "search-index.json").write_text(json.dumps(search_data, indent=2))

    print(f"[+] Built {len(blog_posts)} blog posts")
    print(f"[+] Built {len(writeup_posts)} writeups")
    print(f"[+] Search index: {len(search_data)} entries")
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
