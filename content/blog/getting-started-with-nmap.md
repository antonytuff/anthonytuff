---
title: Getting Started with Nmap
date: 2026-03-10
tags: recon, tools
description: A beginner-friendly guide to network scanning with Nmap.
---

## Why Nmap?

Nmap (Network Mapper) is the de facto standard for network discovery and security auditing. Whether you're doing a pentest or just exploring your own network, Nmap is the first tool you reach for.

## Basic Scans

The simplest scan targets a single host:

```
nmap 192.168.1.1
```

For a more thorough scan with service detection:

```
nmap -sV -sC -p- 10.10.10.1
```

Flags breakdown:
- `-sV` -- Version detection
- `-sC` -- Default scripts
- `-p-` -- All 65535 ports

## Stealth Scanning

SYN scan (half-open) is the default for privileged users:

```
sudo nmap -sS -T4 10.10.10.1
```

> Always get proper authorization before scanning networks you don't own.

## Output Formats

Save your results for later analysis:

```
nmap -oA scan_results 10.10.10.1
```

This creates `.nmap`, `.xml`, and `.gnmap` files.

## Next Steps

- Explore NSE scripts in `/usr/share/nmap/scripts/`
- Learn about firewall evasion techniques
- Practice on platforms like HackTheBox and TryHackMe
