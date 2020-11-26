
#Version 0.1 of a python based javascript-deobfuscator

Intention was to automate the "search and replace" step of javacript malware de-obfuscation. 

Uses regex filters to extract variable/function names and values from lines of javascript. 
Builds a dictionary of extracted values. 
Resolves values to previously defined values, then updates the dictionary. 

eg 

var ss2 = new activexobject; # would update dict with {ss2::"activexobject"}

var x3 = ss2[filesystemobject]; #would resolves ss2 -> activexobject, and update dict with {x3:"activexobject[filesystemobject]}

And so on


Works reasonably well on the 1 sample file
Work in progress, need to expand to cover off more encoding types. 
Also need to update dictionary logic and regex filters. 

Very very much a WIP :)
