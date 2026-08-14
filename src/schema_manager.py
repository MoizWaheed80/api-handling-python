from config import PRODUCT_SCHEMA


class SchemaManager:

    def __init__(self):

        self.schema = PRODUCT_SCHEMA.copy()


    # ======================================
    # GET CURRENT KNOWN FIELDS
    # ======================================

    def get_known_fields(self):

        return set(
            self.schema.keys()
        )


    # ======================================
    # DETECT NEW FIELDS
    # ======================================

    def detect_new_fields(
        self,
        api_product
    ):

        api_fields = set(
            api_product.keys()
        )

        known_fields = (
            self.get_known_fields()
        )

        new_fields = (
            api_fields - known_fields
        )

        return new_fields


    # ======================================
    # DETECT MISSING FIELDS
    # ======================================

    def detect_missing_fields(
        self,
        api_product
    ):

        api_fields = set(
            api_product.keys()
        )

        known_fields = (
            self.get_known_fields()
        )

        missing_fields = (
            known_fields - api_fields
        )

        return missing_fields


    # ======================================
    # ADD NEW FIELD
    # ======================================

    def add_new_field(
        self,
        field_name,
        sample_value
    ):

        detected_type = self.detect_type(
            sample_value
        )

        self.schema[field_name] = {
            "column": field_name,
            "type": detected_type
        }

        print(
            f"NEW FIELD DETECTED: "
            f"{field_name}"
        )

        print(
            f"Added to schema as "
            f"{field_name} "
            f"({detected_type})"
        )


    # ======================================
    # TYPE DETECTION
    # ======================================

    @staticmethod
    def detect_type(value):

        if isinstance(value, bool):

            return "bool"

        if isinstance(value, int):

            return "int"

        if isinstance(value, float):

            return "float"

        if isinstance(value, dict):

            return "json"

        if isinstance(value, list):

            return "json"

        return "string"