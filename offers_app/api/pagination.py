from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Page number pagination for offers supporting dynamic page_size."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100