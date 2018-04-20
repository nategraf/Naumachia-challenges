===============================
A Rose by Any Other IP Solution
===============================

Challenge Setup:
 * User is on L2 with a DNS server
 * On another L2 segment is a client and server speaking over HTTP
 * The server uses password based authentication and session cookies

Solution:
 * MitM DNS queries to poison the client records
 * Host an HTTP service to receive the traffic from the client and get their cookie or password
 * Log in as the administrator and get the flag
