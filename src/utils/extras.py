def format_placeholders(string: str, placeholders: dict):
    """Formats {} like placeholders in a string"""

    class CustomDict(dict):
        def __missing__(self, key):
            return " "
    
    dict_instance = CustomDict(**placeholders)

    return string.format_map(dict_instance)
