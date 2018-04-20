
======================
Secret Recipe Solution
======================

Challenge Setup:
 * User is on L2 with an FTP server an associated authentication server
 * They know the username of the user they want to access, but not the password
 * Each login request is sent via TCP in a JSON web token (JWT) and a signed reponse is sent back

Solution:
 * Start an ARP spoof MitM attack to capture packets on the network
 * Log in as anonymous and capture the packet sent from the auth server in response
 * Attempt to log in as the restricted user, and replace the auth failed packet with the auth success packet from anonymous
