##Smartway Server Service
##By Bartek Juszczak
##29/10/2015

import googlemaps
import requests
import time
import sys
from math import *
try_counter = 0
while 1:
    try:
        gmaps = googlemaps.Client(key='AIzaSyAheqofU3G47Z27K00foE1Zbm_rhAlhFGc')
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

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return 0.846541* c * r  ## Distance in km

def googleMapsDirections(origin,destination,waypointsString = False):
    global gmaps
    if waypointsString == False:
        gMapsResult = gmaps.directions(origin=origin,
                                         destination = destination,
                                         mode="walking")
    else:
        waypoints = ["optimize:true",waypointsString]
        gMapsResult = gmaps.directions(origin=origin,
                                         destination = destination,
                                         mode="walking",
                                       waypoints = waypoints)
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
        for item in item0['steps']:
            startLat = str(item['start_location']['lat'])
            startLng = str(item['start_location']['lng'])
            endLat = str(item['end_location']['lat'])
            endLng = str(item['end_location']['lng'])
            initialPath['coordinates'] += [startLat + "," + startLng] + [endLat + "," + endLng]
            ##print "new google.maps.LatLng(" + startLat + "," + startLng + "),"
            ##print "new google.maps.LatLng(" + endLat + "," + endLng + "),"
    return initialPath

def getNearbyPlaces(coordPoint,pType,destination,radius,timelimit = 0):
    coords = coordPoint.split(",")
    Lat = coords[0]
    Lng = coords[1]
    results = {}
    request = requests.get("https://maps.googleapis.com/maps/api/place/nearby\
search/json?location=" + Lat + "," + Lng + "&radius=" + radius + "&types=" + pType + "&key=AIzaSyAheqofU3G47Z27K00foE1Zbm_rhAlhFGc").json()
    for item in request['results']:
        pLat = str(item['geometry']['location']['lat'])
        pLng = str(item['geometry']['location']['lng'])
        newPath = googleMapsDirections(coordPoint,destination ,pLat + ", " + pLng)
        if newPath == False:
            continue
        results[str(item['name'].encode('utf8', 'replace'))] = [newPath['duration'],newPath['coordinates']]
    return results

def mainThread():
    origin = "Cisco,Feltham" ## !!Will be received from app!!
    destination = "Heathrow Airport" ## !!Will be received from app!!
    initialRoute = googleMapsDirections(origin, destination) ## keys = duration,origin,destination,coordinates
    extras = ['food','cafe','atm','pharmacy']
    placeTypes = {}
    for place in extras:
        placeTypes[place] = {}
    searchRadius = "500"
    coordinateCounter = 0
    distanceBetweenCurrentPointCollection = 0
    distanceSinceLastReset = 1.1
    while coordinateCounter in range(len(initialRoute['coordinates'])):
        currentCoordinatePairAsFloatList = map(float,initialRoute['coordinates'][coordinateCounter].split(","))
        currentP1CoordinatePairAsFloatList =  map(float,initialRoute['coordinates'][coordinateCounter + 1].split(","))
        distanceBetweenCurrentPointCollection += haversine(currentCoordinatePairAsFloatList[0],currentCoordinatePairAsFloatList[1],currentP1CoordinatePairAsFloatList[0],currentP1CoordinatePairAsFloatList[1])
        coordinateCounter += 2
        if distanceBetweenCurrentPointCollection > 1:
            distanceBetweenCurrentPointCollection = 0
            for placeType in extras:
                print placeType
                if placeType == "atm":
                    searchRadius = "1500"
                placeTypes[placeType] = getNearbyPlaces(coordPoint=initialRoute['coordinates'][coordinateCounter+1],pType=placeType,destination=destination,radius=searchRadius)
                print len(placeTypes[placeType])





        
        
mainThread()


##sample = googleMapsDirections(origin="Cisco,Feltham", destination="Heathrow Airport")
##getNearbyPlaces(sample['coordinates'][0],20,"food",destination="Heathrow Airport",radius="1000")

    
