---
title: "Lab Review Extreme Red Team Laboratories MAILSERVICE"
date: 2026-05-29
tags: Intial Access,Red Team,Active Directory,Lateral Movement, Tunnelling
description: MAILSERVICE is a multi-domain Active Directory lab that covers the full attack chain. Initial access via mail server abuse, credential extraction, network pivoting, cross-domain trust exploitation, MSSQL privilege escalation, Kerberos delegation abuse, and DCSync. 
---

## Why I Did This Lab

A good friend of mine, [zerofrost](https://allannjuguna.github.io/) you know the type, always dropping links and saying "bro just try this"  pushed me toward Extreme Red Team Laboratories, and I am genuinely glad he did. After sitting CRTE and CRTO just recently, I was looking for something that would push me further into real Active Directory attack chains.

This is 2 cents review.

## MAILSERVICE Lab?

MAILSERVICE is an advanced Active Directory lab from [Extreme Red Team Laboratories (ERL)](https://extremeredlab.0x29a.it/chains). It simulates a realistic enterprise environment spanning **two domains** connected via a cross-forest trust. You are given a jump server and left to find your own way in or form intial access to owning the domain.

You start with a network, a VPN connection that can be requested  in their discord channel the rest is entirely on you. The lab is a realistic Active Directory attack chain that covers initial access, credential extraction, tunneling, lateral movement, and privilege escalation across multiple hosts and domains.
![](../static/img/Extreme/Pasted%20image%2020260528234104.png)
Just like the icon, you are likely going to scratch you head as you join in the dots and trying to find out what make sense.

The lab covers a full realistic attack chain including:
- **Initial foothold** 
- **Credential extraction** 
- **Network pivoting** using tunneling tools
- **Cross-domain trust exploitation** via Kerberos
- **MSSQL abuse** with cross-domain authentication
- **Privilege escalation** 
- **Active Directory delegation abuse**  RBCD, constrained delegation, and unconstrained delegation

In short: it is a realistic multi-stage attack chain that mirrors what you would encounter on an actual red team engagement.


## What You Will Learn

From a value proposition you are likely to learn the following ,
### 1. Network Traversal and Pivoting

You are not working in a flat network. You have to figure out how to reach internal hosts, set up tunnels, and route your traffic intelligently through compromised machines. If you have not practiced multi-hop pivoting in a segmented environment, this lab will force you to get comfortable with it .
### 2. Enumeration Deep and Methodical

Enumeration is always key, I spent a significant amount of time  to understand whats going on. it is the difference between finishing the lab and spinning in circles. You will use bloodHound, and you need to know how to read it and interpret. Not just run it. **Read and Understand it.** Understand what each ACE means, what delegation flags are set, and which relationships lead somewhere useful. I found myself going back to BloodHound repeatedly throughout the engagement, each time extracting something I had missed before.

### 3. Kerberos Delegation and Active Directory Misconfigurations

The lab exposes you to several common AD misconfigurations you will absolutely encounter on real engagements. I will not say which ones or in what order  that is for you to discover but the environment is rich with realistic configuration mistakes that have real-world parallels. If you have studied the CRTE, CRTP or CRTO material, you will recognise the categories. What the lab adds is the complexity of dealing with them in combination, in a multi-domain environment, with some paths deliberately blocked. Does the three flavor sounds familiar to you.

### 4. MSSQL Exploitation

MSSQL is your entry point into `nsa.gov`. Cross-domain trust authentication, `xp_cmdshell`, service account identity abuse — these are all in play. If you have not spent time with MSSQL in a domain context, expect this to humble you slightly before it teaches you.

### 5. Privilege Escalation

There are multiple escalation opportunities in the lab. Not all of them lead somewhere useful, and part of the challenge is identifying which path is worth investing time in. If your privesc methodology is weak or you rely on automated tools without understanding what they are finding, you will likely miss the intended path or chase dead ends.



## The Good

**Realistic environment.** Every technique the lab requires maps directly to what you encounter on real red team engagements. This is not a CTF with contrived vulnerabilities. The misconfigurations are the kind that you find in real world production environements.

**The technical depth .** You will not finish this lab by copy-pasting tools. You need to understand what each step does and why, because when the obvious path is blocked and it will be blocked , you need to reason your way to an alternative. That reasoning process is where the real learning happens. I actually appreciate how it made me have some sleepless nights  to figure out why a particular pattern was not working,

**Two-domain architecture.** Having to operate across two domains connected by a trust adds a layer of realism that single-domain labs simply cannot replicate. Learning how cross-domain authentication works and how to leverage it is a skill set that separates intermediate practitioners from advanced ones.

**Lab stability and persistent connections**. This is something I genuinely appreciated and want to call out specifically. The lab stayed stable throughout my entire engagement. Whenever I reconnected, whether the next morning or after a work call my tunnels were still active and my sessions were where I left them. That kind of reliability matters more than it sounds. There is nothing more demoralising than losing your pivot chain mid-engagement and having to rebuild it from scratch. 

I completed the lab over roughly five days, fitting it around actual client engagements. That would not have been possible without a stable environment. I could pick up exactly where I left off each session.

Just some pointers: use tmux wheere you can. Keep your chisel, socat, ligolo, or your tool,  reverse shells, and  attack windows in separate named tmux windows. When your VPN reconnects and your agent pings back in, you do not want to be scrambling to remember which terminal had which session. Set it up properly from day one and it will save you significant time and frustration across a multi-day engagement like this.

**ERL support via Discord.** When I was genuinely stuck, the ERL team on Discord was responsive and gave thoughtful nudges without spoiling the path. They do not give you answers they help you think. 

---

## The One Thing to Be Aware Of

This is a shared lab environment, and **other players leave traces.** During my engagement I found directories, files, and tools left behind by other players. Some of these were initially confusing,  it was not always obvious whether I was looking at something intentional or someone else's footprint.

**My advice:** develop a methodology for distinguishing your own artefacts from others'. Be systematic. If something feels out of place for the scenario, it probably belongs to another player.

**The lab can be reset.** If the environment feels contaminated by other players' activity, request a reset via the ERL Discord. The team is responsive and will get it sorted if there is a need be.


## What I Would Recommend Brushing Up On Before Starting

Based on my experience, I would recommend being solid on the following before diving in:
- **Active Directory fundamentals** authentication, trusts, group policies, and privilege hierarchies
- **Kerberos** not just the attack tools, but how the protocol actually works
- **Network pivoting** multi-hop tunneling in segmented environments
- **PowerShell operational security** what restrictions exist and how to work within them
- **Privilege escalation methodology** structured, not just tool-driven
- **Enumeration discipline**  knowing what questions to ask, not just which commands to run

If you have done CRTE or CRTO and felt comfortable with the material, you are ready for this lab. It will still challenge you and may not, but you willl understand whats going on.

## Certification 
Once you have captured the flag and completed your attack chain, the submission process is straightforward. You write up a report documenting all the steps you took your methodology, the techniques used, and the flag itself and submit it to ERL for review.

If your report passes review, you purchase your badge and you are officially certified.
![](../static/img/Extreme/Pasted%20image%2020260529002049.png)

![](../static/img/Extreme/Pasted%20image%2020260529002646.png)


## Conclusion

I recommend MAILSERVICE, without hesitation, to any practitioner who has completed a structured AD course and wants to test themselves against something closer to a real engagement.On the OPSEC point. there are no blue teams watching your steps in this lab, so do not let that hold you back. That said, it is absolutely something you can train yourself on while you are in the environment. If you want to go the extra mile, spin up a C2 framework and run your operations through it. The lab gives you the freedom to practice that kind of tradecraft alongside the core attack chain

[ERL](https://extremeredlab.0x29a.it/chains) have a genuinely good catalogue of labs and I would recommend them to anyone serious about levelling up their red team skills.Its actually affordable. I have already started looking at their **SUMMOS lab** as my next target. SUMMOS chains multiple environments including cloud components. the kind of modern multi-domain attack surface that reflects where real enterprise environments are heading. If the quality matches MAILSERVICE, it is going to be a very good time.


**Rating: 8/10**  
_(Minus one point for the shared environment artefact issue a minor operational inconvenience, not a reflection of the lab design itself.)_
