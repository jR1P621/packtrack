from rest_framework import serializers
from typing import List


class NestedDynamicFieldsModelSerializer(serializers.ModelSerializer):
    '''
    Allows dynamic control over the depth and information presented in nested serializers.
    '''

    def __init__(self, *args, **kwargs):

        def parse_nested_fields(fields: List[str]) -> dict:
            '''
            Parses the `fields` parameter to get 
            '''
            field_object = {"fields": []}
            for f in fields:
                obj = field_object

                # get nested serializer fields
                nested_fields = f.split("__")
                for v in nested_fields:
                    # add this objects field
                    if v not in obj["fields"]:
                        obj["fields"].append(v)
                    # add nested object's field
                    if nested_fields.index(v) < len(nested_fields) - 1:
                        obj[v] = obj.get(v, {"fields": []})
                        obj = obj[v]
            return field_object

        def select_nested_fields(serializer, fields):
            '''
            Wrapper to retrieve data from serializer fields or nested serializer fields
            '''
            for k in fields:
                if k == "fields":
                    fields_to_include(serializer, fields[k])
                else:
                    select_nested_fields(serializer.fields[k], fields[k])

        def fields_to_include(serializer, fields):
            '''
            Drop any fields that are not specified in the `fields` argument.
            '''
            allowed = set(fields)
            if isinstance(serializer, serializers.ListSerializer):
                existing = set(serializer.child.fields.keys())
                for field_name in existing - allowed:
                    serializer.child.fields.pop(field_name)
            else:
                existing = set(serializer.fields.keys())
                for field_name in existing - allowed:
                    serializer.fields.pop(field_name)

        # Don't pass the `fields` arg up to the superclass
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            fields = parse_nested_fields(fields)
            # Drop any fields that are not specified in the `fields` argument.
            select_nested_fields(self, fields)
