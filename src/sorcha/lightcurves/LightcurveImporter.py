from .base_lightcurve import AbstractLightCurve


def register_lc_subclasses():
    """This method will identify all of the subclasses of `AbstractLightCurve`
    and build a dictionary that maps `name : subclass`.

    Returns
    -------
    dict
        A dictionary of all of subclasses of `AbstractLightCurve`. Where
        the str returned from `subclass.name_id()` is the key, and the class is
        the value.

    Raises
    ------
    ValueError
        If a duplicate key is found, a ValueError will be raised. This would
        likely occur if a user copy/pasted an existing subclass but failed to
        update the unique name_id string.
    """
    subclass_dict = {}
    for subcls in AbstractLightCurve.__subclasses__():
        if subcls.name_id() in subclass_dict:
            raise ValueError(
                "Attempted to add duplicate Lightcurve calculator name to LC_METHODS: "
                + str(subcls.name_id())
            )

        subclass_dict[subcls.name_id()] = subcls

    return subclass_dict


def update_lc_subclasses():
    """This function is used to register newly created subclasses of the
    `AbstractLightCurve`.
    """
    for subcls in AbstractLightCurve.__subclasses__():
        if subcls.name_id() not in LC_METHODS.keys():
            LC_METHODS[subcls.name_id()] = subcls


# The dictionary of all available subclasses of the AbstractLightCurve.
LC_METHODS = register_lc_subclasses()