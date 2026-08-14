import json


def normalize_product(
    api_product,
    schema_manager
):

    result = {}

    schema = schema_manager.schema


    for api_field, metadata in schema.items():

        column_name = metadata["column"]

        value = api_product.get(
            api_field
        )


        # ==================================
        # HANDLE NESTED API DATA
        # ==================================

        if isinstance(value, (dict, list)):

            value = json.dumps(
                value,
                ensure_ascii=False
            )


        # ==================================
        # ADD TO RESULT
        # ==================================

        result[column_name] = value


    return result