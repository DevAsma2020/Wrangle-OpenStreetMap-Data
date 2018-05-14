
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schemaDB




OSM_PATH = "Toronto.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

postal_code_re = re.compile(r'^M[A-Z0-9]{2} [A-Z0-9]{3}$', re.IGNORECASE) #Regex pattern to extract last word in each value
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) #Regex pattern to extract last word in each value
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schemaDB.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'version']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'version']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


#Before : After
mapping = {"Ave": "Avenue",
           "E": "East",
           "Pl": "Place",
           "Dr": "Drive",
           "St":"Street",
           "W":"West",
           "Rd":"Road",
           "Hwy":"Highway",
           "Blvd":"Boulevard",
           "St.":"Street",
           "E.":"East",
           "ave":"Avenue",
           "Pkwy":"Parkway",
           "ST":"Street",
           "W.":"West",
           "st.":"Street",
           "rd":"Road",
           "avenue":"Avenue",
           "street":"Street",
           "west":"West"
           }




def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements



    # YOUR CODE HERE

    if element.tag == 'node':
        # Main node
        for node_attrib in NODE_FIELDS:
            if node_attrib in element.attrib:
                node_attribs[node_attrib] = element.attrib[node_attrib]

        # Tags child for main node
        for tag_child in element:
            attrib_child_tag = {}
            m = PROBLEMCHARS.search(tag_child.attrib["k"])
            if not m:
                #check v value
                v=audit(tag_child.attrib["k"],tag_child.attrib["v"])
                if type(v)==tuple:
                    if v[0]==1:
                        v=v[1][0]
                    else:
                        v="skip"
                if v!="skip":

                    attrib_child_tag["id"] = node_attribs["id"]
                    attrib_child_tag["key"] = get_Key_value(tag_child.attrib["k"])
                    attrib_child_tag["value"] =v
                    attrib_child_tag["type"] = get_type_value(tag_child.attrib["k"])
                    tags.append(attrib_child_tag)

        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        # Main node
        for node_attrib in WAY_FIELDS:
            if node_attrib in element.attrib:
                way_attribs[node_attrib] = element.attrib[node_attrib]

        position = 0
        for child in element:
            nd_tags = {}
            way_node = {}
            if child.tag == "nd":

                way_node["id"] = way_attribs["id"]
                way_node["node_id"] = child.attrib["ref"]
                way_node["position"] = position
                position = position + 1
                way_nodes.append(way_node)
            else:
                m = PROBLEMCHARS.search(child.attrib["k"])
                if not m:
                #check v value
                    v=audit(child.attrib["k"],child.attrib["v"])
                    if type(v)==tuple:
                        if v[0]==1:
                            v=v[1][0]
                        else:
                            v="skip"
                    if v!="skip":

                        nd_tags["id"] = way_attribs["id"]
                        nd_tags["key"] = get_Key_value(child.attrib["k"])
                        nd_tags["value"] = audit(child.attrib["k"],child.attrib["v"])
                        nd_tags["type"] = get_type_value(child.attrib["k"])
                        tags.append(nd_tags)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Audit Functions                     #
# ================================================== #

def is_street_name(elem):#check if Tag attributes have street key
    return (elem == "addr:street")



def audit(k_value, v_value):# Main function that open OSM file, loop through node ot way element and check tags elements.
    if is_street_name(k_value):
        name=update_name(v_value,mapping)
        return name
    elif is_postal_code(k_value):
        name=audit_postak_code(v_value)
        return name
    else:
        return v_value



def update_name(name, mapping):#take street name and mapping dictionary to update street name
    m = street_type_re.search(name)
    if m:
        StreetType = m.group()
        if StreetType in mapping:
            name = name.replace(StreetType, mapping[StreetType])

    return name



def is_postal_code(elem):
    return (elem=="addr:postalcode")




def audit_postak_code(postal_code):#Extract last word in Tag key values, which would be street type
    m = postal_code_re.search(postal_code)#try to search Regex pattern in value
    print(m)
    if m:
        postal_code=m.group()
        return postal_code
    if not m:#value wasn't matching Regex patttern
        if "," in postal_code:#valeu has more than one postal code
            postal_code = postal_code.split(',')
            return(1,postal_code)
        elif postal_code[0]=="M" and len(postal_code)==6:
            postal_code=' '.join(postal_code[i:i+3] for i in range(0, 6, 3))
            return postal_code
        else:
            return(2,postal_code)

# ================================================== #
#               Helper Functions                     #
# ================================================== #

def get_Key_value(key_attr):#check value for k attribute
    if ":" in key_attr:#if value has : in it
        return key_attr.split(":", 1)[1] #take after :
    else:
        return key_attr


def get_type_value(key_attr):#check value for k attribute
    if ":" in key_attr:
        return key_attr.split(":", 1)[0]#take before :
    else:
        return "regular"

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


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
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

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

        #validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                #if validate is True:
                    #validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])



if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
print("DOOOOOOOOOOOOOOOONE!")
