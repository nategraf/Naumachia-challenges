====================
Straw House Solution
====================

Challenge Setup:
  * User is on L2 with a telnet client and telnet shell server
  * The serevr only uses username/password security and does not secure transport

Solution:
  * Perform a mitm attack such as ARP spoofing to intercept telnet traffic
  * Search through the packets sent by the client for a username and password
  * Log in to the telnet server and read the from a file in the home directory
