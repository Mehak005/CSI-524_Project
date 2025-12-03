"""
file_sharing_api.py
Mock file-sharing API with REST-like interface.
This simulates a real file-sharing backend with authorization logic.

NOTE: This implementation contains INTENTIONAL bugs for demonstration purposes!
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid


class User:
    """Represents a user in the system"""
    def __init__(self, user_id: str, email: str, organization_id: str, name: str):
        self.user_id = user_id
        self.email = email
        self.organization_id = organization_id
        self.name = name
        self.created_at = datetime.now()

    def __repr__(self):
        return f"User(id={self.user_id}, email={self.email}, org={self.organization_id})"


class File:
    """Represents a file in the system"""
    def __init__(self, file_id: str, owner_id: str, name: str,
                 visibility: str, content: str = ""):
        self.file_id = file_id
        self.owner_id = owner_id
        self.name = name
        self.visibility = visibility  # private, shared, org_public, public
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"File(id={self.file_id}, owner={self.owner_id}, visibility={self.visibility})"


class Permission:
    """Represents explicit sharing permissions"""
    def __init__(self, file_id: str, user_id: str, permission_type: str):
        self.file_id = file_id
        self.user_id = user_id
        self.permission_type = permission_type  # read, edit
        self.granted_at = datetime.now()

    def __repr__(self):
        return f"Permission(file={self.file_id}, user={self.user_id}, type={self.permission_type})"


class APIResponse:
    """Standardized API response"""
    def __init__(self, status_code: int, message: str, data: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"APIResponse(status={self.status_code}, message='{self.message}')"

    def to_dict(self):
        return {
            'status_code': self.status_code,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class FileShareAPI:
    """
    Mock file-sharing API with authorization enforcement.

    This simulates a RESTful API for file sharing with access control.
    Contains intentional authorization bugs for testing purposes.
    """

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.files: Dict[str, File] = {}
        self.permissions: Dict[Tuple[str, str], Permission] = {}  # (file_id, user_id) -> Permission
        self.organizations: Dict[str, List[str]] = {}  # org_id -> list of user_ids

        print("🚀 FileShareAPI initialized")

    # ==================== USER MANAGEMENT ====================

    def create_user(self, email: str, organization_id: str, name: str) -> APIResponse:
        """Create a new user (POST /users)"""
        user_id = str(uuid.uuid4())
        user = User(user_id, email, organization_id, name)
        self.users[user_id] = user

        # Add to organization
        if organization_id not in self.organizations:
            self.organizations[organization_id] = []
        self.organizations[organization_id].append(user_id)

        return APIResponse(
            status_code=201,
            message="User created successfully",
            data={'user_id': user_id, 'email': email}
        )

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    # ==================== FILE MANAGEMENT ====================

    def create_file(self, owner_id: str, name: str, visibility: str,
                    content: str = "") -> APIResponse:
        """Create a new file (POST /files)"""
        if owner_id not in self.users:
            return APIResponse(404, "User not found")

        if visibility not in ['private', 'shared', 'org_public', 'public']:
            return APIResponse(400, "Invalid visibility level")

        file_id = str(uuid.uuid4())
        file = File(file_id, owner_id, name, visibility, content)
        self.files[file_id] = file

        return APIResponse(
            status_code=201,
            message="File created successfully",
            data={'file_id': file_id, 'name': name, 'visibility': visibility}
        )

    def get_file(self, file_id: str, user_id: str) -> APIResponse:
        """
        Read a file (GET /files/:id)
        Requires authorization check
        """
        if file_id not in self.files:
            return APIResponse(404, "File not found")

        file = self.files[file_id]

        # Authorization check
        if not self._check_authorization(file_id, user_id, 'read'):
            return APIResponse(403, "Access denied")

        return APIResponse(
            status_code=200,
            message="File retrieved successfully",
            data={
                'file_id': file.file_id,
                'name': file.name,
                'owner_id': file.owner_id,
                'visibility': file.visibility,
                'content': file.content,
                'created_at': file.created_at.isoformat()
            }
        )

    def update_file(self, file_id: str, user_id: str, content: str) -> APIResponse:
        """
        Update file content (PUT /files/:id)
        Requires authorization check
        """
        if file_id not in self.files:
            return APIResponse(404, "File not found")

        file = self.files[file_id]

        # Authorization check
        if not self._check_authorization(file_id, user_id, 'edit'):
            return APIResponse(403, "Access denied")

        file.content = content
        file.updated_at = datetime.now()

        return APIResponse(
            status_code=200,
            message="File updated successfully",
            data={'file_id': file_id, 'updated_at': file.updated_at.isoformat()}
        )

    def delete_file(self, file_id: str, user_id: str) -> APIResponse:
        """
        Delete a file (DELETE /files/:id)
        Requires authorization check
        """
        if file_id not in self.files:
            return APIResponse(404, "File not found")

        # Authorization check
        if not self._check_authorization(file_id, user_id, 'delete'):
            return APIResponse(403, "Access denied")

        # Delete file and associated permissions
        del self.files[file_id]
        keys_to_delete = [k for k in self.permissions.keys() if k[0] == file_id]
        for key in keys_to_delete:
            del self.permissions[key]

        return APIResponse(
            status_code=200,
            message="File deleted successfully",
            data={'file_id': file_id}
        )

    # ==================== SHARING ====================

    def share_file(self, file_id: str, user_id: str, target_user_id: str,
                   permission_type: str = 'read') -> APIResponse:
        """
        Share a file with another user (POST /files/:id/share)
        Requires authorization check
        """
        if file_id not in self.files:
            return APIResponse(404, "File not found")

        if target_user_id not in self.users:
            return APIResponse(404, "Target user not found")

        # Authorization check - can the user share this file?
        if not self._check_authorization(file_id, user_id, 'share'):
            return APIResponse(403, "Access denied - cannot share this file")

        # Grant permission
        permission = Permission(file_id, target_user_id, permission_type)
        self.permissions[(file_id, target_user_id)] = permission

        return APIResponse(
            status_code=200,
            message="File shared successfully",
            data={
                'file_id': file_id,
                'shared_with': target_user_id,
                'permission': permission_type
            }
        )

    def get_file_permissions(self, file_id: str, user_id: str) -> APIResponse:
        """Get all permissions for a file (GET /files/:id/permissions)"""
        if file_id not in self.files:
            return APIResponse(404, "File not found")

        file = self.files[file_id]

        # Only owner can view permissions
        if file.owner_id != user_id:
            return APIResponse(403, "Access denied - only owner can view permissions")

        file_permissions = [
            {
                'user_id': perm.user_id,
                'permission_type': perm.permission_type,
                'granted_at': perm.granted_at.isoformat()
            }
            for (fid, uid), perm in self.permissions.items()
            if fid == file_id
        ]

        return APIResponse(
            status_code=200,
            message="Permissions retrieved",
            data={'permissions': file_permissions}
        )

    # ==================== AUTHORIZATION LOGIC ====================

    def _check_authorization(self, file_id: str, user_id: str, action: str) -> bool:
        """
        Core authorization logic.

        ⚠️ WARNING: This implementation contains INTENTIONAL BUGS for testing!

        Args:
            file_id: The file being accessed
            user_id: The user attempting access
            action: The action being attempted (read, edit, delete, share)

        Returns:
            True if authorized, False otherwise
        """
        if file_id not in self.files or user_id not in self.users:
            return False

        file = self.files[file_id]
        user = self.users[user_id]

        # Rule 1: Owner has full access
        if file.owner_id == user_id:
            return True

        # Rule 2: Public files
        if file.visibility == 'public':
            if action == 'read':
                return True
            # BUG #1: Public files allow editing! (Should only allow read)
            elif action == 'edit':
                return True  # 🐛 INTENTIONAL BUG
            else:
                return False

        # Rule 3: Organization-public files
        if file.visibility == 'org_public':
            # Check if user is in same organization
            owner = self.users[file.owner_id]
            same_org = (user.organization_id == owner.organization_id)

            if same_org and action == 'read':
                return True
            # BUG #2: Org members can delete org_public files! (Should only read)
            elif same_org and action == 'delete':
                return True  # 🐛 INTENTIONAL BUG
            else:
                return False

        # Rule 4: Check explicit permissions
        permission_key = (file_id, user_id)
        if permission_key in self.permissions:
            perm = self.permissions[permission_key]

            if action == 'read':
                return True  # All permissions include read
            elif action == 'edit':
                return perm.permission_type == 'edit' or perm.permission_type == 'read'
            # BUG #3: Collaborators can share files! (Should not be allowed)
            elif action == 'share':
                return True  # 🐛 INTENTIONAL BUG
            elif action == 'delete':
                return False  # Collaborators cannot delete

        # Rule 5: Shared and Private files - deny by default
        return False

    # ==================== UTILITY METHODS ====================

    def get_all_files(self) -> List[File]:
        """Get all files (for debugging)"""
        return list(self.files.values())

    def get_all_users(self) -> List[User]:
        """Get all users (for debugging)"""
        return list(self.users.values())

    def reset(self):
        """Reset the API state (useful for testing)"""
        self.users.clear()
        self.files.clear()
        self.permissions.clear()
        self.organizations.clear()
        print("🔄 API state reset")

    def print_state(self):
        """Print current API state (for debugging)"""
        print("\n" + "="*60)
        print("API STATE")
        print("="*60)
        print(f"Users: {len(self.users)}")
        for user in self.users.values():
            print(f"  - {user}")
        print(f"\nFiles: {len(self.files)}")
        for file in self.files.values():
            print(f"  - {file}")
        print(f"\nPermissions: {len(self.permissions)}")
        for perm in self.permissions.values():
            print(f"  - {perm}")
        print("="*60 + "\n")


# Demo/Testing
if __name__ == "__main__":
    api = FileShareAPI()

    # Create organizations
    org1 = "org-acme"
    org2 = "org-external"

    # Create users
    print("\n📋 Creating users...")
    owner_resp = api.create_user("owner@acme.com", org1, "Alice Owner")
    collab_resp = api.create_user("collaborator@acme.com", org1, "Bob Collaborator")
    org_resp = api.create_user("orgmember@acme.com", org1, "Charlie OrgMember")
    ext_resp = api.create_user("external@other.com", org2, "Dave External")

    owner_id = owner_resp.data['user_id']
    collab_id = collab_resp.data['user_id']
    org_id = org_resp.data['user_id']
    ext_id = ext_resp.data['user_id']

    print(f"✅ Created 4 users")

    # Create files with different visibility
    print("\n📁 Creating files...")
    private_file = api.create_file(owner_id, "private.txt", "private", "Secret content")
    public_file = api.create_file(owner_id, "public.txt", "public", "Public content")
    org_file = api.create_file(owner_id, "org.txt", "org_public", "Org content")
    shared_file = api.create_file(owner_id, "shared.txt", "shared", "Shared content")

    private_fid = private_file.data['file_id']
    public_fid = public_file.data['file_id']
    org_fid = org_file.data['file_id']
    shared_fid = shared_file.data['file_id']

    print(f"✅ Created 4 files with different visibility levels")

    # Share a file with collaborator
    print("\n🤝 Sharing file...")
    api.share_file(shared_fid, owner_id, collab_id, 'edit')
    print(f"✅ Shared file with collaborator")

    # Test some scenarios
    print("\n🧪 Testing Authorization Scenarios:")
    print("-" * 60)

    test_scenarios = [
        ("Owner reading private file", owner_id, private_fid, 'read'),
        ("Collaborator reading shared file", collab_id, shared_fid, 'read'),
        ("Collaborator deleting shared file", collab_id, shared_fid, 'delete'),
        ("External reading public file", ext_id, public_fid, 'read'),
        ("External editing public file (BUG!)", ext_id, public_fid, 'edit'),
        ("Org member deleting org file (BUG!)", org_id, org_fid, 'delete'),
        ("Collaborator sharing file (BUG!)", collab_id, shared_fid, 'share'),
    ]

    for desc, uid, fid, action in test_scenarios:
        result = api._check_authorization(fid, uid, action)
        status = "✅ ALLOW" if result else "❌ DENY"
        bug_marker = " 🐛" if "BUG" in desc else ""
        print(f"{status} - {desc}{bug_marker}")

    # Show state
    api.print_state()