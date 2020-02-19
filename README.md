# Data Fetch
This module, in charge of fetching datasets from Nexus and copy them on local storage.

# Install
```
cd bluebrainatlas-datafetch
pip install .
```

Then, the command `bba-datafetch` becomes available in the system PATH.

# Use and examples
Display help:
```
bba-datafetch --help
```

There are a few operator for the `--filter` argument:
- `=` strictly equal for number and case-insensitive equal for strings
- `~=` contains, only for strings
- `!=` different, for numbers or does-not-contain for strings
- `>=` greater than or equal to, for numbers only
- `<=` lower than or equal to, for numbers only
- `>` greater than, for numbers only
- `<` lower than, for numbers only

There is also a `--verbose` arg.

- Fetch a resource payload from its `@id`:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --payload \                                       # <-- to fetch the payload !
              --out ./tmp/some_payload.json \                   # <-- needs a .json extension
              --nexus-id 7f85cd66-d212-4799-bb4c-0732b8534442
```

- Fetch the distribution file linked a resource, from resource `@id`:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_distribution.nrrd \              # <-- extension must be the same as distant file
              --nexus-id 7f85cd66-d212-4799-bb4c-0732b8534442
```

- Fetch a resource payload properties (dynamic SPARQL query building):
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --payload \                                       # <-- to fetch the payload !
              --out ./tmp/some_payload.json \                   # <-- needs a .json extension
              --filter \
                  type=BrainParcellationDataLayer \
                  resolution.value=10 \
                  atlasRelease.name="Allen Mouse CCF v2" \
```


- Fetch the distribution linked to a resource from payload properties (dynamic SPARQL query building):
```
c
```

- Some comparison operator don't play well with shell script and need to be framed with quote signs:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_distribution.nrrd \
              --filter \
                  type=BrainParcellationDataLayer \
                  "resolution.value=>10" \                # <-- if not framed with "...", the > symbol redirects the output
                  atlasRelease.name="Allen Mouse CCF v2" \
```

- Case insensitive for property and type names:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_payload.json \
              --payload \
              --verbose \
              --filter \
                  type=BrainParcellationDataLayer \
                  resOlution.value=10 \                      # <-- wrong case spelling, still works!
                  Bufferencoding=gzip \                      # <-- wrong case spelling, still works!
                  atlasRelease.name="Allen Mouse CCF v2" \   
```

- Fetch the point cloud file linked to the brain region `mba:1048`:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_payload.raw \
              --verbose \
              --filter \
                  type=CellPositions \
                  brainLocation.brainRegion~="1048" \
```
For this one, the CLI still does not work with a filter like `brainLocation.brainRegion="mba:1048"` because `mba` is actually a variable.  Added to the `#TODO`.


# TODO
- Replace with context prefixes when necessary. For example, the use of `mba:547` is problematic because the SPARQL query should actually be about  `http://api.brain-map.org/api/v2/data/Structure/1048`
- Deal with digging into lists, just like we would do in raw SPARQL using `rdf:first` and `rdf:rest`:
```SQL
PREFIX unknown: <https://bbp.epfl.ch/nexus/v1/resources/bbp/atlas/_/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX nsg: <https://neuroshapes.org/>
SELECT ?s ?stuff
WHERE {
  ?s a nsg:VolumetricDataLayer .
  ?s <https://neuroshapes.org/brainLocation>/<https://neuroshapes.org/brainRegion> ?theid .
  ?s nsg:dimension/rdf:first/<http://schema.org/name> ?firstdim .
  ?s nsg:dimension/rdf:rest/rdf:first/<http://schema.org/size> ?stuff .
  FILTER(regex(str(?theid), "997", "i"))
  FILTER(regex(str(?firstdim), "intensity", "i"))
}
```
