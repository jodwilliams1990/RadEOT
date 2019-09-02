import numpy as np
from threading import Thread, Event, Lock
import socket as sock
from subprocess import Popen
import sys
import time

import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic
import platform
from geocoder import ip
import pyModeS as pms

from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource, WheelZoomTool, WMTSTileSource, HoverTool
from bokeh.models.glyphs import ImageURL, Circle, MultiLine

from gc import collect
from os import _exit

# Unit conversions
ft = 0.3048 # Meters, exactly
kt = 1852 / 3600 # Meters / second, exactly
ft_min = ft / 60 # Meters / second, exactly

# Aircraft types
cats = {41:'Light', 42:'Small', 43:'Large', 44:'High-Vortex Large', 45:'Heavy', 46:'High Performance', 47:'Rotorcraft',
        31:'Glider', 32:'Lighter-than-Air', 33:'Skydiver', 34:'Ultralight', 35:'Reserved', 36:'UAV', 37:'Space Vehicle',
        21:'Surface Emergency Vehicle', 22:'Surface Service Vehicle', 23:'Point Obstacle', 24:'Cluster Obstacle', 25:'Line Obstacle', 26:'Reserved', 27:'Reserved'}
# Available sprites
sprites = {41:'Light', 42:'Small', 43:'Large', 44:'High-VortexLarge', 45:'Heavy', 47:'Rotorcraft', 
           31:'Glider', 34:'Ultralight'}

# ColumnDataSources for sending aircraft data to the plot. If you want to change these, remember to also change the new data dictionaries in atc() to match
# rot is specifically for rotating the aircraft sprite. hdg is the useful heading
# hb is an attempt to fix a mysterious bug involving phantom hitbox circles being left behind
planeSprites = ColumnDataSource(dict(img = [], x = [], y = [], rot = [], hb = [], addr = [], call = [], cat = [], alt = [], hdg = [], spd = []))
planeShdws = ColumnDataSource(dict(img = [], x = [], y = [], rot = []))
planeTrails = ColumnDataSource(dict(x = [], y = [])) # Active aircraft trails
planePaths = ColumnDataSource(dict(x = [], y = [])) # Historic flight paths

geo = Geodesic() # Define an ellipsoid to solve geodesic problems on

v = False # Verbose logging - toggles whether aircraft update messages are printed to the log

def log(strn):
    now = time.strftime('%H:%M:%S')
    print(now, strn)
    f_log.write(now + ' ' + strn + '\n')

class Plane:
    def __init__(self, addr):
        self.addr = addr # ICAO address
        self.seen = None # Timestamp of last message
        self.call = 'UNKNOWN' # Callsign
        self.cat = 'UNKNOWN' # Category
        self.sprite = 'Large' # Sprite to display
        
        self.pos = [] # Current position in Lat, Lon coordinates
        self.alt = [] # Array of altitudes (feet)
        
        self.gspd = None # Ground speed (knots)
        self.aspd = None # Air speed (knots), this one seems largely unused.
        self.hdg = None # Heading
        self.clm = None # Climb rate (ft / min)
        self.vel_t = None # Timestamp of the previous velocity message
        
        # Aircraft velocity, used for estimating position between messages
        self.vel = None
        self.azi = None # Azimuth - this is the direction of travel along the ground, and is defined as anti-clockwise from East
        
        # Require 2 position messages to initially decode the position, so save the previous one here
        self.old_msg = None # Store the previous position message
        self.old_odd = None # Message parity: 0 = Even, 1 = Odd
        self.old_t = None # Timestamp of the previous position message

# Checks whether an aircraft's calculated velocity is exceedingly different from its broadcast velocity, and falls back to the broadcast velocity if needed
def vel_check(plane):
    if plane.azi and plane.gspd and (plane.vel/(plane.gspd * kt) + (plane.gspd * kt)/plane.vel > 3 or (180 - abs(abs(90 - plane.hdg - plane.azi) - 180)) > 15):
        plane.azi = 90 - plane.hdg
        plane.vel = plane.gspd * kt

def parser(strm, traffic):
    while not cease.is_set():
        # dump1090 performs error checking and necessary corrections, so no need for any of that here
        msg = strm.readline().rstrip()[1:-1] # Read a single line from the TCP stream
        df = pms.df(msg) # Get the downlink format of this message
        if not (df == 17 or df == 18):
            continue # Discard this message if it's not one we want
            
        with traffic_l: # Acquire traffic lock
            addr = pms.icao(msg) # Get the ICAO address
            plane = traffic.get(addr) # Get the corresponding plane if it exists
            if not plane:
                if v: log('Aircraft ' + addr + ' discovered')
                plane = Plane(addr) # If it doesn't, create a new plane
                traffic[addr] = plane
            
            plane.seen = time.time()
            tc = pms.typecode(msg) # Get the message typecode
            
# Callsign
            if tc >= 1 and tc <= 4:
                plane.call = pms.adsb.callsign(msg).replace('_', ' ').strip()
                ec = int(msg[9], 16) & 0b0111 # Get the emitter category
                if tc != 1 and ec: # Typecode 1 is reserved, and an ec of 0 means the data is unavailable.
                    plane.cat = cats[tc * 10 + ec]
                    sprite = sprites.get(tc * 10 + ec)
                    if sprite: plane.sprite = sprite # Set the aircraft sprite if one is available
                elif not ec:
                    plane.cat = 'Unavailable'
                else:
                    plane.cat = 'Reserved'
                
                if v: log('Updated aircraft ' + addr + ' callsign: ' + plane.call + ' and category: ' + plane.cat + ' (TC = {:d}, EC = {:d})'.format(tc, ec))
            
# Position
            elif tc >= 9 and tc <= 18:
                if plane.pos: # A position reference can be used to decode a single message once a fix is achieved
                    plane.pos.append(pms.adsb.position_with_ref(msg, plane.pos[-1][0], plane.pos[-1][1]))
                    plane.alt.append(pms.adsb.altitude(msg))
                    # Solve the inverse geodesic problem to calculate the aircraft's velocity
                    # This tends to be more reliable than the broadcast velocity for predicting the aircraft's current position
                    disp = np.array(geo.inverse(plane.pos[-2], plane.pos[-1]))
                    plane.vel = disp[0, 0] / (plane.seen - plane.old_t)
                    plane.azi = disp[0, 2]
                    # A very large displacement in a short space of time usually indicates a corrupt position, try again with fresh position messages
                    if plane.gspd and plane.vel > plane.gspd * kt * 8: # 8 times broadcast speed seems to be a reasonable threshold
                        log('Warning: Aircraft ' + addr + ' moved faster than expected -\nCalculated {:.1f} m/s, received {:.1f} m/s\n\
...Verifying position...'.format(plane.vel, plane.gspd * kt))
                        plane.pos = [] # Erase position history
                        plane.old_msg = None # Reset old message to ensure a fresh pair
                        plane.old_odd = None
                        plane.old_t = None
                        continue
                        
                else: # If we don't have a position fix yet
                    odd = (int(msg[13], 16) >> 2) & 1 # Get the message parity. One day I'll remember there's two hex characters to a byte...
                    # If we have an old message saved and one message is odd and the other is even...
                    if plane.old_msg and plane.old_odd ^ odd:
                        if odd: # If the new message is the odd one
                            plane.pos.append(pms.adsb.position(plane.old_msg, msg, plane.old_t, plane.seen))
                        else:
                            plane.pos.append(pms.adsb.position(msg, plane.old_msg, plane.seen, plane.old_t))
                        
                        # Occasionally, an aircraft position will somehow be calculated as None. Catch this before it breaks anything
                        if plane.pos[-1] == None:
                            log('Warning: Aircraft ' + addr + ' position was found to be None')
                            plane.pos.pop(-1) # Remove the faulty position
                            plane.old_msg = msg
                            plane.old_odd = odd
                            plane.old_t = plane.seen
                            continue
                        
                        plane.alt.append(pms.adsb.altitude(msg))
                        # Find where the plane was when it sent the old message to get the velocity azimuth
                        pos_old = pms.adsb.position_with_ref(plane.old_msg, plane.pos[-1][0], plane.pos[-1][1])
                        disp = np.array(geo.inverse(pos_old, plane.pos[-1]))
                        plane.vel = disp[0, 0] / (plane.seen - plane.old_t)
                        plane.azi = disp[0, 2]
                        
                    else: # The messages are useless on their own or if they have the same parity, so save this message and wait for another one.
                        plane.old_msg = msg
                        plane.old_odd = odd
                
                # Verify the calculated velocity, unless it's been too long since the last velocity message
                # This should prevent aircraft from drifting around corners
                if plane.vel_t and plane.seen - plane.vel_t < 5: vel_check(plane)
                
                plane.old_t = plane.seen # Timestamp of most recent position
                
                if v:
                    if plane.pos:
                        log('Updated aircraft ' + addr + ' position: {:.5f} N, {:.5f} E, {:d} ft'.format(plane.pos[-1][0], plane.pos[-1][1], plane.alt[-1]))
                    else:
                        log('Updated aircraft ' + addr + ' position: No fix yet, initial message saved')
            
# Velocity
            elif tc == 19:
                try:
                    spd, plane.hdg, plane.clm, spd_t = pms.adsb.velocity(msg)
                except TypeError: # Very rarely, the velocity calculation will return None. Catch this before it breaks anything
                    log('Warning: Failed to update aircraft ' + addr + ' velocity due to a TypeError')
                    continue
                if spd_t == 'GS': # Check whether we got a ground speed or air speed
                    plane.gspd = spd
                    if v: log('Updated aircraft ' + addr +
                              ' velocity: Ground speed = {:d} kt, Heading = {:.1f} deg, Climb rate = {:d} ft/min'.format(plane.gspd, plane.hdg, plane.clm))
                else:
                    plane.aspd = spd
                    if v: log('Updated aircraft ' + addr +
                              ' velocity: Air speed = {:d} kt, Heading = {:.1f} deg, Climb rate = {:d} ft/min'.format(plane.aspd, plane.hdg, plane.clm))
                
                # Update velocity if needed
                vel_check(plane)
                plane.vel_t = plane.seen # Timestamp of most recent velocity
                
            else:
                pass # Unrecognised typecode

# Keeps track of air traffic and updates the map
def atc():
    new_plane_data = dict(img = [], x = [], y = [], rot = [], hb = [], addr = [], call = [], cat = [], alt = [], hdg = [], spd = [])
    new_shdw_data = dict(img = [], x = [], y = [], rot = [])
    new_trail_data = dict(x = [], y = [])
    new_path_data = dict(x = [], y = [])
    active = 0 # Number of active aircraft to be displayed
    ded = [] # Aircraft that need to be deleted
    pos = [] # Aircraft lat, lon positions
    azi = [] # Aircraft azimuths
    dst = [] # Aircraft distances travelled since last message
    now = time.time()
    with traffic_l:
        for addr, plane in traffic.items():
            age = now - plane.seen
            if age > 60: # If the plane hasn't been heard from in over a minute
                ded.append(addr) # Mark this plane for deletion
                continue
            ghost = 'Ghost' if age > 30 else '' # If the plane is starting to get old, make it a ghost
            if plane.pos and plane.hdg: # Only show an aircraft if it has all the necessary data. Callsign messages are fairly rare and also non-critical
                active += 1
                new_plane_data['addr'].append(addr)
                new_plane_data['img'].append(wdir + 'static/Sprites/' + plane.sprite + ghost + '.png')
                pos.append(plane.pos[-1])
                azi.append(plane.azi) # This seems to be defined as anti-clockwise from East for some reason
                dst.append(plane.vel * (now - plane.old_t)) # Predicted distance travelled since last position message
                new_plane_data['rot'].append(np.radians(315 - plane.hdg)) # Image sprite rotation
                new_plane_data['call'].append(plane.call)
                new_plane_data['cat'].append(plane.cat)
                new_plane_data['alt'].append(plane.alt[-1])
                new_plane_data['hdg'].append(plane.hdg)
                new_plane_data['spd'].append(plane.gspd if plane.gspd else plane.aspd)
                
                new_shdw_data['img'].append(wdir + 'static/Sprites/' + plane.sprite + ghost + 'Shadow.png')
                new_shdw_data['rot'].append(np.radians(315 - plane.hdg))
                
                if len(plane.pos) > 1: # Draw a trail if we have more than one point for this aircraft
                    pos_hst = np.array(plane.pos)
                    pos_hst_mct = ccrs.GOOGLE_MERCATOR.transform_points(ccrs.PlateCarree(), pos_hst[:,1], pos_hst[:,0])
                    new_trail_data['x'].append(pos_hst_mct[:,0])
                    new_trail_data['y'].append(pos_hst_mct[:,1])
        
        for addr in ded:
            # Save a limited amount of the aircraft's data before deletion
            pos_hst = np.array(traffic.get(addr).pos)
            if len(pos_hst) > 1:
                pos_hst_mct = ccrs.GOOGLE_MERCATOR.transform_points(ccrs.PlateCarree(), pos_hst[:,1], pos_hst[:,0])
                new_path_data['x'].append(pos_hst_mct[:,0])
                new_path_data['y'].append(pos_hst_mct[:,1])
            del traffic[addr] # Delete this aircraft
            if v: log('Aircraft ' + addr + ' deleted')
    
    pos_est = np.array(geo.direct(pos, azi, dst)) # Estimated positions based on old position and displacement vector
    # Note for the confused: transform_points takes coordinates in the form (x, y), which in PlateCaree coordinates ends up as Lon, Lat (instead of the usual Lat, Lon)
    pos_mct = ccrs.GOOGLE_MERCATOR.transform_points(ccrs.PlateCarree(), pos_est[:,1], pos_est[:,0])
    # hb gives all hitbox circles a screen-size of 60. Any phantom circles won't have a size and therefore won't appear. Hopefully.
    new_plane_data.update(x = pos_mct[:,0], y = pos_mct[:,1], hb = [60] * active)
    new_shdw_data.update(x = pos_mct[:,0], y = pos_mct[:,1] - np.array(new_plane_data['alt'])/50) # Offset the shadow vertically based on altitude
    
    planeSprites.stream(new_plane_data, active)
    planeShdws.stream(new_shdw_data, active)
    planeTrails.stream(new_trail_data, active)
    planePaths.stream(new_path_data, 100) # Remember 100 aircraft. Remembering too many could cause performance issues

def stop(ctxt):
    log('...Stopping program...')
    cease.set() # Stop the parsing thread
    
    # Wait for threads to finish
    t_parse.join()
    
    log('...Closing TCP connection...')
    s.close() # Close the TCP connection
    
    log('...Closing dump1090...')
    dmp.terminate() # Exit dump1090
    
    log('Goodbye')
    f_log.close()
    sys.exit(0) # sys.exit works perfectly fine here for some reason

# Stop the server when the bowser window is closed
curdoc().on_session_destroyed(stop) # This can sometimes take quite a while
# Changing --check-unused-sessions or --unused-session-lifetime on server startup might fix this

# When run as a bokeh server, a different namespace is used
wdir = '' if __name__ == '__main__' else 'sdr_adsb/'

f_log = open(wdir + 'log.txt', 'w')
log('...Initialising...')

log('...Starting Dump1090...')
if platform.system() == 'Windows':
    dmp = Popen([wdir + 'static/dump1090-win.1.10.3010.14/dump1090', '--net', '--quiet'])
else:
    dmp = Popen([wdir + 'static/dump1090-master/dump1090', '--net', '--quiet'])

# Connect to Dump1090's TCP stream
HOST = '127.0.0.1'
PORT = 30002
log('...Connecting to Dump1090 at ' + HOST + ' on port {:d}...'.format(PORT))
s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
# If Dump doesn't start up before execution makes it here, the system actively refuses the connection, and no amount of timeout will help.
# Retry connection every second for 10 seconds
try:
    for i in range(0, 10):
        try: s.connect((HOST, PORT))
        except ConnectionRefusedError: # The expected error when the system refuses the connection
            time.sleep(1)
            # Need to redefine the socket on Unix after an attempted connection otherwise it gives an invalid argument error on the next connection attempt
            if platform.system() != 'Windows':
                s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
            if i == 9:
                raise
        except: # In case we get any other kind of error
            raise
        else:
            break # If we didn't get an error, connection succeeded!

except Exception as e:
    log('Unable to connect: ' + repr(e))
    dmp_stat = dmp.poll()
    if dmp_stat:
        log('Dump1090 encountered an error, check the dongle is plugged in properly')
    elif dmp_stat == None:
        log('Dump1090 seems to be working fine, but couldn\'t be connected to\n\
Try checking the permissions for ' + HOST + ':' + repr(PORT))
        dmp.terminate() # dump1090 is still running if its status is None, kill it
    else:
        log('Dump1090 quit unexpectedly')
    log('...Exiting...')
    f_log.close()
    collect()
    _exit(1) # This is not a clean exit, but it's the only one that works (sys.exit raises an exception, but does not stop the server)

strm = s.makefile() # Convert it to a file-like object to make use of the newlines dump1090 spits out
log('Connected')

log('...Starting parse thread...')
# Create threads
cease = Event() # Informs the parsing thread when it's time to end
traffic = {} # Used to store aircraft data
traffic_l = Lock() # Thread safety
t_parse = Thread(target = parser, args = [strm, traffic])
t_parse.start()

log('...Creating map...')
u_lat, u_lon = ip('me').latlng # User's position. Can sometimes be quite inaccurate
log('User found at {:.5f} N, {:.5f} E'.format(u_lat, u_lon))
u_pos = ccrs.GOOGLE_MERCATOR.transform_point(u_lon, u_lat, ccrs.PlateCarree())

# Create an empty plot in Mercator coordinates. sizing_mode expands the plot to fill the whole screen
# Important note: cartopy has two types of Mercator projections: Mercator() and GOOGLE_MERCATOR which are slightly different
# bokeh's implementation of the Mercator projection is equivalent to cartopy's GOOGLE_MERCATOR projection (hence its use in atc())
p = figure(x_range=(u_pos[0] - 200000, u_pos[0] + 200000), y_range=(u_pos[1] - 200000, u_pos[1] + 200000), x_axis_type="mercator", y_axis_type="mercator",
       toolbar_location = None, tools = 'pan,wheel_zoom', sizing_mode = 'stretch_both')

# Map selection:
#p.add_tile(WMTSTileSource(url = 'https://tiles.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'))
p.add_tile(WMTSTileSource(url = 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'))
#p.add_tile(WMTSTileSource(url = 'http://c.tile.stamen.com/watercolor/{Z}/{X}/{Y}.jpg'))

p.select_one(WheelZoomTool).zoom_on_axis = False # Disable single axis zooming
p.toolbar.active_scroll = p.select_one(WheelZoomTool) # Make the scroll wheel the active zoom tool

# Define the glyphs for the plot. Some of these arguments correspond to ColumnDataSource columns
# Due to an issue with bokeh, image sprites cannot be rotated about their centres, hence the requirement for all noses in the top-left
plane_sprite = ImageURL(url = 'img', x = 'x', y = 'y', w = None, h = None, angle = 'rot', anchor = 'top_left')
plane_shdw = ImageURL(url = 'img', x = 'x', y = 'y', w = None, h = None, angle = 'rot', anchor = 'top_left')
# Make-shift hitbox for tooltips since image glyphs don't support the hovertool
circ = Circle(x = 'x', y = 'y', size = 'hb', line_alpha = 0, fill_alpha = 0)
plane_trail = MultiLine(xs = 'x', ys = 'y', line_color = '#FFFF00', line_width = 2)
plane_trail_shdw = MultiLine(xs = 'x', ys = 'y', line_color = '#000000', line_width = 4)
plane_paths = MultiLine(xs = 'x', ys = 'y', line_color = '#0000FF', line_width = 3, line_alpha = 0.2, line_cap = 'round', line_join = 'round')

# The order of these is important, and determines which glyphs are rendered on top of others. The later a glyph is added, the higher its level
p.add_glyph(planePaths, plane_paths) # Historic flight paths
p.add_glyph(planeTrails, plane_trail_shdw) # Aircraft trail borders
p.add_glyph(planeTrails, plane_trail) # Arcraft trails
p.add_glyph(planeShdws, plane_shdw) # Aircaft shadows
ccl = p.add_glyph(planeSprites, circ) # Aircraft tooltip hitboxes
p.add_glyph(planeSprites, plane_sprite) # Aircraft sprites

# Tooltips (restricted to only appear for the make-shift hitboxes)
p.add_tools(HoverTool(renderers = [ccl],
                      tooltips = [('ICAO', '@addr'), ('Flight', '@call'), ('Category', '@cat'), ('Altitude', '@alt ft'), ('Heading', '@hdg°'), ('Speed', '@spd kt')]))

curdoc().add_root(p) # Add the plot to the window
curdoc().title = "SDR Aircraft Tracker" # Give the window a name
curdoc().add_periodic_callback(atc, 100) # Update map every 100 ms

log('Initialisation complete')
