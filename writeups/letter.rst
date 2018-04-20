====================
Open Letter Solution
====================

Challenge Setup:
 * User is on L2 with an SMTP server and a client sending mail
 * The client uses STARTTLS to begin a secure TLS connection (single CA and high strength ciphers)
 * The client will continue without encryptio if the server responds with an error code to STARTTLS

Solution:
 * MitM traffic on the network and notice trace the SMTP traffic
 * Drop the packet containing the STARTTLS command and spoof an error (>400) return code
 * Listen for mail on the wire and get the flag from the email
