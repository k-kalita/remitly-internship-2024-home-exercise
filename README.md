# Remitly 2024 Summer Internship Home Exercise
This program is a solution to the Remitly 2024 Summer Internship home exercise. It can be used to verify whether a JSON definition of an *AWS::IAM::Policy* read from a file contains a single asterisk in the *Resource* field. The program will return `False` if the *Resource* field contains a single asterisk, and `True` otherwise. In case of a wrongly formatted definition the program will return an error message.

## How to run
To use the program, simply run the following command in the terminal:
```bash
python verify_policy.py <path_to_file>
```
where `<path_to_file>` is the path to the file containing the JSON definition of the *AWS::IAM::Policy*.

To run unit tests use the following command:
```bash
python verify_policy.py --test
```
or alternatively:
```bash
python -m unittest -v test.py
```

