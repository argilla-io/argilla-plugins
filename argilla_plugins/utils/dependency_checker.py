import importlib.util


def import_package(package_name):
    """Import a package and return it.

    Args:
        package_name (str): The name of the package to import.

    Returns:
        The imported package.
    """

    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise Exception(
            f"Package {package_name} not found. To use this plugin first install the"
            f" required package `pip install {package_name}`."
        )
    else:
        return True
