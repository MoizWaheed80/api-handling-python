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

        result[column_name] = value


    return result