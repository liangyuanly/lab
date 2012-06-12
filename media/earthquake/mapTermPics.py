from matplotlib.patches import Polygon 
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import math


def drawPointsOnJPMap(points):
    m = Basemap(llcrnrlon=129.5, llcrnrlat=30.4, urcrnrlon=147.0, urcrnrlat=45.4, projection='cyl', lat_1=10, lat_2=50, lon_0=138, resolution='l', area_thresh=10000)

    m.drawmapboundary(fill_color='#85A6D9')
    m.fillcontinents(color='white',lake_color='#85A6D9')
    m.drawcoastlines(color='#6D5F47', linewidth=.4)
    m.drawcountries(color='#6D5F47', linewidth=.4)
   
    for point in points:
        x, y = m(point[1], point[0]);
        m.scatter(x, y, zorder = 2);

    plt.show();

def loadTermLocs(filename):
    infile = file(filename);
    lines = infile.readlines();
    infile.close();
    term_locs = {};
    for i in range(0, len(lines), 2):
        term = lines[i];
        locs = lines[i+1];
        locs = locs.split('\t');
        
        term_locs[term] = [];
        for loc in locs:
            if len(loc) > 5:
                loc = loc[1:len(loc)-1];
                point = loc.split(',');
                term_locs[term].append((float(point[0]), float(point[1])));

    return term_locs;

def mapTermMain():
    filename = './data/term_location_2011_3.txt';
    term_locs = loadTermLocs(filename);
    
    #cluster_file = file('./data/cluster.txt');
    #lines = cluster_file.readlines();
    #cluster = {};
    #for line in lines:
    #    items = line.split(',');
    #    cluster[items[1]] = cluster[items[0]];

    for term, locs in term_locs.iteritems():
        print term;
        drawPointsOnJPMap(locs);

mapTermMain();

