
# coding: utf-8

# In[2]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "san-diego_sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def audit_location(osmfile):
    osm_file = open(osmfile, "r")
    post_code_types = set()
    city_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:postcode":
                    post_code_types.add(tag.attrib['v'])
                if tag.attrib['k'] == "addr:city":
                    city_types.add(tag.attrib['v'])
                
    osm_file.close()
    return post_code_types, city_types

st_types = audit_street(OSMFILE)
pprint.pprint(dict(st_types))

post_types,city_types = audit_location(OSMFILE)
print post_types
print city_types

