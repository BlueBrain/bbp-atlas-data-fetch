This documentation is also available on [Confluence](https://bbpteam.epfl.ch/project/spaces/display/BBKG/blue_brain_atlas_data_fetch).

## Description
This module is a (Python) CLI in charge of fetching datasets from Nexus, one file (or payload) at the time. It can fetch payloads and save them as JSON files or it can fetch binaries (_distributions_) linked to resources.

There is mainly two ways of fetching a piece of data:
- using the @id of a resource
- using filters on the resource properties to narrow down the selection and eventually find the relevant dataset

When using filters (see below), a SPARQL query is dynamically generated, allowing graph traversal.

## Source
You can find the source of this module here: [https://bbpcode.epfl.ch/code/#/admin/projects/dke/blue_brain_atlas_data_fetch](https://bbpcode.epfl.ch/code/#/admin/projects/dke/blue_brain_atlas_data_fetch)

## Install
Clone the repository:
```
git clone https://lurie@bbpcode.epfl.ch/code/a/dke/blue_brain_atlas_data_fetch
```

And install with pip:
```
cd blue_brain_atlas_data_fetch
pip install .
```
From now on, the executable **bba-datafetch** is in your PATH.

## Dependencies
Here is the list of Python dependencies:
- [nexus-sdk](https://pypi.org/project/nexus-sdk/)
Though this will be installed by pip automatically.

## Inputs
There is no input apart from configuration and filter/id. See the **CLI arguments** section for more info.

## Outputs
This CLI write on disc one of the two depending on the arguments provided:
- a JSON file that corresponds to the targeted resource payload
- a copy of the distribution file linked in the targeted resource. Could be any kind of file

## CLI arguments
- **--version** - [flag] Display the version
- **--help** - [flag] Display help
- **--verbose** - [flag] Enables verbose mode to print the generated SPARQL query and response
- **--nexus-token-file /path/to/token.txt** - [single string] The path to the text file that contains the Nexus token. Mandatory
- **--nexus-env https://bbp.epfl.ch/nexus/v1/** - [single string] The URL to the Nexus environment. Mandatory
- **--nexus-org bbp** - [single string] The name of the Nexu organization to look for a resource. Mandatory
- **--nexus-id some_id_probably_uuid** - [single string] The @id of the Nexus resource to fetch. Optional, but necessary if **--filter** is not provided
- **--payload** - [flag] Fetch the payload as a JSON file. Optional, the default behavior is to fetch the file linked by the _distribution.contentUrl_ property.
- **--favor - [multiple string] Payload properties and values with the format <'properties:value'> (ex: 'name:1.json') which will be used to determine which file to choose when retrieving a distribution from a resource with multiple distributions. Optional
- **--out /some/file.json** - [single string] Path to the output file to create. The extension has to be .json if the flag --payload is provided. Otherwise, the extension must be the same as the distant file. Mandatory
- **--keep-meta** - [flag] if --payload is provided, the JSON file will not contain the Nexus/JSON-LD system properties. If this flag is provided, the system metadata are kept
- **--rev n** - [number] The revision argument is mainly to be used along **--nexus-id** to fetch a specific revision of a given resource. Optional, fetches the last revision if not provided
- **--tag some_tag** - [single string] The tag argument is mainly to be used along **--nexus-id** to fetch a specific tag of a given resource. Optional
- **--filter prop1=1 prop2=20** - [multiple strings] Filters are to be used instead of --nexus-id if the @id is not known. Filters are applied on properties and can work with graph traversal. Optional but necessary of **--nexus-id** is not provided

## Filters
The **--filter** argument is powerful and deserves its own paragraph.  
Using filters keeps only the resources that match the conditions. each filter takes this shape:

property name [ operator ] value to compare with

Where:
- **property name** can be a direct root level property (eg. _name_), a subproperty (eg. _resolution.value_) or even a graph traversal property (eg. _atlasRelease.name_ when the _atlasRelease_ property is actually just an _@id_ to another resource that has a _name_ property).
- **value** can be a number or a string
- **operator** can be one of the following:
  - **=** strictly equal for number and case-insensitive equal for strings
  - **~=** contains, only for strings
  - **!=** different, for numbers or does-not-contain for strings
  - **>=** greater than or equal to, for numbers only
  - **<=** lower than or equal to, for numbers only
  - **>** greater than, for numbers only
  - **<** lower than, for numbers only

Example: _resolution.value=25_

Then, multiple filters of this kind can be used, space separated, after a single **--filter** flag.

⚠️ Warning: since this is used in a terminal, the symbol ">" is natively made to redirect the output to a file. Hence, filters that use the operators > or >= must have their whole expression famed with double or simple quotes.

⚠️ Warning 2: Like most CLI, multiword strings must also be framed in double or simple quotes.

Example: --filter _"resolution.value>=25" name="hello world" "another.prop=bip boop"_

ℹ️ Info: property names such as resolution or name should not be preceded by a context prefix. For example: "nsg:resolution.schema:value" is not valid.

ℹ️ Info: if a property is a **@list**, then we can address an element from the list using square brackets. Example: _--filter dimension[0].name=intensity worldMatrix[0]=10_

Under the hood, this is using _rdf:first_ and _rdf:rest_.

## Examples
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

Fetch the distribution file corresponding to the favor argument among multiple distributions from a resource:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_payload.json \
              --nexus-id http://bbp.epfl.ch/neurosciencegraph/ontologies/mba\
              --favor "encodingFormat:application/ld+json" \
              --verbose \
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

- Some comparison operator don't play well with shell script and need to be framed with quote signs:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_distribution.nrrd \
              --filter \
                  type=BrainParcellationDataLayer \
                  "resolution.value>=10" \                # <-- if not framed with "...", the > symbol redirects the output
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

- Fetch the point cloud file linked to the brain region _`mba:1048`_:
```
bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_payload.raw \
              --verbose \
              --filter \
                  type=CellPositions \
                  brainLocation.brainRegion="mba:1048" \
```

Note that _mba:1048_ is the id of a brain region (Allen CCF 1048 is the gigantocellular reticular nucleus) preceded by _mba_, which is the prefix in the graph database (_mba_=mouse brain atlas). This means that prefixes can be used in values if need be.

## Maintainers
This module was originally created by Jonathan Lurie, DKE (jonathan.lurie@epfl.ch).
