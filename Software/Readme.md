#RadEOT

This is the software for the Radio Educational Outreach Tool (RadEOT), up to date to 20/04/2020. The development was led by Dr Jamie Williams at the University of Leicester, with Felicity Easton, Jordan Penney and Prof. Jon Lapington. Several undergraduate and project students also helped in the development - acknowledgements go to Ellen, Emily, Dan, Natasha and Drew for their hard work.

To install the software on a Raspberry Pi 3B+:
- sudo apt update
- sudo apt full-upgrade
- sudo apt-get install qt5-default
- Extract the contents of the Scripts Zip file into ~/Documents/Scripts
- Extract the contents of the PlaneTracker Zipe file into ~/Documents/PlaneTracker
- pip3 install Pandas
- sudo apt-get install gqrx-sdr
- sudo apt-get install pulseaudio
- pip3 install cython shapely pyshp psix
- sudo apt-get install libgeos-dev
- sudo apt-get install libproj-dev proj-data proj-bin
- sudo apt-get install libatlas-base-dev
- pip3 install cartopy geocoder pyrtlsdr
- pip3 install bokeh tables
- sudo apt-get install git
- sudo apt-get install cmake
- sudo apt-get install libusb-1.0-0-dev
- git
- make
- 
- pip3 pymodes
- remove qt5ct
- install qt creator
- Once GQRX is installed, copy contents of "GQRX" folder to /home/pi/.config/gqrx
- Copy Run-RadEOT.sh to a convenient location (most likely Desktop)
- 
