"""
Утилітарні функції для Magento бібліотеки.
"""

from .validation import (
    ValidationError,
    validate_sku,
    validate_email_address as validate_email,
    validate_phone,
    validate_price,
    validate_weight,
    validate_status,
    validate_visibility,
    validate_url_key,
    validate_attribute_set_id,
    validate_product_type,
    validate_product_data,
    validate_customer_data,
    validate_search_criteria
)

from .serialization import (
    JSONEncoder,
    JSONDecoder,
    serialize_to_json,
    deserialize_from_json,
    serialize_model,
    deserialize_model,
    serialize_to_binary,
    deserialize_from_binary,
    to_magento_format,
    from_magento_format,
    create_search_criteria
)

from .helpers import (
    format_price,
    parse_date,
    generate_url_key,
    clean_html,
    safe_get,
    generate_sku,
    generate_random_string,
    hash_string,
    build_url,
    is_valid_url,
    chunk_list,
    flatten_dict,
    get_current_timestamp,
    bytes_to_human_readable,
    mask_sensitive_data
)

__all__ = [
    # Validation
    'ValidationError',
    'validate_sku',
    'validate_email',
    'validate_phone',
    'validate_price',
    'validate_weight',
    'validate_status',
    'validate_visibility',
    'validate_url_key',
    'validate_attribute_set_id',
    'validate_product_type',
    'validate_product_data',
    'validate_customer_data',
    'validate_search_criteria',

    # Serialization
    'JSONEncoder',
    'JSONDecoder',
    'serialize_to_json',
    'deserialize_from_json',
    'serialize_model',
    'deserialize_model',
    'serialize_to_binary',
    'deserialize_from_binary',
    'to_magento_format',
    'from_magento_format',
    'create_search_criteria',

    # Helpers
    'format_price',
    'parse_date',
    'generate_url_key',
    'clean_html',
    'safe_get',
    'generate_sku',
    'generate_random_string',
    'hash_string',
    'build_url',
    'is_valid_url',
    'chunk_list',
    'flatten_dict',
    'get_current_timestamp',
    'bytes_to_human_readable',
    'mask_sensitive_data'
]