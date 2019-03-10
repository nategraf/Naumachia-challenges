# Copper

Bob learned that telnet was actually not secure. Because Bob is a good administrator he wanted to make his own, more secure, version of telnet. He heard AES was secure so he decided to use that.

Here is the script he runs every day over telnet:

```
ls -la
date > monitor.txt
echo "=========================================" >> monitor.txt
echo "ps -aux" >> monitor.txt
ps -aux >> monitor.txt
echo "=========================================" >> monitor.txt
echo "df -h" >> monitor.txt
df -h >> monitor.txt
cp ./monitor.txt /logs
exit
```

## Scenario

This challenge involves having the player construct an encrypted telnet command that copies the flag file to a directory that can be seen.

## Solution
The solution requires a few steps.

1. VPN into Naumachia environment
2. Start ettercap ettercap -G
3. Set to unified listen on tap0
4. Scan for hosts
5. Start wireshark
6. Start arp spoofing in sniff remote connections mode
7. Note the ip of "bob" and "alice"
8. Capture at least one full conversation
8. Stop arp spoofing
9. Construct the command `cp flag.txt /logs` from the encrypted bytes (PoC in `attacker/attacker.py`)
10. Send encrypted messages to telnet server
11. Grab the flag from `<ip>:8080/flag.txt`
