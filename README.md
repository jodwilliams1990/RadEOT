# RadEOT

Updated 21/04/2020

## What is RadEOT?
RadEOT - the Radio Educational Outreach Tool - uses commercially available technology including a: 
- Raspberry Pi 3B+. This is essentially a small computer, which can be connected to a TV Screen via a HDMI cable or to a touchscreen
- DVB-T software defined radio (SDR) dongle. This is a large USB stick that can plug into a computer, and uses highly configurable SDR to process data from an antenna
- 7" touchscreen, 
- 20000mAh battery pack and
- 3d printed case 
to collect freely available radio data for educational purposes. RadEOT has been developed at the University of Leicester and co-designed with partners across the United Kingdom to ensure it is fit for purpose to complement educational teaching across KS3-5 (ages 11-18), and beyond. In this repository you can find the software and hardware required to make and run your own RadEOT unit, as well as some other developmental codes. 

## What can RadEOT do?
RadEOT is currently designed for:
- tracking aircraft and using the data for physics and mathematics problems, up to a range of ~40 miles
- Designing a horn antenna to observe the galactic centre
- Listen to local and national FM radio
- Listen to other radio sources to observe the radio background
RadEOT will continue to be developed to include meteor shower tracking and downloading data from NOAA weather satellites, among others.

## What is in the repository?
Folder contents:
- Software - instructions to download, install and run RadEOT on a clean install of Raspbian on a Raspberry Pi 3B+
- Hardware - (COMING SOON) documents to enable 3D printing of a case for RadEOT. These were the basis of the initial deployment of 27 RadEOT units in Q1/2 2020
- ADS-B - The basis of the PlaneTracker unit for aircraft tracking and data analysis. It is designed to be run by itself on a Mac.
- RadioDatabase - Radio database is a script developed in August 2019 to identify what radio sources occur at a particular frequency, using data from Ofcom. 
- Old - Previous versions of software: the original gui2408.py is the (slightly amended) working version from 24/08/18 written in TKinter, and demod.py that will form the basis of the Deconvolution activity.
