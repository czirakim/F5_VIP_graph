# F5_VIP_graph

This project is trying to create a visual representation of a F5 Virtual Server.
<br>The main python script is : *F5_VIP_grapher.py  <VIP_name>*
<br>It is using API calls to get the VIP (it uses the name of the VIP as an argument), the pools, pool members,
<br>then the irule names and last the irules content. Based on this info it will draw , using pyvis library,
<br>the connections between the VIP, pool and pool members. The result is saved as an html file.
<br>As irules can be really complex, this is mainly for irules with "if" and "switch" clauses.
<br>Then there is the *app.py* file that takes care of the web server part. It is using content from 
<br>*templates* folder (where the index html is) and *static* folder (where the html documents for each virtual servers are 
<br>generated, and also where the css and js part is)
<br>There are 2 environment variables:  *Authorization_string* (this is credentials for Basic authentication) 
<br>and *IP_ADDRESS* (this is the IP of the F5 device).


# Credits
This was written by Mihai Cziraki
