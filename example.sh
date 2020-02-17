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


bba-datafetch --nexus-env https://bbp.epfl.ch/nexus/v1/ \
              --nexus-token-file ./token.txt \
              --nexus-org bbp \
              --nexus-proj atlas \
              --out ./tmp/some_payload.json \
              --payload \
              --verbose \
              --filter \
                  type=BrainParcellationDataLayer \
                  resolution.value=10 \
                  atlasRelease.name!="Allen Mouse CCF v2" \
