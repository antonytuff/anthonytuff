---
title: "Lab Review Extreme Red Team Laboratories CALIPENDULA"
date: 2026-06-25
tags: red-team active-directory,GCP cloud-security, ERTL,RBCD, kerberos delegation,tunneling, evasion PetitPotam,lateral-movement, assumed-breach, hybrid-cloud,IAM service-accounts, secret-manager 
description: CALIPENDULA is an Extreme Red Team Lab that simulates a hybrid GCP and Active Directory breach scenario, pushing you through cloud IAM enumeration, service account chaining, RBCD relay attacks, multi-hop tunnelling in a segmented network.
---


![](../static/img/Cali/Pasted%20image%2020260625125035.png)


## CALIPENDULA ERTL Review
So I have been grinding through the Extreme Red Team Labs active directory chains, mostly just keeping my skills sharp and honestly because I enjoy it. I recently finished the CALIPENDULA lab and I figured I should write something about it not to spoil it for anyone, but more to talk about what the lab pushes you to learn and my overall experience.

So this is not a spoiler, or revealing attack paths, nothing that's going to ruin it for you. This is more of a "here is what to expect and what you will learn" kind of post.

## What is CALIPENDULA?
CALIPENDULA is an assumed breach lab, meaning you start with some minimal credentials already in hand. The idea is to simulate a scenario where an attacker already has a foothold and needs to find a way deeper into the network. The unique angle here compared to other labs is that it is a hybrid environment, you encounter a  Google Cloud Platform(GCP) and Active Directory in the same chain. You cannot just skip one and go to the other. They are connected by design and you need to understand both to move forward.

I want to be honest,  I was not super strong on GCP when I started this. Thankfully I had gone through the MCRTA certification a while back which covers AWS, GCP and Azure from an attacker's perspective. If you are thinking about cloud security labs and you have not looked at MCRTA, it worth going through it, it gave me just enough foundation to not be completely lost here. Without it I would have been staring at the screen for days not knowing where to even start.

## The GCP Side of Things

This was genuinely the most interesting part for me because it was newer territory. What I realized is that in cloud environments, knowing what to look for matters more than knowing all the tools. I spent a couple of days reading through common GCP attack scenarios and IAM concepts before things started clicking.

The interesting thing about GCP attacks is how chained they can be. You might start with something small and it opens a door to something bigger. The enumeration phase is where you learn the most, you are constantly asking yourself what this identity can access and where that leads.

I played around with a few tools, gcloud obviously, but also some others I had not used much before gcloud, pacu, and somet otjers. The experimentation was actually fun. Cloud security has a different flavour to it compared to pure AD work and I enjoyed that context switch.

I will not say more than that because the enumeration and discovery is genuinely the most satisfying part of this section. Let it surprise you.

## Active Directory: The Segmentation Challenge
I liked how the Actived directory had been segmented. The DC is not directly reachable from everywhere. The network is segmented and you can only get to the DC from specific hosts. That means your tunnelling game has to be on point.

I am a Ligolo-ng & chisel guy. It is just clean and I like how it works. But this lab beat me with it since defender is on and they are windows server so if you run an executable its likey going to be caugh., the network topology just did not play well and I had to pivot to socat. Initially that was frustrating because I had to slow down and actually understand what socat was doing rather than just running it. But honestly that ended up being one of the biggest takeaways from the whole lab. I now understand TCP relay and SOCKS tunnelling at a much deeper level than before. Sometimes the tools you are comfortable with will not be the right fit and that forces you to learn.

On the Active Directory side, the lab teaches you about some very specific concepts that I think every red teamer needs to understand deeply. Things around delegation the different types, how they work, why they exist, and more importantly how they can be abused. The lab also pushes you through coercion techniques, relay attacks, and Kerberos-specific attack chains. It brings a lot of things together in a way that makes sense in context rather than just reading about them in isolation.

One honest thing I will say,  sometimes tools break for no apparent reason even when your methodology is correct. I spent multiple days on one part where I was convinced the path was right but something was not clicking. Turns out it was a tool version issue. 

## Evasion
This one is worth calling out separately. Defender is running on the victim machine and it will catch the standard stuff or signatured tools. Your usual executables will get flagged. You need to think creatively about how you execute things in memory, how you bypass AMSI, and how you achieve your objectives without putting anything on disk that does not need to be there.



## The Not So Great Parts
I try to be balanced so let me be honest about the rough edges.
The lab has multiple players and at times it was noticeably sluggish. When you are in the middle of a timed attack chain like when you are working against something that resets every minute the lag is genuinely painful.

Resets also require three votes from players which can be difficult to coordinate, especially in off-peak hours. I raised concerns in the Discord channel and while the community is helpful, the reset process could be smoother. The lab also picks up contamination from other players files left behind, changes other people made which can add confusion especially when you are trying to understand whether something you are seeing is part of the intended lab design or a leftover from someone else's session.



## Should You Do CALIPENDULA?
If you want to practice hybrid cloud and AD attack chains in a realistic environment, yes. The lab is well designed and the learning density is high. You will come out of it with better instincts around GCP enumeration, tunnelling in segmented networks, and Kerberos delegation abuse.

Go in prepared. Brush up on GCP IAM and service accounts before you start. Know your SOCKS tunnelling tools and have a backup plan if your preferred tool does not cooperate. And have patience some of it will take time to click.

The frustration is part of it. That is where the real learning happens.


## Certification

Once you have captured the flag and completed your attack chain, the submission process is straightforward. You write up a report documenting all the steps you took your methodology, the techniques used, and the flag itself and submit it to ERL for review.

If your report passes review, you purchase your badge and you are officially certified.
![](../static/img/Cali/Pasted%20image%2020260625124729.png)


![](../static/img/Cali/Pasted%20image%2020260625124707.png)

## Conclusion

Overall I think CALIPENDULA is a great lab and genuinely its has realism in it.. It does not just test one skill, it exposes you to a combination of things that you would actually encounter in the field. The GCP component alone makes it stand out from most AD-focused labs, and the tunnelling challenges add a layer of operational complexity that forces you to think rather than just execute.

One thing I did not mention earlier but think is worth calling out,  the lab would be an excellent playground for experimenting with a C2 framework. The segmented network, the evasion requirements, and the multiple pivot points make it a natural environment for testing different C2 setups and seeing how they hold up under realistic constraints. If you want to practice not just the technique but the  red team workflow  or methodology with proper infrastructure, CALIPENDULA gives you the terrain to do that.

I would also encourage people to deliberately try different attack paths through the lab rather than just finding one that works and stopping there. There are alternative routes and exploring them will teach you more than rushing to the flag.

My rating: **8/10**

Points off for the shared environment issues and the reset friction. Everything else, the design, the learning curve, the realism ,is solid. .