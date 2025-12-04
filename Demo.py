"""
simple_demo.py
Simple, clear demonstration of authorization testing.
Perfect for class presentations - easy to explain and understand!
"""

from policy_model import AuthorizationPolicy
from api_client import ApiClient


def print_header(text):
    """Print a nice header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text):
    """Print a section divider"""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print('─' * 70 + "\n")


def simple_demo():
    """
    Simple demonstration of the authorization testing framework.
    Tests 5 carefully chosen scenarios that clearly show how it works.
    """

    print_header("AUTHORIZATION TESTING DEMO")

    print("This demo will:")
    print("  1. Set up a file-sharing environment")
    print("  2. Test 5 authorization scenarios")
    print("  3. Show you which ones pass and which ones fail (bugs!)")
    print()
    input("Press Enter to start...")

    # ============================================================
    # STEP 1: Setup
    # ============================================================

    print_section("STEP 1: Setting Up Test Environment")

    policy = AuthorizationPolicy()
    # Use HTTP client to call the Flask server. Ensure the server is running at this base URL.
    api = ApiClient(base_url='http://localhost:5000')

    # Create users
    print("Creating users...")
    owner = api.create_user("alice@acme.com", "acme-corp", "Alice")
    collaborator = api.create_user("bob@acme.com", "acme-corp", "Bob")
    external = api.create_user("dave@external.com", "external-org", "Dave")

    owner_id = owner.data['user_id']
    collab_id = collaborator.data['user_id']
    external_id = external.data['user_id']

    print("  Alice (Owner) - owns all files")
    print("  Bob (Collaborator) - has permission on some files")
    print("  Dave (External) - from different organization")

    # Create files
    print("\nCreating files...")
    private_file = api.create_file(owner_id, "secret.txt", "private", "Top secret")
    public_file = api.create_file(owner_id, "announcement.txt", "public", "Public news")

    private_id = private_file.data['file_id']
    public_id = public_file.data['file_id']

    print("  secret.txt (PRIVATE) - only Alice can access")
    print("  announcement.txt (PUBLIC) - everyone can read")

    # Give Bob permission on private file
    print("\nGranting permissions...")
    api.share_file(private_id, owner_id, collab_id, 'edit')
    print("  Bob can now READ and EDIT secret.txt")

    print("\nEnvironment ready!")
    input("\nPress Enter to start testing scenarios...")

    # ============================================================
    # STEP 2: Test Scenarios
    # ============================================================

    print_header("STEP 2: Testing Authorization Scenarios")

    test_scenarios = [
        {
            'num': 1,
            'desc': "Alice (Owner) deletes her own private file",
            'user': 'Alice',
            'user_id': owner_id,
            'file': 'secret.txt (PRIVATE)',
            'file_id': private_id,
            'action': 'delete',
            'audience': 'owner',
            'visibility': 'private',
            'is_owner': True,
            'has_collab': False,
            'same_org': True
        },
        {
            'num': 2,
            'desc': "Bob (Collaborator) reads the private file he has access to",
            'user': 'Bob',
            'user_id': collab_id,
            'file': 'secret.txt (PRIVATE)',
            'file_id': private_id,
            'action': 'read',
            'audience': 'collaborator',
            'visibility': 'private',
            'is_owner': False,
            'has_collab': True,
            'same_org': True
        },
        {
            'num': 3,
            'desc': "Bob (Collaborator) tries to share the private file",
            'user': 'Bob',
            'user_id': collab_id,
            'file': 'secret.txt (PRIVATE)',
            'file_id': private_id,
            'action': 'share',
            'audience': 'collaborator',
            'visibility': 'private',
            'is_owner': False,
            'has_collab': True,
            'same_org': True
        },
        {
            'num': 4,
            'desc': "Dave (External) reads the public file",
            'user': 'Dave',
            'user_id': external_id,
            'file': 'announcement.txt (PUBLIC)',
            'file_id': public_id,
            'action': 'read',
            'audience': 'external',
            'visibility': 'public',
            'is_owner': False,
            'has_collab': False,
            'same_org': False
        },
        {
            'num': 5,
            'desc': "Dave (External) tries to edit the public file",
            'user': 'Dave',
            'user_id': external_id,
            'file': 'announcement.txt (PUBLIC)',
            'file_id': public_id,
            'action': 'edit',
            'audience': 'external',
            'visibility': 'public',
            'is_owner': False,
            'has_collab': False,
            'same_org': False
        }
    ]

    results = []

    for scenario in test_scenarios:
        print(f"\n{'━' * 70}")
        print(f"TEST {scenario['num']}/5: {scenario['desc']}")
        print('━' * 70)

        print(f"\n  User: {scenario['user']}")
        print(f"  File: {scenario['file']}")
        print(f"  Action: {scenario['action'].upper()}")

        # Get expected result from policy
        expected = policy.evaluate(
            audience=scenario['audience'],
            visibility=scenario['visibility'],
            action=scenario['action'],
            is_owner=scenario['is_owner'],
            has_collaboration_permission=scenario['has_collab'],
            same_org=scenario['same_org']
        )

        print(f"\n  Policy says: {expected}")

        # Get actual result from API
        if scenario['action'] == 'read':
            response = api.get_file(scenario['file_id'], scenario['user_id'])
        elif scenario['action'] == 'edit':
            response = api.update_file(scenario['file_id'], scenario['user_id'], "New content")
        elif scenario['action'] == 'delete':
            # Use non-destructive authorization check instead of deleting the file
            allowed = api.check_authorization(scenario['file_id'], scenario['user_id'], 'delete')
            response = type('obj', (object,), {'status_code': 200 if allowed else 403})
        elif scenario['action'] == 'share':
            response = api.share_file(scenario['file_id'], scenario['user_id'], external_id, 'read')

        actual = 'ALLOW' if response.status_code in [200, 201] else 'DENY'
        print(f"  API says: {actual}")

        # Compare
        if expected == actual:
            print(f"\n  TEST PASSED - Policy and API agree!")
            results.append('PASS')
        else:
            print(f"\n  BUG FOUND - Policy and API disagree!")
            print(f"     Expected: {expected}, but API returned: {actual}")
            if expected == 'DENY' and actual == 'ALLOW':
                print(f"     SEVERITY: HIGH - Security vulnerability (over-permissive)")
            results.append('FAIL')

        input("\n  [Press Enter for next test...]")

    # ============================================================
    # STEP 3: Summary
    # ============================================================

    print_header("STEP 3: Summary")

    passed = results.count('PASS')
    failed = results.count('FAIL')

    print(f"Results from {len(results)} tests:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed > 0:
        print(f"\nFound {failed} authorization bug(s)!")
        print("\nThese bugs show that:")
        print("  • The API is not correctly enforcing the authorization policy")
        print("  • Manual testing would have likely missed these issues")
        print("  • Automated, systematic testing is essential for security")
    else:
        print("\nAll tests passed! No bugs found.")

    print("\n" + "=" * 70)
    print("  In the full framework, we test ALL 64 possible scenarios")
    print("  and create visualizations to show patterns in the bugs.")
    print("=" * 70 + "\n")

    print("Thank you!")


if __name__ == "__main__":
    simple_demo()