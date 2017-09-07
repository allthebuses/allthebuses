import os
import sys
import requests
import json
import itertools

API="https://api.tfl.gov.uk"
TFL_APP_ID=os.environ['TFL_APP_ID']
TFL_APP_KEY=os.environ['TFL_APP_KEY']
tfl_api = requests.Session()
tfl_api.params={ 'app_id': APP_ID, 'app_key': APP_KEY }

data_dir = 'data'

def main():
    """
    routes = all_routes()
    for id, route in routes.items():
        print(id)
        populate_route_detail(route)
    json.dump(routes, open("all-routes.json", mode="w"))
    """
    routes = json.load(open("data/all-routes.json"))
    json.dump(to_geojson(routes), open("data/all-routes.geojson", mode="w"))

def all_routes():
    routes = {}
    raw = tfl_api.get(API + "/Line/Mode/bus/Route").json()

    for route in raw:
        del route['$type']
        del route['modeName']
        del route['disruptions']
        del route['created']
        del route['modified']
        del route['lineStatuses']
        del route['serviceTypes']
        del route['crowding']

        for section in route['routeSections']:
            del section['$type']
            del section['serviceType']

        routes[route['id']] = route

    return routes

def populate_route_detail(route):
    raw = tfl_api.get(API + '/Line/' + route['id'] + '/Route/Sequence/all')
    raw = raw.json()

    del raw['$type']
    del raw['lineId']
    del raw['lineName']
    del raw['stations']
    del raw['mode']
    del raw['direction']
    del raw['isOutboundOnly']
    del raw['stopPointSequences'] # This is the vverbose set of routes, but does include split/join route segments

    for i in range(len(raw['lineStrings'])):
        raw['lineStrings'][i] = json.loads(raw['lineStrings'][i])

    for lr in raw['orderedLineRoutes']:
        del lr['$type']
        del lr['serviceType']

    return route.update(raw)

def to_geojson(routes):
    doc = { "type": "FeatureCollection", "features": [] }

    for id, route in routes.items():
        ls = route.pop("lineStrings")
        del route['routeSections']
        del route['orderedLineRoutes']
        del route['lineId']
        del route['lineName']

        doc['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "MultiLineString",
                "coordinates": list(itertools.chain.from_iterable(ls))
                },
            "properties": route
            })

    return doc

if __name__ == '__main__':
    sys.exit(main())
