def normalize_product(api_product):

    result = {}

    result["product_id"] = api_product.get("id")

    result["product_name"] = (
        api_product.get("title") or None
    )

    result["description"] = (
        api_product.get("description") or None
    )

    result["price"] = api_product.get("price")

    result["discount_percentage"] = (
        api_product.get("discountPercentage")
    )

    result["rating"] = api_product.get("rating")

    result["stock"] = api_product.get("stock")

    result["brand"] = (
        api_product.get("brand") or None
    )

    result["category"] = (
        api_product.get("category") or None
    )

    result["sku"] = (
        api_product.get("sku") or None
    )

    result["weight"] = api_product.get("weight")

    result["warranty_information"] = (
        api_product.get("warrantyInformation") or None
    )

    result["shipping_information"] = (
        api_product.get("shippingInformation") or None
    )

    result["availability_status"] = (
        api_product.get("availabilityStatus") or None
    )

    result["return_policy"] = (
        api_product.get("returnPolicy") or None
    )

    result["minimum_order_quantity"] = (
        api_product.get("minimumOrderQuantity")
    )

    return result


def normalize_dimensions(api_product):

    dimensions = api_product.get(
        "dimensions",
        {}
    )

    result = {}

    result["product_id"] = api_product.get("id")

    result["width"] = dimensions.get("width")

    result["height"] = dimensions.get("height")

    result["depth"] = dimensions.get("depth")

    return result


def normalize_reviews(api_product):

    reviews = api_product.get(
        "reviews",
        []
    )

    results = []

    for review in reviews:

        result = {}

        result["product_id"] = api_product.get("id")

        result["rating"] = review.get("rating")

        result["comment"] = (
            review.get("comment") or None
        )

        result["reviewer_name"] = (
            review.get("reviewerName") or None
        )

        result["reviewer_email"] = (
            review.get("reviewerEmail") or None
        )

        result["review_date"] = (
            review.get("date") or None
        )

        results.append(result)

    return results