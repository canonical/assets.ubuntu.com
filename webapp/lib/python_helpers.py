def shared_items(list_one, list_two):
    """
    Return the list of items that are shared
    between two lists
    """

    return [x for x in list_one.keys() if x in list_two]
