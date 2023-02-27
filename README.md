# F5_VIP_graph

This project is trying to create a physical representation of a F5 Virtual Server.
<br>The main python script is : F5_VIP_grapher.py  <VIP_name>
<br>It is using API calls to get the VIP (it uses the name of the VIP as an argument), the pools, pool members,
<br>then the irule names and last the irules content. Based on these info it will draw , using pyvis library,
<br>the connections between the VIP, pool and pool members. The result it is saved as an html file.
<br>As irules can be really complex, this is mainly for irules with "if" and "switch" clauses.

# Credits
This was written by Mihai Cziraki
