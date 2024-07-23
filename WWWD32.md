Documentation on my attempt at the WWWD contest in 2024, part of the RF Hackers Sanctuary / DEFCON 32. 

### The Contest
- Sign up on Wigle.net
- Pick a quad
- Wardrive the quad
- Collect as many new networks as possible
- Find as many "foxes" as possible.

### The Quad

![[Pasted image 20240721204400.png]]

I chose the smallest quad I could find within a reasonable distance with the fewest known WiFi networks listed on Wigle.net. I ended up with 
- _latitude:_ 34.28059 - 34.303368
- _longitude:_ -118.561386 - -118.48425
- km² claimed: 17.947
- starting quad wifi: 552

I used the Wigle.net API to try and find the best quad based on my criteria, and then had to adjust it slightly to for it to be accepted by the contest system when I submitted my quad selection. 

I don't know the *exact* criteria used to determine the starting quad WiFi, but by toying with different variables I assume it's close to the following:
- firsttime=20180101000000
- lasttime=20240718000000
- minQoS=7

Networks seen within the last 5 years with a high "Quality of Signal". This resulted in 556 networks, where my contest quad reported 552 known networks. I figured this was close enough to base my fox-hunting on.

### The Strategy

![[Pasted image 20240721204749.png]]

Above is my quad with the networks from my API search overlayed. As you can see there is only one main thoroughfare that has been heavily driven so far. My plan was to repeatedly drive this strip assuming foxes would be found here primarily, as well as canvas as much of the quad as I could. The western edge of the quad had a gated community that was inaccessible and the north easter corner had a reservoir that also had gated/secure access that wasn't available for me to drive.  
### The Rig

My normal car is in the shop, so the vehicle I used was a rental. A 2024 Mitsubishi Mirage in Wine Red Metallic with 45k miles.
![[IMG_1127.jpeg]]

I ordered a jhewitt kit from 463n7 a few months back and it came just in time to try it during WWWD. I was able to put together the kit, insert an 18650 backwards in the battery board, fry the battery board, smash an OLED screen inserting it into the 3D printed case, and give up on it all together, all before the contest started. 

I ended up defaulting to the following wardriving setup I've used in the past:
##### Primary
Raspberry Pi 4 - 8GB 
(2) Alfa AWUS036ACM
BU-353S4 USB GPS
HooToo Travel Router
(2) Anker 10000 mAh USB battery pack
Latest Kismet release for Debian Bookworm
##### Backup
Silent Circle Blackphone 2 
Wigle.net App

![[IMG_1129.jpeg]]
All my wardriving stuff in the bucket I store it in

![[IMG_1134.jpeg]]
All radio antennas inside the car. One radio has it's stock antennas and is wedged into a carseat. The second radio has two outdoor 7dBi antennas "mounted" to the headrests of the backseat.

![[IMG_1133.jpeg]]The GPS was magnetically attached to the roof of the car with the cable running inside through the hatchback. This was key for getting a good GPS lock more-a-less instantly. 

### The Drive
##### Day 1 - 2024-07-19
Starting at 12:00 Pacific I set out in my quad, starting on the western half.
I ended the day with around 10k networks found, but only 3k ended up counting as new wifi because my Raspberry Pi's timestamps were incorrect. Important lesson learned.
I also ended up driving way outside of my quad without realizing it as I didn't study a map, didn't have a live map running with my quad overlayed, and was unfamiliar with the area. 

Total Hours Driven : 4
New Wifi: ~3,500
Fox Found Ratio : 0.1 (1/10 foxes found)

##### Day 2 - 2024-07-20
Day 2 started at 9am, hitting the eastern half of my quad. I split the day into two 3 hour shifts with a long lunch in between. 

On the second shift I focussed on the edges of the quads as that's where the foxes have been reported to appear most often. I also ended up using the [WWWD Plugin for Kismet](https://github.com/kismetwireless/kismet-plugin-wiglequad) on this run. It also reported that I was outside my quad, even though I wasn't, but it made for a very useful map of quad coverage. 

![[Pasted Graphic 3.png]]

Total Hours Driven : 10
New WiFi : ~39,200
Fox Found Ratio : 0.2 (2/10 foxes found)
##### Day 3 - 2024-07-21
Day 3 started with a bit more strategy. Around 6am Pacific my uploads from the previous day finally parsed and I tried to get a little more calculated in my fox hunting. 

I used the following code to check all my seen networks on previous runs against what I assume were the starting quad wifi networks (potential foxes) to see what networks were left to find, and where to find them.

```
import json

import glob

import os

import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element, SubElement, tostring

import xml.dom.minidom

  

# Function to create KML from a list of network dictionaries

def create_kml(networks, filename):

kml = Element('kml')

document = SubElement(kml, 'Document')

  

for network in networks:

placemark = SubElement(document, 'Placemark')

name = SubElement(placemark, 'name')

name.text = network['ssid']

description = SubElement(placemark, 'description')

description.text = f"MAC Address: {network['mac']}\nSource File: {network['source_file']}"

  

point = SubElement(placemark, 'Point')

coordinates = SubElement(point, 'coordinates')

coordinates.text = f"{network['trilong']},{network['trilat']},0"

  

dom = xml.dom.minidom.parseString(tostring(kml))

pretty_kml = dom.toprettyxml()

  

with open(filename, 'w') as f:

f.write(pretty_kml)

  

# Function to read potential foxes from JSON files

def read_potential_foxes(json_files):

potential_foxes = []

  

for json_file in json_files:

with open(json_file, 'r') as file:

data = json.load(file)

for result in data['results']:

potential_foxes.append({

'ssid': result['ssid'],

'mac': result['netid'],

'trilat': result['trilat'],

'trilong': result['trilong'],

'source_file': os.path.basename(json_file)

})

  

return potential_foxes

  

# Function to read seen networks from KML files

def read_seen_networks(kml_files):

seen_networks = []

  

for kml_file in kml_files:

tree = ET.parse(kml_file)

root = tree.getroot()

namespace = {"kml": "http://www.opengis.net/kml/2.2"}

  

for placemark in root.findall(".//kml:Placemark", namespace):

description = placemark.find("kml:description", namespace).text

if "Type: WIFI" in description:

mac_address = ""

ssid = placemark.find("kml:name", namespace).text

for line in description.split('\n'):

if line.startswith("Network ID: "):

mac_address = line.split("Network ID: ")[1].strip()

seen_networks.append({

'ssid': ssid,

'mac': mac_address,

'source_file': os.path.basename(kml_file)

})

  

return seen_networks

  

# Cross-reference potential foxes with seen networks

def cross_reference_foxes(potential_foxes, seen_networks):

seen_foxes = []

target_foxes = []

  

seen_mac_set = {network['mac'] for network in seen_networks}

  

for fox in potential_foxes:

if fox['mac'] in seen_mac_set:

seen_networks_with_mac = [sn for sn in seen_networks if sn['mac'] == fox['mac']]

for sn in seen_networks_with_mac:

seen_foxes.append({**fox, 'source_file': sn['source_file']})

else:

target_foxes.append(fox)

  

return seen_foxes, target_foxes

  

# Main script

json_files = glob.glob("*.json")

kml_files = glob.glob("seen/*.kml")

  

# Read data

potential_foxes = read_potential_foxes(json_files)

seen_networks = read_seen_networks(kml_files)

  

# Cross-reference

seen_foxes, target_foxes = cross_reference_foxes(potential_foxes, seen_networks)

  

# Create KML files

create_kml(potential_foxes, 'all_potential_foxes.kml')

create_kml(seen_foxes, 'seen_foxes.kml')

create_kml(target_foxes, 'target_foxes.kml')

  

# Generate report

report = (

f"Total potential foxes: {len(potential_foxes)}\n"

f"Total seen foxes: {len(seen_foxes)}\n"

f"Total target foxes: {len(target_foxes)}\n"

)

  

# Save report to text file

with open('foxhunt_report.txt', 'w') as file:

file.write(report)

  

# Print report to terminal

print(report)

  

print("KML files and report have been created.")
```

This resulted in the following report:
Total potential foxes: 484
Total seen foxes: 1556
Total target foxes: 6

The seen foxes count is higher than it should be as I saw some of the networks multiple times on subsequent runs and I didn't filter out repeated runs/networks. The important thing was that I confirmed the 2 foxes Wigle reported as found were indeed in the list of potential foxes, and I had only 6 target fox networks to focus on specifically. I knew this number was inaccurate as I should have 8 foxes remaining, but it gave me something to aim for.

I also put together all the KML's of my previous runs so I could get a sense for what I had covered of my quad so far. There were some large areas missing due to a combination of me missing some KML's of my previous runs, but also some of my runs from Day 1 not counting due to the afformentioned timestamp mistake I made.

![[Pasted Graphic 3 1.png]]
Notice the pass I made on the North East corner trying to see if I could make it into the reservoir. (I couldn't.)

I spent the first shift of day 3 repeatedly driving the main drag in my quad where the remaining foxes might've been - I ended up taking a break, going home, and digging through my electronics hoarding stash to find a replacement OLED to fix the jhewitt rig and add it into the mix for my final run.

![[IMG_1141.jpeg]]

The last half of day 3, I just went through the main drag a few more times and ended up finding a handful of sections I had completely missed on previous runs. At the end of the last drive, I got my final uploads in and now I'm waiting for the backlog on Wigle to process to find the final results. 

Total Hours Driven : 15
New WiFi : ~39,200 + ??? 
Fox Found Ratio : 0.2 (2/10 foxes found) + ??? 

![[Pasted image 20240721213713.png]]

#### The Results

???

![[IMG_1119.jpeg]]