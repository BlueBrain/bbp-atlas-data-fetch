import os
import pytest
import requests
from bba_data_fetch.main import (
    randomString,
    extractListIndexFromPropName,
    createRestFirstSequence,
    translateFilters,
    buildSparqlQuery,
    getFilteredIds,
    parse_args,
    main,
)

test_folder = os.environ["TEST_FOLDER"]


def test_randomString():

    result = randomString()
    assert len(result) == 5
    assert isinstance(result, str)


def test_extractListIndexFromPropName():

    prop = "prop_name[10]"
    (prop_name, list_index) = extractListIndexFromPropName(prop)
    assert prop_name == "prop_name"
    assert list_index == 10

    prop = "prop_name"
    (prop_name, list_index) = extractListIndexFromPropName(prop)
    assert prop_name == "prop_name"
    assert list_index is None

    prop = "prop_name['not_an_int']"
    (prop_name, list_index) = extractListIndexFromPropName(prop)
    assert prop_name == "prop_name['not_an_int']"
    assert list_index is None

    prop = []
    with pytest.raises(TypeError) as e:
        extractListIndexFromPropName(prop)
    assert "expected string or bytes-like object" in str(e.value)


def test_createRestFirstSequence():

    list_index = 3
    result = createRestFirstSequence(list_index)
    assert result == "/rdf:rest/rdf:rest/rdf:rest/rdf:first"

    list_index = None
    result = createRestFirstSequence(list_index)
    assert result == ""

    list_index = "not_an_index"
    with pytest.raises(TypeError) as e:
        createRestFirstSequence(list_index)
    assert "can't multiply sequence by non-int of type 'str'" in str(e.value)


def test_buildSparqlQuery():

    context_when_no_context = "staging/resources/bbp/atlas/_/"
    context = {
        "@context": {
            "Property_1": {"@id": "nsg:Property_1"},
            "Property_2": {"@id": "prov:Property_2"},
        }
    }
    filters = [
        {
            "id": "dbgxf",  # some random string
            "properties": ["property", "name"],
            "comparator": "=",
            "value": "Value of property",
            "value_type": "string",
        }
    ]

    result = buildSparqlQuery(filters, context, context_when_no_context)
    assert (
        result == "PREFIX unknown: <staging/resources/bbp/atlas/_/>\n"
        "PREFIX @context: <{'Property_1': {'@id': 'nsg:Property_1'}, 'Property_2': "
        "{'@id': "
        "'prov:Property_2'}}>\n"
        "SELECT ?s\n"
        "WHERE {\n"
        "\t?s property/name ?dbgxf .\n"
        '\tFILTER(regex(str(?dbgxf), "^Value of property$", "i"))\n}'
    )

    filters = [
        {
            "id": "dbgxf",
            "properties": ["property", "name"],
            "comparator": "!=",
            "value": "Value of property",
            "value_type": "number",
        },
        {
            "id": "dbgxf",
            "properties": ["property", "name"],
            "comparator": "~=",
            "value": "Value of property",
            "value_type": "type",
        },
    ]

    result = buildSparqlQuery(filters, context, context_when_no_context)
    assert (
        result == "PREFIX unknown: <staging/resources/bbp/atlas/_/>\n"
        "PREFIX @context: <{'Property_1': {'@id': 'nsg:Property_1'}, 'Property_2': "
        "{'@id': "
        "'prov:Property_2'}}>\n"
        "SELECT ?s\n"
        "WHERE {\n"
        "\t?s property/name ?dbgxf .\n"
        "\t?s a Value of property .\n"
        "\tFILTER(?dbgxf != Value of property) .\n}"
    )

    filters = []

    result = buildSparqlQuery(filters, context, context_when_no_context)
    assert (
        result == "PREFIX unknown: <staging/resources/bbp/atlas/_/>\n"
        "PREFIX @context: <{'Property_1': {'@id': 'nsg:Property_1'}, 'Property_2': "
        "{'@id': "
        "'prov:Property_2'}}>\n"
        "SELECT ?s\n"
        "WHERE {\n}"
    )

    context_when_no_context = None
    assert (
        result == "PREFIX unknown: <staging/resources/bbp/atlas/_/>\n"
        "PREFIX @context: <{'Property_1': {'@id': 'nsg:Property_1'}, 'Property_2': "
        "{'@id': "
        "'prov:Property_2'}}>\n"
        "SELECT ?s\n"
        "WHERE {\n}"
    )

    filters = "not a list of dict"
    with pytest.raises(TypeError) as e:
        buildSparqlQuery(filters, context, context_when_no_context)
    assert "string indices must be integers" in str(e.value)

    context = None
    with pytest.raises(TypeError) as e:
        buildSparqlQuery(filters, context, context_when_no_context)
    assert str(e.value) == "'NoneType' object is not iterable"


def test_translateFilters():

    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--filter",
        'property.name="data"',
        "resolution.value~=25",
        "mba:region.number>=1",
        "worldMatrix[0]<10",
        'wrong.prop!"wrong"',
    ]
    args = parse_args(list_of_args)

    context = {
        "Property_1": {"@id": "nsg:Property_1"},
        "Property_2": {"@id": "prov:Property_2"},
        "region": {"@id": "mba:region"},
        "worldMatrix": {"@id": "rdf:worldMatrix"},
        "type": {"@id": "rdf:type"},
        "rdf": "adress/syntax",
    }

    (filter_datastructure, context_mappers) = translateFilters(args, context)

    filter_properties = ["properties", "comparator", "value", "value_type"]
    filter_1 = [["unknown:property", "unknown:name"], "=", '"data"', "string"]
    filter_2 = [["unknown:resolution", "unknown:value"], "~=", "25", "string"]
    filter_3 = [["unknown:mba:region", "unknown:number"], ">=", 1, "number"]
    filter_4 = [["rdf:worldMatrix/rdf:first"], "<", 10, "number"]
    filters_dict = [
        dict(zip(filter_properties, filter_1)),
        dict(zip(filter_properties, filter_2)),
        dict(zip(filter_properties, filter_3)),
        dict(zip(filter_properties, filter_4)),
    ]

    for index in range(0, len(filters_dict)):
        for prop in filter_properties:
            assert filter_datastructure[index][prop] == filters_dict[index][prop]

    assert context_mappers == {"rdf": "adress/syntax"}


def test_getFilteredIds():
    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--filter",
        'property.name="data"',
    ]
    args = parse_args(list_of_args)

    with pytest.raises(Exception) as e:
        getFilteredIds(args)


def test_main():

    # no --filter and --nexus-id args
    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
    ]

    with pytest.raises(SystemExit) as e:
        main(list_of_args)
    assert e.value.code == 1

    # --filter and --nexus-id args are mutually exclusive
    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--filter",
        "filter",
        "--nexus-id",
        "id",
    ]

    with pytest.raises(SystemExit) as e:
        main(list_of_args)
    assert e.value.code == 1

    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--nexus-id",
        "id",
    ]

    with pytest.raises(SystemExit) as e:
        main(list_of_args)
    assert e.value.code == 1

    list_of_args = [
        "--nexus-token",
        "",
        "--nexus-env",
        "env/",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--filter",
        "filter",
        "--verbose",
    ]

    with pytest.raises(requests.exceptions.MissingSchema) as e:
        main(list_of_args)
    assert "Invalid URL" in str(e.value)

    list_of_args = [
        "--nexus-token",
        "",
        "--forge-config",
        "cfg/forge-config.yml",
        "--nexus-env",
        "env/",
        "--nexus-org",
        "org",
        "--nexus-proj",
        "proj",
        "--out",
        test_folder,
        "--nexus-id",
        "id",
    ]

    with pytest.raises(SystemExit) as e:
        main(list_of_args)
    assert e.value.code == 1
