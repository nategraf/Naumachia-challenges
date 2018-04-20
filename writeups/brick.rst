====================
Brick House Solution
====================

Challenge Setup:
  * User is on L2 with a telnet client and telnet shell server
  * The serevr only uses username/password along with an HMAC SHA256 challenge and reponse with a secret shared key

Solution:
  * Perform a mitm attack such as ARP spoofing to intercept telnet traffic
  * Modify or hijack the client telnet session stream to read the flag or get a reverse shell
