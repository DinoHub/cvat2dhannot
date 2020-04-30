import xml.etree.ElementTree as ET

# create the file structure
data = ET.Element('annotations')
version = ET.SubElement(data, 'version')
version.text = '1.1'

box_props = ['frame', 'outside', 'occluded', 'keyframe', 'xtl', 'ytl', 'xbr','ybr']

for track in tracks:
    track_xml_element = ET.SubElement(data, 'track')
    track_xml_element.set('id','0')
    track_xml_element.set('label','ship')

    for box in boxes:
        box_xml_element = ET.SubElement(track, 'box')
        box_xml_element.text = " "
        for prop in box_props:
            box_xml_element.set(prop, '0')

# create a new XML file with the results
mydata = ET.tostring(data, encoding='unicode')
print(mydata)
with open("try.xml", "w") as f:
    f.write(mydata)
