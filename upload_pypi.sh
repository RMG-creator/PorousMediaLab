#!/bin/bash
# uploading pip script


echo "uploading pip package"
# python setup.py sdist upload -r pypi

python setup.py sdist
twine upload --repository pypi dist/*
