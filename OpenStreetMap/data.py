
# coding: utf-8

# In[63]:

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = "G:/data_analyst_nano/san-diego_california.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']

def get_tags(element,idd):
    tags = []  
    for tag in element.iter('tag'):
        tag_dic = {}
        k = tag.attrib['k']
        v = tag.attrib['v']
        if PROBLEMCHARS.search(k):
            continue
        elif LOWER_COLON.search(k):
            tag_dic['type'] = k[:k.find(':')]
            tag_dic['key']  = k[k.find(':')+1:]
        else:
            tag_dic['type'] = 'regular'
            tag_dic['key']  = k
        
        if tag_dic['key'] == "city":
            if not v in ["San Diego","san diego"]:
                continue 

        tag_dic['id'] = idd
        tag_dic['value'] = update_value(k,v)
        tags.append(tag_dic)
    return tags

mapping = { "Av": "Avenue",'Ave': 'Avenue','Ave.': 'Avenue','Blvd': 'Boulevard','Blvd.': 'Boulevard','Dr': 'Drive','Dr.':'Drive','Ln': 'Lane','Rd':'Road','Wy':'Way','St':'Street'}

def update_value(k,v):
    if k == "addr:postcode":
        if re.match(r'^\d{5}$', v):
            return v            
        elif  re.match(r'^(\d{5})-\d{4}$', v):
            return re.findall(r'^(\d{5})-\d{4}$', v)[0]
        elif v.startswith('CA '):
            v = v[3:]
            return v
        return v
    if k == "addr:street":
        last_word = v.split()[-1]
        if last_word in mapping.keys():
            v = v.replace(last_word,mapping[last_word])
            return v
        return v
    return v

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    if element.tag == 'node':
        for temp in element.iter('node'):
            idd = temp.attrib['id']
            for n in node_attr_fields:
                i = temp.attrib[n]
                node_attribs[n] = i
        
        if element.iter('tag'):
            tags = get_tags(element,idd)
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for temp in element.iter('way'):
            idd = temp.attrib['id']
            for n in way_attr_fields:
                i = temp.attrib[n]
                way_attribs[n] = i
        
        if element.iter('nd'):
            pos = 0
            for nd in element.iter('nd'):
                nd_dic = {}
                nd_dic['id'] = idd
                nd_dic['node_id'] = nd.attrib['ref']
                nd_dic['position'] = pos
                way_nodes.append(nd_dic)
                pos+=1        
        
        if element.iter('tag'):
            tags = get_tags(element,idd)            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if element.tag == 'node':
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
            elif element.tag == 'way':
                ways_writer.writerow(el['way'])
                way_nodes_writer.writerows(el['way_nodes'])
                way_tags_writer.writerows(el['way_tags'])


process_map(OSM_PATH)

