"""
    Download the file attached to a given resource from Nexus.
    If no file is atatched and the output required is actually the payload,
    then the output extension must be .json
"""

import argparse
import sys
import os
import json
import nexussdk as nexus

from bluebrainatlas_datafetch import __version__

__author__ = "Jonathan Lurie"
__copyright__ = "EPFL - The Blue Brain Project"
__license__ = ""



def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description=__doc__)

    parser.add_argument(
        "--version",
        action="version",
        version="bluebrainatlas-datafetch {ver}".format(ver=__version__))

    parser.add_argument(
        "-nexus-token-file",
        dest="nexus_token_file",
        required=True,
        help="Local path to the file containing the Nexus token"
    )

    parser.add_argument(
        "-nexus-env",
        dest="nexus_env",
        required=True,
        help="URL to the Nexus environment"
    )

    parser.add_argument(
        "-nexus-org",
        dest="nexus_org",
        required=True,
        help="The Nexus organization where the resource is"
    )

    parser.add_argument(
        "-nexus-proj",
        dest="nexus_proj",
        required=True,
        help="The Nexus project where the resource is"
    )

    parser.add_argument(
        "-nexus-id",
        dest="nexus_id",
        required=True,
        help="The Nexus @id of the resource to fetch the linked file of"
    )

    parser.add_argument(
        "-out",
        dest="out",
        required=True,
        help="Output filepath"
    )

    parser.add_argument(
        "-rev",
        dest="nexus_rev",
        required=False,
        default=None,
        help="OPTIONAL Revision of the Nexus resource"
    )

    parser.add_argument(
        "-tag",
        dest="nexus_tag",
        required=False,
        default=None,
        help="OPTIONAL Tag of the Nexus resource"
    )

    return parser.parse_args(args)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    # setting Nexus SDK
    token = open(args.nexus_token_file, 'r').read().strip()
    nexus.config.set_token(token)

    if args.nexus_env[-1] == '/':
        args.nexus_env = args.nexus_env[:-1]
    nexus.config.set_environment(args.nexus_env)




    query = """
    PREFIX nsg: <https://neuroshapes.org/>
    PREFIX schema: <http://schema.org/>
    SELECT ?s
    WHERE {?s a nsg:BrainParcellationDataLayer .
      ?s nsg:resolution/schema:value ?r .           # select the field resolution.value (from the BrainParcellationDataLayer)
      ?s nsg:bufferEncoding ?be .                   # select the field bufferEncoding (from the BrainParcellationDataLayer
      ?s nsg:atlasRelease ?ar .                     # select the field atlasRelease (from the BrainParcellationDataLayer)
      ?ar schema:name ?arn .                        # select the name of the atlasRelease
      FILTER(?r = 25) .                             # keep only the BrainParcellationDataLayer with resolution 25
      FILTER(regex(str(?arn), ".*V2$", "i"))        # keep only the atlasRelease with a name ending with v2 (case insensitive)
      FILTER(?be = "gzip")}                         # keep only the BrainParcellationDataLayer with data compressed
    """

    result = nexus.views.query_sparql(args.nexus_org, args.nexus_proj, query = query)
    print(json.dumps(result, indent=2))




    exit(999)




    # Fetching the resource of interest
    try:
        resource = nexus.resources.fetch(args.nexus_org, args.nexus_proj, args.nexus_id, rev=args.nexus_rev, tag=args.nexus_tag)
    except Exception as e:
        print("❌", e)
        exit(1)

    output_extension = args.out.split(".").pop().lower()

    # Make sure the parent directory of the specified output exist, if not, create it
    parent_dir = os.path.dirname(args.out)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)

    if "distribution" in resource and "contentUrl" in resource["distribution"]:
        linked_file_extension = resource["distribution"]["name"].split(".").pop().lower()

        # check that extension of distant file and the output is the same (case not sensitive)
        if linked_file_extension != output_extension:
            print("❌ The output extension is", output_extension, "while the distant file extension is", linked_file_extension, " - They must be the same.")
            exit(1)

        # fetching the file
        file_id = resource["distribution"]["contentUrl"].split("/")[-1]
        nexus.files.fetch(args.nexus_org, args.nexus_proj, file_id , out_filepath=args.out)
    else:

        # If there is no file attached to the resource, we want to write the payload as a JSON
        # output file. Though if the extension of the given output is not json, then we raise an error and quit.
        if output_extension != "json":
            print("❌ This resource is not linked to any file. The output extension must be .json to output a payload file.")
            exit(1)

        # removing the file if it exists
        if os.path.exists(args.out):
            os.remove(args.out)

        # sanitize from all the Nexus meta
        resource.pop("@context", None)
        resource.pop("@id", None)
        resource.pop("@type", None)
        resource.pop("_self", None)
        resource.pop("_project", None)
        resource.pop("_rev", None)
        resource.pop("_deprecated", None)
        resource.pop("_createdAt", None)
        resource.pop("_createdBy", None)
        resource.pop("_updatedAt", None)
        resource.pop("_updatedBy", None)
        resource.pop("_incoming", None)
        resource.pop("_outgoing", None)
        resource.pop("_constrainedBy", None)

        # write the resource payload as a json file
        f = open(args.out, "w+")
        f.write(json.dumps(resource, indent=2))
        f.close()

        exit(0)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
