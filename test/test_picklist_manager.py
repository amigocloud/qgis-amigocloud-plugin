import pytest
from utils.PicklistManager import PicklistManager

pm = PicklistManager()

schema1 = [
        {
            "name": "txtfield",
            "alias": "txtfield",
            "default": "this is value float",
            "nullable": True,
            "editable": True,
            "visible": True,
            "type": "string"
        },
        {
            "name": "pk_valuefloat",
            "nullable": True,
            "default": None,
            "editable": True,
            "choices": [
                {
                    "code": 0.1,
                    "value": "pkvf_first"
                },
                {
                    "code": 1.1,
                    "value": "pkvf_second"
                },
                {
                    "code": 2.1,
                    "value": "pkvf_third"
                }
            ],
            "visible": True,
            "alias": "pk_valueFloat",
            "type": "float"
        },
        {
            "name": "wkb_geometry",
            "visible": True,
            "geometry_type": "POINT",
            "nullable": False,
            "editable": True,
            "alias": "wkb geometry",
            "type": "geometry"
        },
        {
            "name": "amigo_id",
            "nullable": False,
            "default": "GENERATE_UUID",
            "auto_populate": True,
            "max_length": 32,
            "type": "string"
        }
    ]


@pytest.mark.parametrize("test_input, expected_output",
                            [
                                (("b'pk_ds_valueFloat'", schema1), ("b'pk_ds_valueFloat'", 'pk_valuefloat', {'pkvf_second': 1.1, 'pkvf_first': 0.1, 'pkvf_third': 2.1}))
                            ]
                         )
def test_manage_picklists(test_input, expected_output):

    ds_name = test_input[0]
    schema = test_input[1]

    result = pm.manage_picklists(ds_name, schema)

    assert result[0] == expected_output


