import pandas as pd
import numpy as np
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from operator import add
from uszipcode import SearchEngine
import gmplot
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint
from geopy.distance import great_circle
import random
import math
import haversine as hs

apikey = "AIzaSyDv0JWXkfts9An4XKSkHXgrU0SxEyOu2CQ"

def clusters_by_county(city, state="CA"):
    conf = SparkConf()
    conf.setMaster("local").setAppName("My app")
    sc = SparkContext(conf=conf)

    # Columns : ['Data Year', 'Fuel Type', 'ZIP', 'Number of Vehicles']
    data = sc.textFile("sales.csv").filter(lambda row : row.split(',')[2] != 'ZIP')
    # (zip, number of vehicles)
    data_rdd = data.map(lambda row : (row.split(',')[2], int(row.split(',')[3])))
    data_existing_chargers = pd.read_csv('alt_fuel_stations.csv', usecols=['Latitude', 'Longitude'])
    existing_chargers = data_existing_chargers[['Latitude', 'Longitude']].values.tolist()

    # not real zipcodes?
    fake_zips = ["94003", "94029", "92670", "92680", "99999"]
    zipcode_sales = data_rdd.reduceByKey(add).filter(lambda row : row[0] not in fake_zips) \
        .sortBy(lambda row : -row[1]).collectAsMap()
    # https://uszipcode.readthedocs.io/01-Usage-Example/index.html
    # https://uszipcode.readthedocs.io/02-Advanced-Tutorial/index.html
    search = SearchEngine()
    source_result = search.by_city_and_state(city=city, state=state)[0]
    source_latlng = tuple([source_result.lat, source_result.lng])

    def latlng_from_zip(zipcode):
        result = search.by_zipcode(zipcode)
        return tuple([float(result.lat), float(result.lng)])
    latlng_sales = {}
    for zipcode in zipcode_sales:
        lat_lng = latlng_from_zip(zipcode)
        # https://pypi.org/project/haversine/
        if hs.haversine(source_latlng, lat_lng, unit='mi') < 100:
            latlng_sales[lat_lng] = zipcode_sales[zipcode]
    potential_locations = list(latlng_sales.keys())

    def get_centermost_point(cluster):
        centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
        centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
        return tuple(centermost_point)
    charging_stations = []
    for station in existing_chargers:
        if hs.haversine(source_latlng, station, unit='mi') < 100:
            charging_stations.append(tuple(station))

    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.OPTICS.html
    # cluster existing charger locations to get clusters of "coverage"
    # # haversine distance uses radians
    # # 5 miles
    miles_per_radian = 3959
    db = DBSCAN(eps=(5 / miles_per_radian), min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(charging_stations))
    clusters_chargers = sc.parallelize(db.labels_).zipWithIndex().map(lambda row : (row[0], charging_stations[row[1]])).groupByKey().map(lambda row : (row[0], list(row[1])))
    # find the point in each cluster that is closest to its centroid
    charger_cluster_center_points = clusters_chargers.map(lambda row : get_centermost_point(row[1])).collect()
    print("{:,} charger points clustered to {:,} points, {:.3f}.".format(len(charging_stations), len(charger_cluster_center_points), len(charger_cluster_center_points) / len(charging_stations)))
    # add noise, (num_clusters) data points at random from our original set of all chargers charging_stations
    # # don't want to completely remove dense sequences of chargers
    random_samples = random.sample(charging_stations, len(charger_cluster_center_points))
    charger_cluster_center_points.extend(random_samples)
    db_noise = DBSCAN(eps=(0.1 / miles_per_radian), min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(charger_cluster_center_points))
    clusters_noise = sc.parallelize(db_noise.labels_).zipWithIndex().map(lambda row : (row[0], charger_cluster_center_points[row[1]])).groupByKey().map(lambda row : (row[0], list(row[1])))
    charger_cluster_center_points_noise = clusters_noise.map(lambda row : get_centermost_point(row[1])).collect()
    print("{:,} charging points at conclusion of clustering.".format(len(charger_cluster_center_points_noise)))

    # https://pypi.org/project/gmplot/
    # https://developers.google.com/maps/documentation/javascript/overview#zoom-levels
    # https://github.com/gmplot/gmplot/wiki/GoogleMapPlotter.scatter
    # 100 mile radius map view of demand points that will be used in clustering
    gmap = gmplot.GoogleMapPlotter(lat=source_latlng[0], lng=source_latlng[1], zoom=10, apikey=apikey)
    gmap.scatter(*zip(*potential_locations))
    gmap.draw('city-ev-demand-map.html')

    # cluster sales data points to get clusters of "demand"
    # # 5 miles
    db = DBSCAN(eps=(5 / miles_per_radian), min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(potential_locations))
    clusters = sc.parallelize(db.labels_).zipWithIndex().map(lambda row : (row[0], potential_locations[row[1]])).groupByKey().map(lambda row : (row[0], list(row[1])))
    cluster_center_points = clusters.map(lambda row : get_centermost_point(row[1])).collect()
    print("{:,} demand points clustered to {:,} points, {:.3f}.".format(len(potential_locations), len(cluster_center_points), len(cluster_center_points) / len(potential_locations)))
    # add noise, (num_clusters) data points at random from our original set of all sales potential_locations
    # # visually, want some predictions that are near each other
    random_samples = random.sample(potential_locations, len(cluster_center_points))
    cluster_center_points.extend(random_samples)
    db_noise = DBSCAN(eps=(0.1 / miles_per_radian), min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(cluster_center_points))
    clusters_noise = sc.parallelize(db_noise.labels_).zipWithIndex().map(lambda row : (row[0], cluster_center_points[row[1]])).groupByKey().map(lambda row : (row[0], list(row[1])))
    cluster_center_points_noise = clusters_noise.map(lambda row : get_centermost_point(row[1])).collect()
    print("{:,} demand points at conclusion of clustering.".format(len(cluster_center_points_noise)))

    final_predicted_locations = []
    for potential_location in cluster_center_points_noise:
        covered = False
        for charger in charger_cluster_center_points:
            if hs.haversine(potential_location, charger, unit='mi') <= 5:
                covered = True
                break
        if not covered:
            final_predicted_locations.append(potential_location)

    print("{:,} points without a current charger within 5 miles.".format(len(final_predicted_locations)))

    gmap = gmplot.GoogleMapPlotter(lat=source_latlng[0], lng=source_latlng[1], zoom=10, apikey=apikey)
    gmap.scatter(*zip(*final_predicted_locations), color='red')
    miles_per_meter = 0.000621371
    gmap.scatter(*zip(*charger_cluster_center_points), color='green', marker=False, size=(5/miles_per_meter))
    gmap.draw('new-charger-potential_locations.html')


clusters_by_county("Los Angeles")