"""
test_framework.py
Automated testing framework for authorization enforcement.
Compares API behavior against the formal policy model.
"""

from policy_model import AuthorizationPolicy
from api_client import ApiClient
from typing import List, Dict
import json
from datetime import datetime


class TestResult:
    """Represents the result of a single test case"""

    def __init__(self, scenario_id: int, scenario: Dict,
                 expected: str, actual: str, passed: bool):
        self.scenario_id = scenario_id
        self.scenario = scenario
        self.expected = expected
        self.actual = actual
        self.passed = passed
        self.timestamp = datetime.now()

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{status} - Scenario {self.scenario_id}"


class AuthorizationTestFramework:
    """
    Automated testing framework for authorization logic.
    Systematically tests all possible scenarios.
    """

    def __init__(self):
        self.policy = AuthorizationPolicy()
        # Use HTTP client pointing at local Flask server
        # Ensure the server is running (default: http://localhost:5000)
        self.api = ApiClient(base_url='http://localhost:5000')
        self.test_results: List[TestResult] = []

        # Test fixture IDs (will be populated during setup)
        self.users = {}
        self.files = {}

        print("Authorization Test Framework initialized")

    def setup_test_fixtures(self):
        """
        Create test users and files in the API.
        This sets up the environment for testing.
        """
        print("\n" + "=" * 60)
        print("SETTING UP TEST FIXTURES")
        print("=" * 60)

        # Reset API state (call server)
        self.api.reset()

        # Create organizations
        org_acme = "org-acme"
        org_external = "org-external"

        # Create test users
        print("\n1) Creating test users...")
        owner_resp = self.api.create_user("owner@acme.com", org_acme, "Test Owner")
        collab_resp = self.api.create_user("collab@acme.com", org_acme, "Test Collaborator")
        org_resp = self.api.create_user("orgmember@acme.com", org_acme, "Test OrgMember")
        ext_resp = self.api.create_user("external@other.com", org_external, "Test External")

        self.users = {
            'owner': owner_resp.data['user_id'],
            'collaborator': collab_resp.data['user_id'],
            'org_member': org_resp.data['user_id'],
            'external': ext_resp.data['user_id']
        }

        print(f"   Created 4 test users")
        for role, uid in self.users.items():
            print(f"      - {role}: {uid[:8]}...")

        # Create test files with different visibility levels
        print("\n2) Creating test files...")
        owner_id = self.users['owner']

        private_resp = self.api.create_file(owner_id, "test-private.txt",
                            "private", "Private content")
        shared_resp = self.api.create_file(owner_id, "test-shared.txt",
                           "shared", "Shared content")
        org_resp = self.api.create_file(owner_id, "test-org.txt",
                        "org_public", "Org content")
        public_resp = self.api.create_file(owner_id, "test-public.txt",
                           "public", "Public content")

        self.files = {
            'private': private_resp.data['file_id'],
            'shared': shared_resp.data['file_id'],
            'org_public': org_resp.data['file_id'],
            'public': public_resp.data['file_id']
        }

        print(f"   Created 4 test files")
        for visibility, fid in self.files.items():
            print(f"      - {visibility}: {fid[:8]}...")

        # Grant collaboration permissions
        print("\n3) Setting up collaboration permissions...")
        collab_id = self.users['collaborator']

        # Collaborator gets 'edit' permission on shared file
        self.api.share_file(self.files['shared'], owner_id, collab_id, 'edit')

        # Collaborator gets 'edit' permission on private file
        self.api.share_file(self.files['private'], owner_id, collab_id, 'edit')

        print(f"   Granted collaboration permissions")

        print("\n" + "=" * 60)
        print("TEST FIXTURES READY")
        print("=" * 60 + "\n")

    def execute_api_action(self, file_id: str, user_id: str, action: str) -> str:
        """
        Execute an action on the API and return ALLOW or DENY.

        Args:
            file_id: The file to access
            user_id: The user attempting access
            action: The action to perform (read, edit, delete, share)

        Returns:
            'ALLOW' if successful (status 200), 'DENY' if forbidden (status 403)
        """
        response = None

        if action == 'read':
            response = self.api.get_file(file_id, user_id)
        elif action == 'edit':
            response = self.api.update_file(file_id, user_id, "Updated content")
        elif action == 'delete':
            # Use a non-destructive authorization check endpoint to avoid removing test fixtures
            authorized = self.api.check_authorization(file_id, user_id, 'delete')
            return 'ALLOW' if authorized else 'DENY'
        elif action == 'share':
            # Share with a dummy target user
            target_id = self.users['external']
            response = self.api.share_file(file_id, user_id, target_id, 'read')

        if response:
            # 200 = success (ALLOW), 403 = forbidden (DENY), 404 = not found
            if response.status_code == 200 or response.status_code == 201:
                return 'ALLOW'
            elif response.status_code == 403:
                return 'DENY'
            else:
                return 'ERROR'

        return 'ERROR'

    def test_scenario(self, scenario: Dict) -> TestResult:
        """
        Test a single authorization scenario.

        Args:
            scenario: Dictionary containing scenario details

        Returns:
            TestResult object with pass/fail information
        """
        audience = scenario['audience']
        visibility = scenario['visibility']
        action = scenario['action']
        expected = scenario['expected_result']

        # Map scenario to actual API entities
        user_id = self.users[audience]
        file_id = self.files[visibility]

        # Execute the action on the API
        actual = self.execute_api_action(file_id, user_id, action)

        # Compare expected vs actual
        passed = (expected == actual)

        return TestResult(
            scenario_id=scenario['scenario_id'],
            scenario=scenario,
            expected=expected,
            actual=actual,
            passed=passed
        )

    def run_all_tests(self) -> List[TestResult]:
        """
        Run all test scenarios and collect results.

        Returns:
            List of TestResult objects
        """
        print("\n" + "=" * 60)
        print("RUNNING AUTOMATED TESTS")
        print("=" * 60 + "\n")

        # Generate all scenarios from policy
        scenarios = self.policy.generate_all_scenarios()
        total = len(scenarios)

        print(f"Total scenarios to test: {total}")
        print("Running tests...\n")

        self.test_results = []

        for i, scenario in enumerate(scenarios, 1):
            result = self.test_scenario(scenario)
            self.test_results.append(result)

            # Progress indicator (every 10 tests)
            if i % 10 == 0 or i == total:
                passed = sum(1 for r in self.test_results if r.passed)
                print(f"   Progress: {i}/{total} tests completed ({passed} passed)")

        print("\n" + "=" * 60)
        print("TESTS COMPLETED")
        print("=" * 60 + "\n")

        return self.test_results

    def analyze_results(self) -> Dict:
        """
        Analyze test results and generate summary statistics.

        Returns:
            Dictionary with analysis metrics
        """
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed

        # Categorize failures
        over_permissive = []  # API allows when should deny
        over_restrictive = []  # API denies when should allow

        for result in self.test_results:
            if not result.passed:
                if result.expected == 'DENY' and result.actual == 'ALLOW':
                    over_permissive.append(result)
                elif result.expected == 'ALLOW' and result.actual == 'DENY':
                    over_restrictive.append(result)

        # Group failures by audience
        failures_by_audience = {}
        for result in self.test_results:
            if not result.passed:
                audience = result.scenario['audience']
                if audience not in failures_by_audience:
                    failures_by_audience[audience] = []
                failures_by_audience[audience].append(result)

        # Group failures by action
        failures_by_action = {}
        for result in self.test_results:
            if not result.passed:
                action = result.scenario['action']
                if action not in failures_by_action:
                    failures_by_action[action] = []
                failures_by_action[action].append(result)

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'over_permissive': over_permissive,
            'over_restrictive': over_restrictive,
            'failures_by_audience': failures_by_audience,
            'failures_by_action': failures_by_action
        }

    def print_summary(self):
        """Print a formatted summary of test results"""
        analysis = self.analyze_results()

        print("=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Scenarios: {analysis['total']}")
        print(f"PASSED: {analysis['passed']} ({analysis['pass_rate']:.1f}%)")
        print(f"FAILED: {analysis['failed']} ({100 - analysis['pass_rate']:.1f}%)")
        print("=" * 60)

        if analysis['failed'] > 0:
            print("\nFAILURE ANALYSIS")
            print("-" * 60)

            # Over-permissive failures (HIGH SEVERITY)
            if analysis['over_permissive']:
                print(f"\nOVER-PERMISSIVE (HIGH SEVERITY): {len(analysis['over_permissive'])} cases")
                print("   API allows actions that should be DENIED\n")
                for result in analysis['over_permissive']:
                    s = result.scenario
                    print(f"   Scenario {s['scenario_id']}: {s['audience']} can {s['action']} "
                          f"{s['visibility']} file")
                    print(f"      Expected: DENY | Actual: ALLOW")

            # Over-restrictive failures (MEDIUM SEVERITY)
            if analysis['over_restrictive']:
                print(f"\nOVER-RESTRICTIVE (MEDIUM SEVERITY): {len(analysis['over_restrictive'])} cases")
                print("   API denies actions that should be ALLOWED\n")
                for result in analysis['over_restrictive']:
                    s = result.scenario
                    print(f"   Scenario {s['scenario_id']}: {s['audience']} cannot {s['action']} "
                          f"{s['visibility']} file")
                    print(f"      Expected: ALLOW | Actual: DENY")

            # Breakdown by audience
            print("\nFAILURES BY AUDIENCE:")
            for audience, failures in analysis['failures_by_audience'].items():
                print(f"   {audience:12} - {len(failures)} failures")

            # Breakdown by action
            print("\nFAILURES BY ACTION:")
            for action, failures in analysis['failures_by_action'].items():
                print(f"   {action:12} - {len(failures)} failures")

        else:
            print("\nALL TESTS PASSED! No authorization bugs found.")

        print("\n" + "=" * 60 + "\n")

    def export_results(self, filename: str = 'test_results.json'):
        """Export detailed test results to JSON"""
        results_data = []

        for result in self.test_results:
            results_data.append({
                'scenario_id': result.scenario_id,
                'audience': result.scenario['audience'],
                'visibility': result.scenario['visibility'],
                'action': result.scenario['action'],
                'expected': result.expected,
                'actual': result.actual,
                'passed': result.passed,
                'timestamp': result.timestamp.isoformat()
            })

        with open(filename, 'w') as f:
            json.dump({
                'summary': self.analyze_results(),
                'results': results_data
            }, f, indent=2, default=str)

        print(f"Detailed results exported to {filename}")

    def get_failed_scenarios(self) -> List[TestResult]:
        """Get only the failed test results"""
        return [r for r in self.test_results if not r.passed]


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AUTHORIZATION TESTING FRAMEWORK")
    print("Systematic Testing of Access Control Enforcement")
    print("=" * 60 + "\n")

    # Initialize framework
    framework = AuthorizationTestFramework()

    # Setup test environment
    framework.setup_test_fixtures()

    # Run all tests
    results = framework.run_all_tests()

    # Print summary
    framework.print_summary()

    # Export results
    framework.export_results()

    # Show some specific failed scenarios for demonstration
    failed = framework.get_failed_scenarios()
    if failed:
        print("\n" + "=" * 60)
        print("SAMPLE FAILED SCENARIOS (First 5)")
        print("=" * 60)
        for i, result in enumerate(failed[:5], 1):
            s = result.scenario
            print(f"\n{i}. Scenario {s['scenario_id']}:")
            print(f"   Audience: {s['audience']}")
            print(f"   File Visibility: {s['visibility']}")
            print(f"   Action: {s['action']}")
            print(f"   Expected: {result.expected}")
            print(f"   Actual: {result.actual}")
            print(f"   Status: {'PASS' if result.passed else 'FAIL'}")

    print("\nTesting complete! Check test_results.json for detailed output.\n")