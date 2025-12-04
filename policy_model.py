"""
policy_model.py
Ground truth authorization policy for file-sharing system.
This defines the EXPECTED behavior for all scenarios.
"""


class AuthorizationPolicy:
    """
    Formal policy model for file-sharing authorization.
    This serves as the ground truth for testing.
    """

    def __init__(self):
        self.rules = self._define_rules()

    def evaluate(self, audience, visibility, action, is_owner=False,
                 has_collaboration_permission=False, same_org=False):
        """
        Evaluate authorization decision based on policy rules.

        Args:
            audience: 'owner', 'collaborator', 'org_member', 'external'
            visibility: 'private', 'shared', 'org_public', 'public'
            action: 'read', 'edit', 'delete', 'share'
            is_owner: Boolean indicating if user is the file owner
            has_collaboration_permission: Boolean for explicit sharing
            same_org: Boolean indicating same organization

        Returns:
            'ALLOW' or 'DENY'
        """

        # RULE 1: Owner has full access (highest priority)
        if is_owner or audience == 'owner':
            return 'ALLOW'

        # RULE 2: Public files - read-only access for everyone
        if visibility == 'public':
            if action == 'read':
                return 'ALLOW'
            else:
                return 'DENY'

        # RULE 3: Organization-public files - read-only for org members
        if visibility == 'org_public':
            if same_org and action == 'read':
                return 'ALLOW'
            else:
                return 'DENY'

        # RULE 4: Explicit collaboration permissions
        if has_collaboration_permission:
            if action in ['read', 'edit']:
                return 'ALLOW'
            else:  # delete, share not allowed for collaborators
                return 'DENY'

        # RULE 5: Shared files - only explicit collaborators
        if visibility == 'shared':
            return 'DENY'  # Already handled by RULE 4

        # RULE 6: Private files - owner and collaborators only
        if visibility == 'private':
            return 'DENY'  # Already handled by RULE 1 and RULE 4

        # RULE 7: Default deny
        return 'DENY'

    def _define_rules(self):
        """Return human-readable rule descriptions"""
        return [
            {
                "id": 1,
                "description": "Owner has full access to their files",
                "condition": "audience == 'owner'",
                "result": "ALLOW all actions",
                "priority": "HIGHEST"
            },
            {
                "id": 2,
                "description": "Public files are read-only for everyone",
                "condition": "visibility == 'public' AND action == 'read'",
                "result": "ALLOW",
                "priority": "HIGH"
            },
            {
                "id": 3,
                "description": "Org-public files are read-only for org members",
                "condition": "visibility == 'org_public' AND same_org AND action == 'read'",
                "result": "ALLOW",
                "priority": "HIGH"
            },
            {
                "id": 4,
                "description": "Collaborators can read and edit",
                "condition": "has_collaboration_permission AND action IN ['read', 'edit']",
                "result": "ALLOW",
                "priority": "MEDIUM"
            },
            {
                "id": 5,
                "description": "Collaborators cannot delete or share",
                "condition": "has_collaboration_permission AND action IN ['delete', 'share']",
                "result": "DENY",
                "priority": "MEDIUM"
            },
            {
                "id": 6,
                "description": "Private/shared files deny all other access",
                "condition": "visibility IN ['private', 'shared'] AND no explicit permission",
                "result": "DENY",
                "priority": "LOW"
            },
            {
                "id": 7,
                "description": "Default deny all",
                "condition": "default",
                "result": "DENY",
                "priority": "LOWEST"
            }
        ]

    def get_rules_description(self):
        """Return formatted rules for display"""
        return self.rules

    def generate_all_scenarios(self):
        """
        Generate all possible test scenarios.
        Returns list of dictionaries with scenario details and expected results.
        """
        scenarios = []

        audiences = ['owner', 'collaborator', 'org_member', 'external']
        visibilities = ['private', 'shared', 'org_public', 'public']
        actions = ['read', 'edit', 'delete', 'share']

        scenario_id = 1
        for audience in audiences:
            for visibility in visibilities:
                for action in actions:
                    # Determine context flags based on audience
                    is_owner = (audience == 'owner')
                    has_collab = (audience == 'collaborator')
                    same_org = (audience in ['owner', 'org_member'])

                    # Get expected result from policy
                    expected = self.evaluate(
                        audience=audience,
                        visibility=visibility,
                        action=action,
                        is_owner=is_owner,
                        has_collaboration_permission=has_collab,
                        same_org=same_org
                    )

                    scenarios.append({
                        'scenario_id': scenario_id,
                        'audience': audience,
                        'visibility': visibility,
                        'action': action,
                        'is_owner': is_owner,
                        'has_collaboration': has_collab,
                        'same_org': same_org,
                        'expected_result': expected
                    })
                    scenario_id += 1

        return scenarios

    def export_to_csv(self, filename='policy_scenarios.csv'):
        """Export all scenarios to CSV for reference"""
        import csv
        scenarios = self.generate_all_scenarios()

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=scenarios[0].keys())
            writer.writeheader()
            writer.writerows(scenarios)

        print(f"Exported {len(scenarios)} scenarios to {filename}")
        return scenarios

    def print_statistics(self):
        """Print summary statistics about the policy"""
        scenarios = self.generate_all_scenarios()
        total = len(scenarios)
        allow_count = sum(1 for s in scenarios if s['expected_result'] == 'ALLOW')
        deny_count = total - allow_count

        print("\n" + "=" * 60)
        print("AUTHORIZATION POLICY STATISTICS")
        print("=" * 60)
        print(f"Total test scenarios: {total}")
        print(f"Expected ALLOW: {allow_count} ({allow_count / total * 100:.1f}%)")
        print(f"Expected DENY: {deny_count} ({deny_count / total * 100:.1f}%)")
        print("=" * 60 + "\n")

        # Breakdown by audience
        print("Breakdown by Audience:")
        for audience in ['owner', 'collaborator', 'org_member', 'external']:
            audience_scenarios = [s for s in scenarios if s['audience'] == audience]
            audience_allows = sum(1 for s in audience_scenarios if s['expected_result'] == 'ALLOW')
            print(f"  {audience:12} - ALLOW: {audience_allows:2}/16  DENY: {16 - audience_allows:2}/16")
        print()


# Test the policy model
if __name__ == "__main__":
    policy = AuthorizationPolicy()

    # Show statistics
    policy.print_statistics()

    # Test a few specific scenarios
    print("Sample Test Cases:")
    print("-" * 60)

    test_cases = [
        {
            'desc': 'Owner deleting their own private file',
            'audience': 'owner',
            'visibility': 'private',
            'action': 'delete',
            'is_owner': True,
            'has_collaboration': False,
            'same_org': True
        },
        {
            'desc': 'External user reading public file',
            'audience': 'external',
            'visibility': 'public',
            'action': 'read',
            'is_owner': False,
            'has_collaboration': False,
            'same_org': False
        },
        {
            'desc': 'External user editing public file',
            'audience': 'external',
            'visibility': 'public',
            'action': 'edit',
            'is_owner': False,
            'has_collaboration': False,
            'same_org': False
        },
        {
            'desc': 'Collaborator deleting shared file',
            'audience': 'collaborator',
            'visibility': 'shared',
            'action': 'delete',
            'is_owner': False,
            'has_collaboration': True,
            'same_org': False
        },
        {
            'desc': 'Org member reading org-public file',
            'audience': 'org_member',
            'visibility': 'org_public',
            'action': 'read',
            'is_owner': False,
            'has_collaboration': False,
            'same_org': True
        }
    ]

    for i, test in enumerate(test_cases, 1):
        result = policy.evaluate(
            audience=test['audience'],
            visibility=test['visibility'],
            action=test['action'],
            is_owner=test['is_owner'],
            has_collaboration_permission=test['has_collaboration'],
            same_org=test['same_org']
        )
        status = "ALLOW" if result == "ALLOW" else "DENY"
        print(f"{i}. {test['desc']}")
        print(f"   Result: {status} {result}\n")

    # Export to CSV
    policy.export_to_csv()