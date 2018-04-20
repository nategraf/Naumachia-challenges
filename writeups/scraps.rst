=====================
Table Scraps Solution
=====================

Challenge Setup:
 * User is on L2 with one other host
 * That host is throwing out reverse shell connections to an ip that isn't on the network

Solution:
 * Listen on the network and notice that the host is try to reach out to a non-existant ip
 * Assume that ip, and look at the connection attempts to figure out a port number
 * Listen on that port number and catch the reverse shell
