"""
    Download the file attached to a given resource from Nexus.
    If no file is atatched and the output required is actually the payload,
    then the output extension must be .json
"""

import argparse
import re
import sys
import os
import json
import string
import random
import logging
import nexussdk as nexus

from bluebrainatlas_datafetch import __version__

__author__ = "Jonathan Lurie"
__copyright__ = "EPFL - The Blue Brain Project"
__license__ = ""

UNKNOWN_CONTEXT_SHORT = "unknown:"


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
        "--nexus-token-file",
        dest="nexus_token_file",
        required=True,
        help="Local path to the file containing the Nexus token"
    )

    parser.add_argument(
        "--nexus-env",
        dest="nexus_env",
        required=True,
        help="URL to the Nexus environment"
    )

    parser.add_argument(
        "--nexus-org",
        dest="nexus_org",
        required=True,
        help="The Nexus organization where the resource is"
    )

    parser.add_argument(
        "--nexus-proj",
        dest="nexus_proj",
        required=True,
        help="The Nexus project where the resource is"
    )

    parser.add_argument(
        "--nexus-id",
        dest="nexus_id",
        required=False,
        default=None,
        help="The Nexus @id of the resource to fetch the linked file of (optional, but necessary if --filter is not provided)"
    )

    parser.add_argument(
        "--out",
        dest="out",
        required=True,
        help="Output filepath"
    )

    parser.add_argument(
        "--favor",
        dest="favor",
        type=str,
        required=False,
        default=[],
        nargs='+',
        help="OPTIONAL Payload properties and values with the format <'properties:value'> (ex: 'name:1.json') which will be used to determine which file to choose when retrieving a resource with multiple distributions."
    )
    parser.add_argument(
        "--payload",
        dest="payload",
        action="store_true",
        help="OPTIONAL Stores the payload instead of the distribution file attached (--out extension must be .json)"
    )

    parser.add_argument(
        "--keep-meta",
        dest="keep_meta",
        action="store_false",
        help="OPTIONAL Keep Nexus metadata in the payload (only applies when the payload is fetched and not the distribution file)"
    )

    parser.add_argument(
        "--rev",
        dest="nexus_rev",
        required=False,
        default=None,
        help="OPTIONAL Revision of the Nexus resource"
    )

    parser.add_argument(
        "--tag",
        dest="nexus_tag",
        required=False,
        default=None,
        help="OPTIONAL Tag of the Nexus resource"
    )

    parser.add_argument(
        "--filter",
        dest="filter",
        required=False,
        default=None,
        nargs='+',
        help="OPTIONAL Filter the results properties (example: 'resolution.value=10 bufferEncoding=gzip'). Optional but necessary of --nexus-id is not provided."
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="OPTIONAL Verbose mode"
    )

    args = parser.parse_args(args)

    # setting the verbosity of the log
    if args.verbose:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(message)s', level=logging.WARNING)

    if not args.nexus_id and not args.filter:
        logging.error("❌ If the argument --filter is missing, the argument --nexus-id becomes mandatory.")
        exit(1)

    if args.nexus_id and args.filter:
        logging.error("❌ Arguments --filter and --nexus-id are mutually exclusive.")
        exit(1)

    return args


def randomString(stringLength=5):
    """Generate a random string of fixed length

    Args:
      stringLength ([int]): The length of the string to generate

    Returns:
      :string: The random string
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def extractListIndexFromPropName(prop_name):
    """
        A property name can refer to an position in a list, such as in "dimension[10]"
        then, the '10' as well as the 'dimension' must be extracted.
    """

    regex = r"\[(\d+)\]$"
    matches = re.search(regex, prop_name)

    if matches:
        group_num = 1
        list_index = int(matches.group(group_num))
        prop_name_without_index = prop_name[:matches.start(group_num)-1]
        return (prop_name_without_index, list_index)
    else:
        return (prop_name, None)


def createRestFirstSequence(list_index):
    """
        In RDF, an element of a @list is addressed with rdf:first and rdf:rest
        This fuction builds a sequence of /rdf:rest/rdf:rest/.../rdf:first based
        on the list_index provided.
    """
    rest = "/rdf:rest"
    first = "/rdf:first"

    if list_index is None:
        return ''

    return list_index * rest + first



def translateFilters(args, context):
    """
        Convert the string filters into filters datastructure that are easier to understand
        for further processes.
        For example:
            "atlasRelease.name='Allen Mouse CCF v2'"
            will turn into
            {
                "id": "dbgxf", # some random string
                "properties": [
                    "atlasRelease",
                    "name"
                ],
                "comparator": '=',
                "value": "Allen Mouse CCF v2",
                "value_type": "string"
            }
        return :tuple: (filter_datastructure, context_mappers)
    """
    # must be in the order from the most complex to the simplest
    filter_symbols = [">=", "<=", "!=", "~=", "=", ">", "<"]

    interpreted_filters = []
    context_mappers = {}

    # Create a LUT for context entries to match lowercase names
    lowercase_context_lut = {}
    for name in context:
        lowercase_context_lut[name.lower()] = name

    # converting each filter...
    for given_filter in args.filter:
        # print("processing filter:", given_filter)
        symbol = None
        symbol_position = -1
        # checking what symbole is being used for the curent filter
        for s in filter_symbols:
            symbol_position = given_filter.find(s)
            if symbol_position >= 0:
                symbol = s
                break

        # if there is no symbole match for this filter, we just ignore this filter
        # and go to the next one
        if not symbol:
            continue

        properties_no_mapping = given_filter[:symbol_position].split(".")

        # here, each prop will be preceded by "nsg:" or another context in use
        properties_with_mapping = []
        for prop in properties_no_mapping:
            (prop_name, list_index) = extractListIndexFromPropName(prop)
            if list_index is not None:
                context_mappers["rdf"] = context["rdf"]

            lowercase_prop = prop_name.lower()
            prop_with_mapping = ''

            #if prop in context:
            if lowercase_prop in lowercase_context_lut:
                prop_with_mapping = context[lowercase_context_lut[lowercase_prop]]["@id"]
                context_id = prop_with_mapping.split(":")[0]
                context_mappers[context_id] = context[context_id]
            else:
                prop_with_mapping = UNKNOWN_CONTEXT_SHORT + prop_name

            # adding /rdf:rest/rdf:first if necessary (when a prop name is given with [n] at the end)
            prop_with_mapping = prop_with_mapping + createRestFirstSequence(list_index)
            properties_with_mapping.append(prop_with_mapping)

        value = given_filter[symbol_position+len(symbol):]
        value_type = "string"

        # A value can possibly use a preffix, such as in "mba:997" (Allen CCF brain region id)
        # If this prefix is in the context, then it is replaced by the actual value
        position_semicolon = value.find(":")
        if position_semicolon > 0:
            prefix = value[:position_semicolon]
            prefix_lower = prefix.lower()
            if prefix_lower in lowercase_context_lut:
                value = context[lowercase_context_lut[prefix_lower]] + value[position_semicolon+1:]

        # If the value happens to be a number, we convert in into a number,
        # unless the operator is ~= which is reserved for string so we do not want
        # to cast to number because we still want to use a regex on this one.
        if symbol != "~=":
            try:
                value = float(value)
                value_int = int(value)
                # Check if it's an int or a float, to make sure we dont end up
                # with a trailing ".0" if the provided value is an int
                if abs(value - value_int) < sys.float_info.epsilon:
                    value = value_int
                value_type = "number"
            except:
                pass

        smarter_filter = {
            "id": randomString(),
            "properties": properties_with_mapping,
            "comparator": symbol,
            "value": value,
            "value_type": value_type
        }

        # special case of the "type" property, where we have to look up in the context for
        # the mapping of the value (and not only of the property name)
        if len(smarter_filter["properties"]) == 1 and smarter_filter["properties"][0] == context["type"]["@id"]:
            # deleting some useless properties
            del smarter_filter["comparator"]
            del smarter_filter["id"]
            del smarter_filter["properties"]

            # updating the field type
            smarter_filter["value_type"] = "type"
            lowercase_type = smarter_filter["value"].lower()
            if lowercase_type in lowercase_context_lut:
                smarter_filter["value"] = context[lowercase_context_lut[lowercase_type]]["@id"]
            else:
                smarter_filter["value"] = UNKNOWN_CONTEXT_SHORT + smarter_filter["value"]

        interpreted_filters.append(smarter_filter)

    return (interpreted_filters, context_mappers)


def buildSparqlQuery(filters, context_mappers, context_when_no_context):
    """
        Builds a SPARQL query
    """

    q = ""
    select_var_name = "?s"

    # add unknown prefix
    q += "PREFIX {} <{}>\n".format(UNKNOWN_CONTEXT_SHORT, context_when_no_context)

    # add the prefixes
    for pref in context_mappers:
        line = "PREFIX {}: <{}>\n".format(pref, context_mappers[pref])
        q += line

    # add the SELECT
    q += "SELECT {}\n".format(select_var_name)

    # add the WHEREs
    q += "WHERE {\n"
    for filter in filters:
        line = ""
        if filter["value_type"] == "type":
            line = "\t{} a {} .\n".format(select_var_name, filter["value"])
        else:
            line = "\t{} {} ?{} .\n".format(select_var_name, "/".join(filter["properties"]), filter["id"])
        q += line

    # add the FITLERs
    for filter in filters:
        line = ""
        if filter["value_type"] == "type":
            continue

        line = ""
        if filter["value_type"] == "string":
            if filter["comparator"] == "=":
                line = "\tFILTER(regex(str(?{}), \"^{}$\", \"i\"))\n".format(filter["id"], filter["value"])
            elif filter["comparator"] == "~=":
                line = "\tFILTER(regex(str(?{}), \"{}\", \"i\"))\n".format(filter["id"], filter["value"])
            elif filter["comparator"] == "!=":
                line = "\tFILTER(regex(str(?{}), \"^(?!{}).*$\", \"i\"))\n".format(filter["id"], filter["value"])

        elif filter["value_type"] == "number":
            line = "\tFILTER(?{} {} {}) .\n".format(filter["id"], filter["comparator"], filter["value"])
        q += line

    # close the query
    q += "}"
    return q


def getFilteredIds(args):
    # fetching the full context to lookup the context mappings
    context_payload = nexus.resources.fetch('neurosciencegraph', 'datamodels', 'https://neuroshapes.org')

    # stealing the context from the context payload. Could be @context or an element of it if it
    # happens to be a list. We just take the first one in this case. (not bulletproof but ssince this resource
    # is under the control of DKE, we will know if it changes...)
    context = None
    if isinstance(context_payload["@context"], dict):
        context = context_payload["@context"]
    elif isinstance(context_payload["@context"], list):
        for el in context_payload["@context"]:
            if isinstance(el, dict):
                context = el
                break

    context_when_no_context = args.nexus_env + "/resources/" + args.nexus_org + "/" + args.nexus_proj + "/_/"

    (filters, context_mappers) = translateFilters(args, context)

    query = buildSparqlQuery(filters, context_mappers, context_when_no_context)
    separator = "---------------------------------------------------------------------------"
    logging.info("{}\nSPARQL Query:\n{}\n{}".format(separator, query, separator))

    try:
        result = nexus.views.query_sparql(args.nexus_org, args.nexus_proj, query = query)
    except Exception as e:
        logging.error("❌ {}".format(e))
        if e.response.status_code == 400:
            logging.info("📄 Here is the original server error message:")
            logging.info(e.response.text.replace("\\n", "\n").replace("\\t", "\t"))
        exit(1)

    logging.info("{}\nSPARQL Response:\n{}\n{}".format(separator, json.dumps(result, indent=2), separator))

    ids = []
    for binding in result["results"]["bindings"]:
        ids.append(binding["s"]["value"])

    return ids


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

    # Getting the @ids from the query or simply from the list provided in args
    id = args.nexus_id
    if args.filter:
        ids = getFilteredIds(args)
        # print(ids)

        if len(ids) == 0:
            logging.error("❌ No match for the given filter.")
            exit(1)

        if len(ids) > 1:
            logging.warning("⚠️  There are multiple matches for the provided filters:")
            logging.warning("\n".join(ids))
            logging.warning("➡️  Using the first one.")

        id = ids[0]

    # Fetching the resource of interest
    try:
        resource = nexus.resources.fetch(args.nexus_org, args.nexus_proj, id, rev=args.nexus_rev, tag=args.nexus_tag)
    except Exception as e:
        logging.error("❌ {}".format(e))
        exit(1)

    output_extension = args.out.split(".").pop().lower()

    # Make sure the parent directory of the specified output exist, if not, create it
    parent_dir = os.path.dirname(args.out)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)

    # We extract the payload as a json file
    if args.payload:
        # If there is no file attached to the resource, we want to write the payload as a JSON
        # output file. Though if the extension of the given output is not json, then we raise an error and quit.
        if output_extension != "json":
            logging.error("❌ To save the payload, the extension of the file must be .json")
            exit(1)

        # removing the file if it exists
        if os.path.exists(args.out):
            os.remove(args.out)

        # sanitize from all the Nexus meta
        if args.keep_meta:
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

        logging.info("✅  File saved at {}".format(args.out))

        exit(0)

    # if we want the distribution file
    if "distribution" in resource:
        distribution = resource["distribution"]
        if isinstance(resource["distribution"], list):
            logging.info("Resource distribution property is a list. Therefore several files "\
                         "are linked to it: ")
            distrib_found = []
            for distrib in resource["distribution"]:
                logging.info(f"=> '{distrib['name']}'")
                for favor in args.favor:
                    prop_val_list = favor.split(":")
                    if (prop_val_list[0] in distrib and 
                        prop_val_list[1] == distrib[prop_val_list[0]]):
                        distrib_found.append((favor,distrib))
                        
            if distrib_found:
                distribution = distrib_found[0][1]
                for distrib_favor in distrib_found:
                    logging.info(f"--favor argument '{distrib_favor[0]}' corresponds to the "\
                                 f"'{distrib_favor[1]['name']}' distribution.")                    
                if len(distrib_found) > 1:
                    logging.warning("⚠️  More than one distribution has a correspondance with "\
                                    "the --favor arguments values.")
                    logging.info("Fetching the first corresponding distribution with "\
                                 f"'{distribution['name']}' as file name by default...")
                else:
                    logging.info(f"Fetching the corresponding distribution with "\
                                 f"'{distribution['name']}' as file name...")
                
            else:
                distribution = resource["distribution"][0]
                if not args.favor:
                    logging.warning("⚠️  --flavor argument has not been provided.")
                else:
                    logging.warning("⚠️  No distribution has a correspondance with a provided "\
                                    "--favor argument.")
                    logging.info("Fetching the first distribution with "\
                                 f"'{distribution['name']}' as file name by default...")
            
        if "distribution" in resource and "contentUrl" in distribution:
            linked_file_extension = distribution["name"].split(".").pop().lower()

            # check that extension of distant file and the output is the same (case not sensitive)
            if linked_file_extension != output_extension:
                logging.error(f"❌ The provided output extension is .{output_extension} "\
                              f"while the distant file extension is .{linked_file_extension} "\
                              "- They must be the same. ")
                exit(1)

            # fetching the file
            file_id = distribution["contentUrl"].split("/")[-1]
            file_payload = None
    
            # fetching just the payload of the file, to check first if the file hash is in 
            #sync with what is in the payload of the resource (distribution)
            try:
                file_payload = nexus.files.fetch(args.nexus_org, args.nexus_proj, file_id)
            except Exception as e:
                logging.error(f"❌ {e}")
                exit(1)

            # If hashes are different, it means the File has changed (new rev) and the 
            # resource was not updated accordingly, hence the metadata in the payload may 
            # be wrong.
            if distribution["digest"]["value"] != file_payload["_digest"]["_value"]:
                logging.error("❌ Hash mismatch. The resource distribution is no longer "\
                              "in sync with the file resource.")
                exit(1)

            # fetching the actual file (no longer only the payload)
            try:
                nexus.files.fetch(args.nexus_org, args.nexus_proj, file_id , 
                                  out_filepath=args.out)
                logging.info(f"✅  File saved at {args.out}")
            except Exception as e:
                logging.error(f"❌ {e}")
                exit(1)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
