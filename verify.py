import json
from pathlib import Path
from enum import Enum


class ErrorMsg(Enum):
    """Error messages raised when the verified file or `AWS::IAM::Policy` definition is invalid."""
    INVALID_FILE = 'Provided file is not a valid JSON file'
    MISSING_FILE = 'Provided file does not exist'
    INVALID_POLICY_DEF = 'Provided policy definition is not an object'
    MISSING_STATEMENT = 'PolicyDocument.Statement is missing in the JSON data'
    INVALID_STATEMENT_DEF = 'PolicyDocument.Statement is not defined as an object or a list of objects'
    MISSING_RESOURCE = 'Resource field required in permission defining policy is missing'
    INVALID_RESOURCE_DEF = 'Resource field in policy statement is not defined as a string or a list of strings'


def verify_json_file(json_file: str | Path) -> bool:
    """
    Attempt to read a JSON file defining an `AWS::IAM::Policy` and verify its contents (passing the data to
    :func:`verify_json_data`).

    :param json_file: Path to the JSON file
    :type json_file: str | Path
    :return: ``True`` if the `Resource` field in the policy statement(s) is not set to `*`, ``False`` otherwise
    :rtype: bool
    :raises ValueError: If the file does not exist or is not a valid JSON file
    """
    try:
        with open(str(json_file)) as f:
            try:
                return verify_json_data(json.load(f))
            except json.JSONDecodeError:
                raise ValueError(ErrorMsg.INVALID_FILE.value)
    except FileNotFoundError:
        raise ValueError(ErrorMsg.MISSING_FILE.value)


def verify_json_data(data: dict) -> bool:
    """
    Verify the contents of a JSON object defining an `AWS::IAM::Policy` (passes statement data to
    :func:`verify_policy_statement` for verification).

    :param data: JSON object defining an `AWS::IAM::Policy`
    :type data: dict
    :return: ``True`` if the `Resource` field in the policy statement(s) is not set to `*`, ``False`` otherwise
    :rtype: bool
    :raises ValueError: If the provided JSON data is not an object, if `PolicyDocument.Statement` is missing, or if
                       `PolicyDocument.Statement` is not defined as a list or an object
    """
    if not isinstance(data, dict):
        raise ValueError(ErrorMsg.INVALID_POLICY_DEF.value)

    policy_statement = data.get('PolicyDocument', {}).get('Statement')

    if not policy_statement:
        raise ValueError(ErrorMsg.MISSING_STATEMENT.value)

    if isinstance(policy_statement, dict):
        policy_statement = [policy_statement]

    if not isinstance(policy_statement, list):
        raise ValueError(ErrorMsg.INVALID_STATEMENT_DEF.value)
    elif any(not isinstance(statement, dict) for statement in policy_statement):
        raise ValueError(ErrorMsg.INVALID_STATEMENT_DEF.value)

    for statement in policy_statement:
        if not _verify_policy_statement(statement):
            return False

    return True


def _verify_policy_statement(statement: dict) -> bool:
    """
    :param statement: JSON object defining a policy `Statement`
    :type statement: dict
    :return: ``True`` if the `Resource` field in the policy statement is not set to `*`, ``False`` otherwise
    :rtype: bool
    :raises ValueError: If the `Resource` field is missing
    """
    resource = statement.get('Resource')

    if not resource:
        raise ValueError(ErrorMsg.MISSING_RESOURCE.value)
    if not isinstance(resource, str) and not (isinstance(resource, list) and all(isinstance(r, str) for r in resource)):
        raise ValueError(ErrorMsg.INVALID_RESOURCE_DEF.value)

    resource = resource if not (isinstance(resource, list) and len(resource) == 1) else resource[0]
    return resource != '*'
