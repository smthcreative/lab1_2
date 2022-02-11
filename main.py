'''
Program     
'''
from os import name
import folium, argparse, re
from geopy.geocoders import Nominatim
import geopy
from haversine import haversine


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type = int, help = 'choose year')
    parser.add_argument('latitude', type = float, help = 'latitude')
    parser.add_argument('longtitude', type = float, help = 'longtitude')
    parser.add_argument('path', type = str, help = 'path to file')
    args = parser.parse_args()
    print((args.year, args.latitude, args.longtitude, args.path))
    return (args.year, args.latitude, args.longtitude, args.path)


def read_list(year:int, path:str):
    '''
    Function read file with film name and their location
    Return list of movie filmed in current year
    >>> read_list(2015, '/home/buraknext/python /2s/locations.list')[1]
    ['Zhong Kui fu mo: Xue yao mo ling', 2015, 'Zhejiang, China', (29.0000001, 119.9999999)]
    '''
    with open(path, 'r', encoding='UTF-8', errors='ignore') as file:
        current_year = '(' + str(year) + ')'
        films = [x.strip().split() for x in file.readlines() if current_year in x]
        final = []
        for item in films:
            index = item.index(current_year)
            first_part = ' '.join(item[:index])
            first_part = first_part.replace('#', '')
            second_part = ' '.join(item[index + 1:])
            second_part = re.sub(r'\([^()]*\)', '', second_part)
            second_part = re.sub(r'\{[^()]*\}', '', second_part)
            coordinate = find_location(second_part)
            if coordinate is not None:
                final.append([first_part, year, second_part, coordinate])
    return final


def find_location(name):
    '''
    Function find coordinate of location
    >>> find_location('Coventry,West Midlands,England,UK')
    (52.4081812, -1.510477)
    '''
    geolocator = Nominatim(timeout = 10, user_agent="notme")
    try:
        location = geolocator.geocode(name)
        if location is not None:
            return (location.latitude, location.longitude)
    except AttributeError:
        return None


def distance(lat1, lon1, lat2, lon2):
    '''
    Function search distance between two points on the map
    >>> distance(49.817545, 24.023932, 52.4081812, 1.510477)
    988.5919790888222
    '''

    return haversine((lat1, lon1), (lat2, lon2), unit= 'mi')


def nearest_point(lat1, lon1, list_of_point):
    '''
    Function find distance between point with 
    coordinate (lat1;lon1) and point where movie 
    was filmed. Return sorted list of point. Key is 
    distance from lowest to biggest.
    >>> nearest_point(49.817545, 24.023932, [['Zhong Kui fu mo: Xue yao mo ling', 2015, 'Zhejiang, China', (29.0000001, 119.9999999)]])
    [['Zhong Kui fu mo: Xue yao mo ling', 2015, 'Zhejiang, China', (29.0000001, 119.9999999), 4963.81211167831]]
    '''
    for point in list_of_point:
        dist = distance(lat1, lon1, point[3][0], point[3][1]) 
        point.append(dist)
    return sorted(list_of_point, key=lambda length: length[-1])


def create_map(lat1, lon1, list_of_point):
    '''
    Function create map with 10 nearest and
    10 fathermost point
    '''
    print(len(list_of_point))
    map = folium.Map(tiles="Stamen Terrain",
        location=[49.817545, 24.023932],
        zoom_start=17)
    fg1 = folium.FeatureGroup(name="Film_nearest")

    coordinate_used = set()
    for film in list_of_point:
        if (film[3][0], film[3][1]) in coordinate_used:
            continue
        fg1.add_child(folium.Marker(location=[film[3][0], film[3][1]], popup=film[0],icon=folium.Icon()))
        coordinate_used.add((film[3][0], film[3][1]))
        if len(coordinate_used) == 10:
            break

    fg2 = folium.FeatureGroup(name="Film_fathermost")
    for film in reversed(list_of_point):
        if (film[3][0], film[3][1]) in coordinate_used:
            continue
        fg2.add_child(folium.CircleMarker(location=[film[3][0], film[3][1]], raddius = 10, color='red', popup=film[0], fill_color='green', fill_opacity=0.5))
        coordinate_used.add((film[3][0], film[3][1]))
        if len(coordinate_used) == 20:
            break

    map.add_child(fg1)
    map.add_child(fg2)
    map.add_child(folium.LayerControl())
    map.save('_Map_.html')


def main():
    arg = arguments()
    films_of_year = read_list(arg[0], arg[3])
    point = nearest_point(arg[1], arg[2], films_of_year)
    create_map(arg[1], arg[2], point)


if __name__ == '__main__':
    main()
