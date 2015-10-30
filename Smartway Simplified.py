##Smartway Server Service
##By Bartek Juszczak
##29/10/2015

import googlemaps
import requests
import time
import sys
from math import *
import math
import subprocess
try_counter = 0
while 1:
    try:
        gmaps = googlemaps.Client(key='AIzaSyB4J5fM_flIzbEpT8FE-s1LNUejVJqkVwQ')
        break
    except:
        time.sleep(3)
        print "\n\nI was really hoping this would never happen but, Google Maps failed to repsond in any way."
        print "\nRetrying..."
        if try_counter < 5:
            try_counter += 1
            time.sleep(3)
            continue
        else:
            print "\n\nGiving up\n\n"
            sys.exit()

toDoApp={"Pickup dry cleaning":"100C High St, Feltham TW13 4EX", "Buy new toothbrush":"667 Staines Rd, Feltham TW14 8PA"}
facebook={"Facebook check-in from Mark":"Gate 23, Heathrow Airport, London TW6 3XA"}
loyaltyCards ={"Costa Coffee":"Expiry = 2016"}

##def webPageCreator(coordinates):

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return 0.846541* c * r  ## Distance in km

def degToRad(deg):
    return deg * pi / 180

def radToDeg(rad):
    return rad * 180 /pi

def boxToCentre(coords):
    a = []
    b = []
    c = []
    n = len(coords)
    for item in coords:
        a += [cos(degToRad(item[0])) * cos(degToRad(item[1]))]
        b += [cos(degToRad(item[0])) * sin(degToRad(item[1]))]
        c += [sin(degToRad(item[0]))]
    x = (a[0] + a[1] + a[2] + a[3]) / n
    y = (b[0] + b[1] + b[2] + b[3]) / n
    z = (c[0] + c[1] + c[2] + c[3]) / n
    lonFinal = atan2(y, x)
    hyp = sqrt(x * x + y * y)
    latFinal = atan2(z, hyp)
    return str(radToDeg(lonFinal))+","+str(radToDeg(latFinal))

def googleMapsDirections(origin,destination,waypoints):
    global gmaps
    if len(waypoints) > 0:
        waypoints = ["optimize:true",waypoints]
        print waypoints
        gMapsResult = gmaps.directions(origin=origin,
                                     destination = destination,
                                     mode="walking",
                                   waypoints = waypoints)
    else:
        gMapsResult = gmaps.directions(origin=origin,
                             destination = destination,
                             mode="walking")
    coord_number = 0
    initialPath = {}
    initialPath['coordinates'] = []
    initialPath['duration'] = 0
    initialPath['destination'] = destination
    initialPath['origin'] = origin
    if len(gMapsResult) < 1:
        return False
    for item0 in gMapsResult[0]['legs']:
        initialPath['duration'] += int(item0['duration']['text'].split()[0])
        initialPath['distance'] =  item0['distance']['value']
        for item in item0['steps']:
            startLat = str(item['start_location']['lat'])
            startLng = str(item['start_location']['lng'])
            endLat = str(item['end_location']['lat'])
            endLng = str(item['end_location']['lng'])
            initialPath['coordinates'] += [startLat + "," + startLng] + [endLat + "," + endLng]
            ##print "new google.maps.LatLng(" + startLat + "," + startLng + "),"
            ##print "new google.maps.LatLng(" + endLat + "," + endLng + "),"
    return initialPath

def getNearbyPlaces(coordPoint,pType,destination,radius, origin, waypoints, timelimit = 0):
    coords = coordPoint.split(",")
    Lat = coords[0]
    Lng = coords[1]
    results = []
    request = requests.get("https://maps.googleapis.com/maps/api/place/nearby\
search/json?location=" + Lat + "," + Lng + "&radius=" + radius + "&types=" + pType + "&key=AIzaSyB4J5fM_flIzbEpT8FE-s1LNUejVJqkVwQ").json()
    for item in request['results']:
        pLat = str(item['geometry']['location']['lat'])
        pLng = str(item['geometry']['location']['lng'])
        if len(waypoints) < 1:
            waypoints = [pLat + ", " + pLng]
        else:
            waypoints += [pLat + ", " + pLng]
        newPath = googleMapsDirections(origin,destination ,pLat + ", " + pLng)
        if newPath == False:
            continue
        ##results[str(item['name'].encode('utf8', 'replace'))] = [newPath['duration'],newPath['coordinates']]
        results += [[str(item['name'].encode('utf8', 'replace')), newPath['duration'],newPath['coordinates'],pLat + "," + pLng]]
    return results

def mainThread(origin,destination):
    global toDoApp
    global facebookCisco 
    try:
        waypointsMain[0]
    except:
        waypointsMain = []
    while 1:
        initialRoute = googleMapsDirections(origin, destination, waypoints = waypointsMain) ## keys = duration,origin,destination,coordinates,distance
        extras = ['food','cafe','atm','pharmacy']
        placeTypes = {}
        startCoordinates = map(float,initialRoute['coordinates'][0].split(","))
         finishCoordinates = map(float,initialRoute['coordinates'][-1].split(","))
        midpointResult = boxToCentre([[startCoordinates[1],startCoordinates[0]],[finishCoordinates[1],finishCoordinates[0]],[startCoordinates[1],startCoordinates[0]],[finishCoordinates[1],finishCoordinates[0]]])
        print "Your current route would take you " + str(initialRoute['duration']) + " minutes.\n"
        print "Here are some places you might want to visit on your way:\n"
        print "*****To-Do*****\n"
        for item in toDoApp:
            newRoute = googleMapsDirections(origin,destination ,waypointsMain + [toDoApp[item]])
            print item + " +" + str(newRoute['duration'] - initialRoute['duration']) + " mins"
        print "\n"
        print "*****Social*****\n"
        for item in facebook:
            newRoute = googleMapsDirections(origin,destination ,waypointsMain + [facebook[item]])
            print item + " +" + str(newRoute['duration'] - initialRoute['duration']) + " mins"
        print ""
        for place in extras:
            placeTypes[place] = getNearbyPlaces(coordPoint=midpointResult,pType=place,destination=initialRoute['destination'],origin = origin,radius=str((initialRoute['distance']/2 + 200)),waypoints=waypointsMain)[:5]
        for item in placeTypes:
            print "*****" + item.title() + "*****\n"
            for item in placeTypes[item]:
                item[1] = item[1] - initialRoute['duration']
                loyalty = ""
                if item[0]in loyaltyCards:
                    loyalty = " ----- You have a loyalty card for here :)"
                print item[0] + " +" +  str(item[1]) + " mins" + loyalty
            print ""
        userChoice = raw_input("")

        for item in placeTypes: 
            for item in placeTypes[item]:
                if userChoice == item[0]:
                    waypointsMain = str(item[3])
        if userChoice == "go":
            print "Went"
            time.sleep(1000)
                    
            





        
origin = raw_input("Please enter your starting location: ")
destination = raw_input("\nPlease enter your destination: ")
print "\n" * 100
mainThread(origin,destination)


##sample = googleMapsDirections(origin="Cisco,Feltham", destination="Heathrow Airport")
##getNearbyPlaces(sample['coordinates'][0],20,"food",destination="Heathrow Airport",radius="1000")

    
