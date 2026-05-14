---
title: Threat Carver
date: 2025-05-29
description: Streamlit-based explorer for the MITRE ATT&CK framework — surgical analysis of adversary TTPs with Atomic Red Team replication.
tags: tools, red-team, mitre, threat-intel, python
repo: https://github.com/antonytuff/threat-carver
---

## Overview

**Threat Carver** is a Streamlit-based web application built on the [MITRE ATT&CK](https://attack.mitre.org/) framework. It gives offensive and detection-engineering teams a single interactive interface to pivot between threat groups, techniques, and replication payloads — pulling live data straight from the MITRE CTI repository and the [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) project.

> The name comes from "carving" precise TTPs out of the noisy ATT&CK catalogue and turning them into runnable, controlled tests.

[**View on GitHub →**](https://github.com/antonytuff/threat-carver)

---

## Features

### Group Analysis
- Explore techniques used by specific threat groups (APT28, FIN7, Lazarus, etc.)
- Filter by tactic and search for techniques within a group's profile
- Visualise the distribution of tactics across a group's TTPs
- Export filtered results to **CSV** or **JSON**

### Technique Explorer
- Full-text search across every technique in ATT&CK by ID, name, or description
- See detailed metadata (data sources, platforms, mitigations) per technique
- Cross-reference each technique back to the threat groups that use it

### Technique Replication
- Pulls the matching **Atomic Red Team** tests for a selected technique
- Surfaces step-by-step commands, platform-specific dependencies, and cleanup routines
- Designed for safe execution in a controlled lab / range environment

### About ATT&CK
- Built-in primer on the framework, its tactics, and how to apply it in adversary emulation

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Streamlit |
| Data | Pandas, PyYAML |
| Viz | Plotly |
| Sources | [MITRE CTI](https://github.com/mitre/cti), [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) |
| Language | Python 3.7+ |

---

## Quickstart

```bash
git clone https://github.com/antonytuff/threat-carver.git
cd threat-carver/"Threat Carver"
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL (default `http://localhost:8501`) and pick a page from the sidebar.

---

## Why it exists

Most ATT&CK tooling is either read-only (the ATT&CK Navigator) or locked behind enterprise platforms. Threat Carver bridges that gap — a lightweight, self-hosted UI that gets you from "what does this group do?" to "give me a runnable Atomic test for that technique" in two clicks. Useful for:

- Red team engagement planning and TTP selection
- Purple team exercises mapping detections to specific Atomics
- Training labs and CTF-style adversary emulation

---

## License

MIT — see the [repo](https://github.com/antonytuff/threat-carver) for full text.

## Acknowledgements

- [MITRE ATT&CK](https://attack.mitre.org/)
- [MITRE CTI Repository](https://github.com/mitre/cti)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
- [Streamlit](https://streamlit.io/)
