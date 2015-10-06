ABOUT

No Free Lunch is a web application for consumer decision-making. This prototype software is a proof of concept rather than an output of research in software engineering methodology. It uses well-established patterns and technologies.

This directory is divided into two parts, assets/ and app/. The directory assets/ contains Python modules for text mining and building the database. The directory app/ contains Node.js, JavaScript, HTML and CSS files for creating and running a web application. 

The database is MongoDB and assets/ includes files in a directory called data/ for the database plus a script to insert the records, build.py (you cannot run the script until you install a number of dependencies, see below). This data/ directory is a stand-in for a web crawling and scraping module. The web crawling and scraping modules are included for reference in /assets/harvesting - but it is highly recommended that you do NOT run these for the prototype setup, because web crawling creates a major communication bottleneck.

--------------------------------------------------------------------------

USABILITY TESTING

The University of Melbourne's firewall settings do not allow you to visit this URL from within university networks, but from a home wireless or Ethernet network, please visit the app running live at the following address:

http://ec2-52-24-163-164.us-west-2.compute.amazonaws.com:3000/

(For desktop-based browsers only.)

The prototype includes 3 product categories as samples:

space heater
wireless printer
drill

Enter any of these terms into the search bar exactly as written above.

---------------------------------------------------------------------------

SERVER-SIDE BUILDING INSTRUCTIONS

For the target end user, no installation is required. Users can visit and use the web app by visiting the No Free Lunch URL via their browser (desktop only), the prototype URL is listed above. If you need to run No Free Lunch as a server, follow the following instructions. Most of these instructions involve installing dependencies; the main files for actually building and running the app are assets/build.py (6) and app/app.js (13).

A. BUILD DATABASE AND RUN TEXT MINING MODULES

1. Download and install Python 2.7.6.
Follow instructions here: https://www.python.org/downloads/

2. Download and install MongoDB.
Follow instructions here: http://docs.mongodb.org/manual/installation/

3. Navigate to the assets/ directory
$ cd assets

4. Install pip
$ sudo python get-pip.py

5. Make sure requisite Fortran compilers are installed. 
On Linux:
$ sudo apt-get update
$ sudo apt-get install gfortran python-dev libblas-dev liblapack-dev g++

6. Install the Python dependencies
$ sudo pip install -r requirements.txt

-If facing problems with NumPy and SciPy, installation info is found here:
http://www.scipy.org/install.html. Note the dependencies in step 5.

7. Download the nltk corpora:
$ sudo python -m nltk.downloader -d /usr/share/nltk_data all

8. In a separate process, start the mongo server. Do not stop this process!
$ sudo mongod

If mongod throws an error and shuts down on Linux it likely has the wrong data directory specified. Try this:
$ sudo mongod --dbpath /var/lib/

9. Run the back-end scripts - build the database and run text mining modules
$ python build.py

B. SET UP THE WEB APPLICATION

10. Download node.js and npm.
https://nodejs.org/download/

On Linux npm must be installed separately:
$ sudo apt-get install npm

11. Install dependencies
$ npm install

12. Navigate back up a directory, and then to app
$ cd ../app

13. Fire up the app
$ node app
This may also be required on Linux:
sudo ln -s /usr/bin/nodejs /usr/bin/node

14. You can now see the app by navigating to http://localhost:3000/ on your browser.

The prototype includes 3 product categories as samples:
space heater
wireless printer
drill

Enter any of these terms into the search bar exactly as written above.

--------------------------------------------------------------------------

ADDITIONAL SERVER-SIDE OPTIONS

The prototype defaults to using sentiment as implied by star ratings, but additional sentiment analysis tools are included as well in the mining.sentimentscoring package. The class ProductScorer, which becomes the main object within the mining module for dispatching the other modules, can be passed different options for specifying which sentiment scoring method to use, e.g.

# to use a classifier-based sentiment scoring on category 'space heater'
p = ProductScorer('space heater','classifier') 

# to use a dictionary-based sentiment scoring on category 'space heater'
p = ProductScorer('space heater','dictionary')

Based on accuracy analysis, these methods are not recommended over the human-supplied sentiment scores.