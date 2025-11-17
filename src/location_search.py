import xmltodict
import os

class LocationSearch:
    def __init__(self):
        self.locations = []
        self.load_locations()
    
    def load_locations(self):
        # Read OSM file and extract nodes with name or type tags
        osm_path = os.path.join(os.path.dirname(__file__), "../data/map.osm")
        with open(osm_path, 'rb') as f:
            osm_data = xmltodict.parse(f, xml_attribs=True)
        
        type_tags = ['amenity', 'building', 'shop', 'tourism', 'historic', 'leisure', 'natural']
            
        for node in osm_data['osm']['node']:
            if 'tag' in node:
                tags = node['tag'] if isinstance(node['tag'], list) else [node['tag']]
                name = None
                type = None
                
                for tag in tags:
                    if tag['@k'] == 'name':
                        name = tag['@v']
                    elif tag['@k'] in type_tags:
                        type = f"{tag['@k']}: {tag['@v']}"
                
                if name or type:  # Include locations with either name or type
                    self.locations.append({
                        'name': name or type,  # Use type as name if no name exists
                        'type': type,
                        'lat': float(node['@lat']),
                        'lon': float(node['@lon'])
                    })

    def search(self, query):
        # Search locations by name or type
        query = query.lower()
        results = []
        
        # First add exact matches
        for loc in self.locations:
            name = loc['name'].lower() if loc['name'] else ''
            if query == name:
                results.append(loc)
                
        # Then add partial matches
        if len(results) < 5:
            for loc in self.locations:
                name = loc['name'].lower() if loc['name'] else ''
                if loc not in results and query in name:
                    results.append(loc)
                    if len(results) >= 5:
                        break
        
        return results  # Return up to 5 results
