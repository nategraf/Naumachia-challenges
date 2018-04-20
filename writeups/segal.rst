===========
Seagl's Law
===========

Challenge Setup:
  * User is on L2 with an HTTPS server, a client, and an NTP server
  * The HTTPS server uses strong TLSv1.2 with EDH
  * The HTTP client only trusts one CA, which is not accesible in the challenge
  * The user has access to a git repository from a previous challenge
  * The git repository containes an expired certificate issued by the same CA as the one in use

Solution:
  * Find the expired certificiate and key in an old commit of the git repository
  * Preform a mitm attack on the network to intecept both HTTPS and NTP traffic
  * Alter the NTP traffic to specifiy a date in which the expired certificate is valid
  * Break TLS by either hosting the site from the obtained source, or proxying the connection
  * Wait for the client to log in and access the flag
