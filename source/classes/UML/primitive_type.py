from source.utils import get_primitive_type


class PrimitiveType:
    def __init__(self, href):
        self.type = get_primitive_type(href)
