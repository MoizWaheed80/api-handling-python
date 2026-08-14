from copy import deepcopy
from typing import Any

from config import PRODUCT_SCHEMA


class SchemaManager:
    """Manage API schema changes without deleting existing fields."""

    def __init__(self) -> None:
        # Keep our own copy of the configured schema.
        self.schema = deepcopy(PRODUCT_SCHEMA)

    def get_known_fields(self) -> set[str]:
        """Return all fields currently known to the pipeline."""

        return set(self.schema.keys())

    def detect_new_fields(
        self,
        api_product: dict[str, Any]
    ) -> set[str]:
        """Find fields that exist in the API but not in our schema."""

        api_fields = set(api_product.keys())
        known_fields = self.get_known_fields()

        return api_fields - known_fields

    def detect_missing_fields(
        self,
        api_product: dict[str, Any]
    ) -> set[str]:
        """Find known fields missing from the current API record."""

        api_fields = set(api_product.keys())
        known_fields = self.get_known_fields()

        return known_fields - api_fields

    def add_new_field(
        self,
        field_name: str,
        sample_value: Any
    ) -> None:
        """Add a newly discovered API field to the schema."""

        self.schema[field_name] = {
            "column": field_name,
            "type": self.detect_type(sample_value)
        }

    @staticmethod
    def detect_type(value: Any) -> str:
        """Detect the basic type of an API field."""

        if isinstance(value, bool):
            return "bool"

        if isinstance(value, int):
            return "int"

        if isinstance(value, float):
            return "float"

        if isinstance(value, (dict, list)):
            return "json"

        return "string"