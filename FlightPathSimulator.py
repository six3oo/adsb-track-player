""" Dynamically generates a randomized conical flight path from initial values

-------------------------------------------------------
mutex protection occurs when calling replace_message
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import random
import datetime, math
from math import asin, atan2, cos, degrees, radians, sin
from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

REFRESH_RATE = 5

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
	"""
	lat: initial latitude, in degrees
	lon: initial longitude, in degrees
	d: target distance from initial, in km
	bearing: (true) heading in degrees
	R: optional radius of sphere, defaults to mean radius of earth in km
	Returns new lat/lon coordinate {d}km from initial, in degrees
	"""
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	a = radians(bearing)
	lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
	lon2 = lon1 + atan2(
		sin(a) * sin(d/R) * cos(lat1),
			cos(d/R) - sin(lat1) * sin(lat2)
	)
	return (degrees(lat2), degrees(lon2))

class FlightPathSimulator(AbstractTrajectorySimulatorBase):
	def __init__(self,mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile,duration):
		super().__init__(mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile,duration)
		self._starttime = datetime.datetime.now(datetime.timezone.utc)
		self._icao = str(aircraftinfos.icao)
		self._lat0 = aircraftinfos.lat_deg
		self._lon0 = aircraftinfos.lon_deg

		self._alt_m = aircraftinfos.alt_msl_m
		self._speed_mps = aircraftinfos.speed_mps
		self._duration = duration
		self._generate = True
		self.counter = 0

	def refresh_delay(self):
		return REFRESH_RATE

	def update_aircraftinfos(self):
		dist_spd = ((self._speed_mps * 1.852)/3600)*REFRESH_RATE

		##### PRE-GENERATION PROTOTYPE CODE #####
		"""
                if self._generate:
                        dist_spd = ((self._speed_mps * 1.852)/3600)
                        genLat = self._aircraftinfos.lat_deg
                        genLon = self._aircraftinfos.lon_deg
                        genAlt = self._aircraftinfos.alt_msl_m
                        genSpd = self._aircraftinfos.speed_mps
                        genTrk = self._aircraftinfos.track_angle_deg
                        flightPath = []

                        # Pre-generate flight path strings to list
                        for i from 1 to self._duration:
                                dataFrame = self._aircraftinfos.callsign+','+(str)genLat+','+(str)genLon+','+(str)genAlt+','+(str)genSpd+','+(str)genTrk
                                flightPath.append(dataFrame)
                                # Calculate new Lat/Lon based on Speed+Track Angle
                                genLat, genLon = get_point_at_distance(genLat, genLon, dist_spd, genTrk)
                                # Randomized trajectory cone
                                genAlt += random.uniform(-5,5)
                                genSpd += random.uniform(-10,10)
                                genTrk+= random.uniform(-3,3)

                        # Write generated flight path to temp file
                        with open('spoof.csv','a') as spoof:
                                for frame in flightPath:
                                        spoof.write(frame)

                        # temp file spoof.csv format: "<0:callsign>,<1:lat>,<2:lon>,<3:alt>,<4:speed>,<5:track angle>"
                        self._generate = False
                else:
                        with open('spoof.csv', 'r') as spoof:
                                for self._counter in spoof:
                                        posi = line.split(',')
                                        self._aircraftinfos.lat_deg = posi[1]
                                        self._aircraftinfos.lon_deg = posi[2]
                                        self._aircraftinfos.alt_msl_m = posi[3]
                                        self._aircraftinfos.speed_mps = posi[4]
                                        self._aircraftinfos.track_angle_deg = posi[5]
                        
		"""

		
		self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg = get_point_at_distance(self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg, dist_spd, self._aircraftinfos.track_angle_deg)

                # Randomized trajectory cone
		self._aircraftinfos.speed_mps += random.uniform(-10,10)
		self._aircraftinfos.track_angle_deg += random.uniform(-3,3)
		self._aircraftinfos.alt_msl_m += random.uniform(-5,5)

                # Track Angle 0-360 wrapping
		if self._aircraftinfos.track_angle_deg < 0:
			self._aircraftinfos.track_angle_deg += 360
		elif self._aircraftinfos.track_angle_deg > 360:
			self._aircraftinfos.track_angle_deg -= 360
        
		print("[!] FLIGHT SIM\t\tICAO: "+self._icao+"\t\tCallsign: "+self._aircraftinfos.callsign)
		print("    [:] Lat: "+str(self._aircraftinfos.lat_deg)+" | Lon: "+str(self._aircraftinfos.lon_deg)+" | Alt: "+str(self._aircraftinfos.alt_msl_m)+" | Spd: "+str(self._aircraftinfos.speed_mps)+" | Trk Angle: "+str(self._aircraftinfos.track_angle_deg))

		#Write to logfile -> CSV format: DATETIME,CALLSIGN,LAT,LONG,ALT,SPD,TRKANGLE
		with open(self._logfile,"a") as fLog:
			now=str(datetime.datetime.now())
			fLog.write("\n"+now+","+self._aircraftinfos.callsign+","+str(self._aircraftinfos.lat_deg)+","+str(self._aircraftinfos.lon_deg)+","+str(self._aircraftinfos.alt_msl_m)+","+str(self._aircraftinfos.speed_mps)+","+str(self._aircraftinfos.track_angle_deg))
