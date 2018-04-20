=============
Secret Recipe
=============

Description:
  ``topchef`` is compiling a recipe book. It's public to everyone with ``anonymous`` access, but I bet he isn't releasing all of his recipes

Setup:
 * User is on L2 with an FTP server an associated authentication server
 * They know the username of the user they want to access, but not the password
 * Each login request is sent via TCP in a JSON web token (JWT) and a signed reponse is sent back

Solution:
 * Start an ARP spoof MitM attack to capture packets on the network
 * Log in as anonymous and capture the packet sent from the auth server in response
 * Attempt to log in as the restricted user, and replace the auth failed packet with the auth success packet from anonymous

Flavor:
 * The FTP server contains a public repo of recipes, and a private "secret recipe" (flag)
 * Recipes appropriated from `<http://www.garvick.com/recipes/meal-master.htm>`_

Flag:
  ``Ethihak{grandma_loves_you_xoxoxox}``
