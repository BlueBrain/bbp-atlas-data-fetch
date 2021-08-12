# Fetch a resource of a given @id:
bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_distribution.nrrd \
              --nexus-id "https://bbp.epfl.ch/neurosciencegraph/data/7b4b36ad-911c-4758-8686-2bf7943e10fb"

# Fetch a resource that matches various propertiy values:
# bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_distribution.nrrd \
#               --verbose \
#               --filter \
#                   type=BrainParcellationDataLayer \
#                   resolution.value=10 \
#                   atlasRelease.name="Allen Mouse CCF v2" \
#                   dimension[0].name=label \


# regular query, just using a "not include" string operator
# bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_payload.json \
#               --payload \
#               --verbose \
#               --filter \
#                   type=BrainParcellationDataLayer \
#                   resolution.value=10 \
#                   bufferEncoding=gzip \
#                   atlasRelease.name!="Allen Mouse CCF v2" \


# Same but with case mistakes in prop names
# bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_payload.json \
#               --payload \
#               --verbose \
#               --filter \
#                   type=BrainparcellationDataLayer \
#                   resOlution.value=10 \
#                   Bufferencoding=gzip \
#                   atlasRelease.name!="Allen Mouse CCF v2" \

# fetch point cloud for brain region mba:1048
# bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_payload.json \
#               --payload \
#               --verbose \
#               --filter \
#                   type=CellPositions \
#                   brainLocation.brainRegion~="1048" \

# fetch point cloud for brain region mba:1048
# bba-data-fetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_payload.json \
#               --payload \
#               --verbose \
#               --filter \
#                   type=CellPositions \
#                   brainLocation.brainRegion="mba:1048" \
