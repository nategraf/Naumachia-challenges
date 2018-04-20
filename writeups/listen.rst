========================
Stop and Listen Solution
========================

Challenge Setup:
  * Multiple hosts are having a "conversation" over UDP broadcast
  * The flag is at the end of their "conversation"

Solution:
  * User logs into Naumachia and turns on Wireshark or tcpdump
  * Look through the tcpdump or Wireshark output and observe the UDP broadcasts
  * Extract the flag from the last transmission in the conversation containing the flag
