# Fetch a resource of a given @id:
# bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_distribution.nrrd \
#               --nexus-id 7f85cd66-d212-4799-bb4c-0732b8534442

# Fetch a resource that matches various propertiy values:
# bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_distribution.nrrd \
#               --filter \
#                   type=BrainParcellationDataLayer \
#                   resolution.value=10 \
#                   atlasRelease.name="Allen Mouse CCF v2" \


# regular query, just using a "not include" string operator
# bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
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
# bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
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
# bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
#               --nexus-token-file ./token.txt \
#               --nexus-org bbp \
#               --nexus-proj atlas \
#               --out ./tmp/some_payload.json \
#               --payload \
#               --verbose \
#               --filter \
#                   type=CellPositions \
#                   brainLocation.brainRegion~="1048" \
