# agisoft-processing
Written for USC Institute for Creative Technologies' Raspberry Pi Capture Cage. 

You will need a parent folder with any number of pairs of folders. 
Each pair contains 1. a folder for texture (no projection pattern on the model) and 2. a folder for the projection pattern for 3D model use. 

Using Agisoft PhotoScan software, simply "Run Script" with the photoprocessing.py

"Custom Menu" will appear. Click "Select folder" and select the PARENT folder.

***All texture folders will need to end with "_1" and mesh folders will need to end with "_2". (This format was done automatically by the Raspberry Pis)

The software will align photos and build the dense cloud of the projection photos. After it finishes, simply clean up the model so the dense cloud only contains the points you want in your 3D model.

Finally, select "Create model" in the Custom Menu. Some Python scripting magic will occur and your textured model is ready!
