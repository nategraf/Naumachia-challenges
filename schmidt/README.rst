==========
J. Schmidt
==========

*Everytime I go out, people always shout John Jacob Jingleheimer Schmidt! I'd change my name, but I
just got the best domain for my website.*

**Scenario**: The attacker is on layer-2 with a dns server which a client on another segment is
using to resolve the domain name for a website they are accessing. The website is gaurded by HTTP
basic auth so the attacker cannot simply browse it directly. To get the client's credentials they
will need to intercept and modify the DNS response to point to their own box and pose as the HTTP
server.
