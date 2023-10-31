import os
import copy

from bba_data_fetch.main import main

nexus_token = os.environ["NEXUS_STAGING_TOKEN"]
test_folder = os.environ["TEST_FOLDER"]

nexus_ids = [
    "https://bbp.epfl.ch/neurosciencegraph/data/brainatlasrelease/c96c71a8-4c0d-4bc1-8a1a-141d9ed6693d",
    "https://bbp.epfl.ch/neurosciencegraph/data/cellcompositions/54818e46-cf8c-4bd6-9b68-34dffbc8a68c",
    "https://bbp.epfl.ch/neurosciencegraph/data/cellcompositions/54818e46-cf8c-4bd6-9b68-34dffbc8a68c",
    "http://purl.obolibrary.org/obo/NCBITaxon_10090",
    "https://bbp.epfl.ch/neurosciencegraph/data/allen_ccfv3_spatial_reference_system",
    "http://bbp.epfl.ch/neurosciencegraph/ontologies/core/mba_brainregion_corrected?tag=v0.2.0",
    #"https://bbp.epfl.ch/neurosciencegraph/data/7f85cd66-d212-4799-bb4c-0732b8534442?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/e238a1f6-0b30-48df-ac8b-6185efe10a59?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/2f26c63b-6d01-4540-bf8b-b0a2a7c59597?tag=v0.1.0",
    #"https://bbp.epfl.ch/neurosciencegraph/data/c1f768f8-5bbb-46ea-aeee-bc92909a0b52?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/7b4b36ad-911c-4758-8686-2bf7943e10fb?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/025eef5f-2a9a-4119-b53f-338452c72f2a?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/a4552116-607b-469e-ad2a-50bba00c23d8?tag=v0.1.1",
    "https://bbp.epfl.ch/data/bbp/mmb-barrel-cortex/a48c0db0-5fde-4912-a702-595c15a380b6?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/9768fb11-6461-4705-995f-7ad40b3aab77?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/35cb6642-db10-49e9-8f9c-46be17a9c376?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/dca40f99-b494-4d2c-9a2f-c407180138b7?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/9e2c3aa7-3b19-4da6-9623-f864368326e6?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/dfaaece4-04b9-49c9-9561-6141f4e9c848?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/d05b318f-266c-4f15-8ee1-e1d320d79783?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/50b8e911-6d97-4a82-910b-325273cafed6?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/a7b63363-742e-4671-826f-3a2b82db17c6?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/6951d06f-6be9-45f5-a2f3-d4001af9cca5?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/db7b9f14-0942-4131-8ef7-ab02b1497469?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/6e3e0700-7289-4285-ba5c-3ac94930f3d7?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/2f53f1b3-73e7-4cf3-8e82-9bb55c7a6443?tag=v0.1.0",
    #"https://bbp.epfl.ch/neurosciencegraph/data/c5a6e50c-8994-4194-bc3a-7254310d5558?tag=v0.1.0",
    #"https://bbp.epfl.ch/neurosciencegraph/data/3bb21391-0ce7-446d-b18f-309b84f955a6?tag=v0.1.0",
    #"https://bbp.epfl.ch/neurosciencegraph/data/8859cece-c0d0-4776-b638-fb871168880d?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/e758bb5f-d455-457c-90b8-345d5f9abdb2?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/423e277c-259b-410a-bf07-4752be66ae33?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/a3c77f3f-3cb4-4b19-95f3-92b2330dfdb8?tag=v0.1.1",
    #"https://bbp.epfl.ch/neurosciencegraph/data/e51f53c8-6883-49e5-8a5b-eec4bd7d41c3?tag=v0.1.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/ae8cbd28-e17b-4c1e-967a-a5084b7ad335?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/d45f1a66-e663-4991-bda9-3ee8bc447061?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/6a593672-9e7d-45aa-8740-19d79da9b3d3?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/6b711d4c-ff0b-4e87-89b7-5390fc0fc4d0?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/ff5eb1d8-d085-47fb-9951-a3d331c2cfa8?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/7cf713d1-9ca5-42da-8a31-f47d9449543b?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/ab591ed4-3377-43c1-9038-253eeb107dc9?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/09e98630-78d1-4595-bf48-8631dd0bafbd?tag=v0.1.1",
    "https://bbp.epfl.ch/neurosciencegraph/data/6419ac24-9d62-494f-b405-56f00743fcde?tag=v0.2.0",
    "https://bbp.epfl.ch/neurosciencegraph/data/c67fa26d-064c-4f9f-a381-7489fb5837bc?tag=v0.1.1"
]


def test_resource_fetching():
    args_list = [
        "--nexus-token", nexus_token,
        "--forge-config", "cfg/forge-config.yml",
        "--nexus-env", "https://staging.nise.bbp.epfl.ch/nexus/v1",
        "--nexus-org", "bbp",
        "--nexus-proj", "atlas",
        "--out", test_folder,
    ]

    for nexus_id in nexus_ids:
        full_args_list = copy.deepcopy(args_list)
        full_args_list.extend(["--nexus-id", nexus_id])
        print(f"Fetching Resource Id '{nexus_id}'")
        main(full_args_list)
