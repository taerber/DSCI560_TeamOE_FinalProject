
How to deploy our website

Step 1: Save somewhere onto your computer

Step 2: open a terminal window

Step 3: cd to the location of the FinalProject folder

Step 4: run Python backend.py

Step 5: copy and paste the url given into a chrome browser(please use chrome as there may be cache problems with other browsers)

Step 6: Click around on the website! When entering routes please make sure the destination and starting location are far apart, if the locations are too close and the mileage entered is enough to get from point A to B then the routing doesn't work because of the buffer we have added in place(15-50 miles), if this happens just click back to the previous page and retry a different remaining mileage or locations

Some Example Routes:

Destination: 650 Gateway Center Dr, San Diego, CA 92102
Current Location: 31790 Oak Ranch CT Westlake Village CA 91361
Remaining Mileage: 100
Total Mileage: 200

Destination: PIER 39 The Embarcadero &, Beach St, San Francisco, CA 94133
Current Location: 31790 Oak Ranch CT Westlake Village CA 91361
Remaining Mileage: 200
Total Mileage: 400

Destination: 886 Cannery Row, Monterey, CA 93940
Current Location: 1 UCEN Rd, Santa Barbara, CA 93106
Remaining Mileage: 100
Total Mileage: 200

- for our route page when entering locations the map may not refresh, this has to due to how the browser caches, please use Chrome to avoid these problems, if the issue persists then please just clear your browsers history and you can open the 'route_map.html' in the templates folder in a browser and will see the map file does create the correct map but may not refresh in the route html.


Problems that could arise

- for backend to run all the import packages need to be installed

- due to computer enviroment differences(since dsci 553 requires us to use an older version of spark and my computer uses anaconda also I have too many versions of spark so the file can't correctly find the same versions) the kmeans_pred.py file cannot be run in the backend.py, so all the html maps that python file reproduces have been pre-created and entered manually into the backend.py, but they are produced by the kmeans_pred.py file and are accurate 



