====================
Stick House Solution
====================

Challenge Setup:
  * User is on L2 with a telnet client and telnet shell server
  * The serevr only uses username/password along with a IP address whitelist

Solution:
  * Perform a mitm attack such as ARP spoofing to intercept telnet traffic
  * Search through the packets sent by the client for a username and password
  * Change the interface IP to match the client
  * Log in to the telnet server and read the from a file in the home directory
