from datastore_queries import get_config_dictionary


def refresh_config(app):
    """
    Set or refresh the CONFIG dictionary (used in templates) based on datastore Config entities
    """
    app.jinja_env.globals['CONFIG'] = get_config_dictionary()
