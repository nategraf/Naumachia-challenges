======================
A Rose by Any Other IP
======================

Description:
  What's in a domain name? That which we call ``rosedigiulieta.ethihak`` by any other ip would smell as sweet.

Setup:
 * User is on L2 with a DNS server
 * On another L2 segment is a client and server speaking over HTTP
 * The server uses password based authentication and session cookies

Solution:
 * MitM DNS queries to poison the client records
 * Host an HTTP service to receive the traffic from the client and get their cookie or password
 * Log in as the administrator and get the flag

Flavor:
 * The HTTP service is a Rose store owned by Juliet from Romeo and Juliet
 * Also the whole site it in Italian, because why not

Flag:
  ``Ethihak{o_romeo_romeo_dig_@8.8.8.8_A_romeo.}``
