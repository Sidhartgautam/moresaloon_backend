from rest_framework.pagination import PageNumberPagination
from math import ceil

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        page_size = self.page.paginator.per_page
        total_pages = ceil(total_items / 10)  # Calculate total pages

        return {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "count": total_items,
            "page_number": self.page.number,  # Current page number
            "total_pages": total_pages,  # Total number of pages
            "results": data
        }