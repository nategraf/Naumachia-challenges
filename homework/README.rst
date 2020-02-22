=============
Homework Help
=============

*Could you help me with my homework? I think the professor's solution is broken.*

**Scenario**: The network contains a web homework submission server, grading server, and message queue that shuttles
messages between. The web site is for a intro to CS class and accepts and grades Python code, which then gets packaged
into a request and added to the message queue to execute on the grading server with reduced privilleges. By exploiting
an insecure configuration in the message queue the challenger can gain artitrary code execution on the grader server
with elevated privilleges.
