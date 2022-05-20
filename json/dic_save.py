"""Demonstration of how to store and load python dictionaries to disk using
human-readable formats (not pickle).

Examples in this file include JSON, YAML, and TOML.

"""
import pickle
import json

import numpy as np
import yaml  # pyyaml package name
import toml


def main():
    """Stores the dictionary to each file, then loads it back and prints the
    result. The printed result shows if the reloaded data has changed in any
    way. i.e. conversions from ints to strings, etc."""

    parameters = {
        "glossary": {
            "title": "example glossary",
            "GlossDiv": {
                "title": "S",
                "list-float": [
                    0.0312,
                    1.1,
                    2.145,
                    3.0,
                    4.3123,
                    5.2,
                ],
                "list-int": ([
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                ]),
                "GlossSeeAlso": [
                    "GML",
                    "XML",
                ],
                "third-level": {
                    "more-data": 342151,
                },
            }
        }
    }

    demo_json(parameters)

    parameters['ndarray'] = np.random.rand(5)

    demo_yaml(parameters)

    demo_toml(parameters)

    demo_pickle(parameters)


def demo_json(parameters):
    """JavaScript Object Notation

    Pros
    ----
    - JSON is part of the standard library.
    - Very old and well known.

    Gotchas
    -------
    - No numpy arrays; it only takes built-in data structures. Use toList().
    - Dictionary keys must be strings; non-string keys will be converted on
      write.
    """
    with open('new-data.json', 'w') as f:
        json.dump(parameters, f, indent=4)

    with open('new-data.json', 'r') as f:
        loaded_parameters = json.load(f)

    print(loaded_parameters)


def demo_yaml(parameters):
    """YAML Ain't Markup Language

    Pros
    ----
    - Keys do not need to be strings.
    - The syntax is also less verbose because it doesn't use brackets.

    Gotchas
    -------
    - YAML is not part of the standard library.
    - Syntax for storing NumPy arrays is verbose!
    """

    with open('new-data.yaml', 'w') as f:
        # Can use yaml.CDumper for faster dump/load if available
        yaml.dump(parameters, f, indent=4, Dumper=yaml.Dumper)

    with open('new-data.yaml', 'r') as f:
        loaded_parameters = yaml.load(f, Loader=yaml.Loader)

    print(loaded_parameters)


def demo_toml(parameters):
    """Tom's Obvious, Minimal Language

    Pros
    ----
    - Syntax is flatter than YAML, JSON

    Gotchas
    -------
    - TOML is not part of the standard library.
    - Keys must be strings
    - No numpy arrays; arrays automatically converted to lists of STRING!
    """

    with open('new-data.toml', 'w') as f:
        toml.dump(parameters, f)

    with open('new-data.toml', 'r') as f:
        loaded_parameters = toml.load(f)

    print(loaded_parameters)


def demo_pickle(parameters):
    """Pickle saves and load exactly as it was, but is not human readable."""
    with open('new-data.pickle', 'wb') as f:
        pickle.dump(parameters, f)

    with open('new-data.pickle', 'rb') as f:
        loaded_parameters = pickle.load(f)

    print(loaded_parameters)

if __name__ == '__main__':
    main()