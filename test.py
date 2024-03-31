from typing import List
import json
import unittest

from verify import verify_json_file, verify_json_data, ErrorMsg
from config import TEST_RESOURCES_DIR


class TestVerifyJson(unittest.TestCase):
    def setUp(self) -> None:
        self.resource_dir = TEST_RESOURCES_DIR

    def test_verify_valid_file(self) -> None:
        """Test that a valid JSON file is verified successfully."""
        self.assertTrue(verify_json_file(self.resource_dir / 'policy.json'))
        
    def test_verify_invalid_file(self) -> None:
        """Test that attempting to verify invalid files raises the appropriate exceptions."""
        test_cases = [
            ('policy.yaml', ErrorMsg.INVALID_FILE),
            ('missing.json', ErrorMsg.MISSING_FILE),
            ('list.json', ErrorMsg.INVALID_POLICY_DEF),
            ('missing_statement.json', ErrorMsg.MISSING_STATEMENT),
            ('invalid_statement.json', ErrorMsg.INVALID_STATEMENT_DEF),
            ('invalid_statement_list.json', ErrorMsg.INVALID_STATEMENT_DEF),
            ('missing_resource.json', ErrorMsg.MISSING_RESOURCE),
            ('invalid_resource.json', ErrorMsg.INVALID_RESOURCE_DEF),
        ]

        for file, expected in test_cases:
            with self.subTest(file=file, expected=expected):
                with self.assertRaises(ValueError) as cm:
                    verify_json_file(self.resource_dir / file)
                self.assertEqual(str(cm.exception), expected.value)

    def test_verify_valid_data(self) -> None:
        """Test that valid definitions of `AWS::IAM::Policy` with a single statement are verified successfully."""
        test_cases = [
            ('*', False),
            (['*'], False),
            ('testResource', True),
            ('* testResource', True),
            (['testResource'], True),
            (['testResource', '*'], True),
        ]

        for resource, expected in test_cases:
            with self.subTest(resource=resource, expected=expected):
                with open((self.resource_dir / 'policy.json')) as f:
                    data = json.load(f)
                    data['PolicyDocument']['Statement']['Resource'] = resource
                    self.assertEqual(verify_json_data(data), expected)

    def test_verify_valid_data_multiple_statements(self) -> None:
        """Test that valid definitions of `AWS::IAM::Policy` with multiple statements are verified successfully."""
        test_cases = [
            (['*'], False),
            (['testResource', '*'], False),
            (['testResource', ['*']], False),
            (['testResource'], True),
            (['testResource1', 'testResource2'], True),
            (['testResource1', ['testResource2', '*']], True),
        ]

        for resources, expected in test_cases:
            with self.subTest(resources={f'statement_{i}': resource for i, resource in enumerate(resources)},
                              expected=expected):
                with open((self.resource_dir / 'policy.json')) as f:
                    data = json.load(f)
                    statements = [create_statement(resource) for resource in resources]
                    data['PolicyDocument']['Statement'] = statements
                    self.assertEqual(verify_json_data(data), expected)


def create_statement(resource: str | List[str]) -> dict:
    return {
        'Effect': 'Allow',
        'Action': 'test:Action',
        'Resource': resource,
    }
