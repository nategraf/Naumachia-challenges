============================
Stuck in the Middle Solution
============================

Challenge Setup:
  * User is on L2 with two peers talking over a plaintext tcp UDP protocol
  * One peer will periodically send a "flag" over to the over and ask if it is correct. The other peer with repond yes or no

Solution:
  * Perform a mitm attack such as ARP spoofing to intercept both directions of communication
  * Examine each response from the responding peer until it reponds that the submitting peer submitted a correct flag
