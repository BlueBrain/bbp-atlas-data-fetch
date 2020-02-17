# Data Fetch
This module, in charge of fetching datasets from Nexus and copy them on local storage.

# Install
```
cd bluebrainatlas-datafetch
pip install .
```

Then, the command `bba-datafetch` becomes available in the system PATH.

# Use
Display help:
```
bba-datafetch --help
```

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
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_distribution.nrrd \              # <-- extension must be the same as distant file
              --filter \
                  type=BrainParcellationDataLayer \
                  resolution.value=10 \
                  atlasRelease.name="Allen Mouse CCF v2" \
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
                  "resolution.value=>10" \                 <-- if not framed with "...", the > symbol redirects the output
                  atlasRelease.name="Allen Mouse CCF v2" \
```

For the `filter`, there are different kinds of operators:
- `=` strictly equal for number and case-insensitive equal for strings
- `~=` contains, only for strings
- `!=` different, for numbers only or does-not-contain for strings
- `>=` greater than or equal to, for numbers only
- `<=` lower than of equal to, for numbers only
- `>` greater than, for numbers only
- `<` lower than, for numbers only

There is also a `--verbose` arg.


# TODO
- Make sure filters on props that don't exist are discarded.
