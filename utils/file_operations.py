import os
import sys

import requests
from typing import Dict, Optional, Tuple
from utils.common.cli_utils import print_json


def handle_file_operations(args):
    """Handle file operations."""
    if args.command == "list":
        result = FileOperations.list_files(args.project_code, args.path)
        print_json(result)
    elif args.command == "read":
        result = FileOperations.read_file(args.project_code, args.file_path)
        print(result.get("content", ""))
    elif args.command == "write":
        # Read content from stdin or file
        content = ""
        if args.content:
            content = args.content
        elif args.file:
            with open(args.file, "r") as f:
                content = f.read()
        elif not sys.stdin.isatty():
            content = sys.stdin.read()

        result = FileOperations.write_file(args.project_code, args.file_path, content)
        print_json(result)
    else:
        print(f"Unknown command: {args.command}")

class FileOperations:
    """Utilities for managing local project files."""
    
    @staticmethod
    def local_models_root() -> str:
        """Get the base directory for local model projects."""
        if not os.path.exists("./local-model-projects"):
            os.makedirs("./local-model-projects")
        return os.path.abspath("./local-model-projects")
    
    @staticmethod
    def local_sources_root() -> str:
        """Get the base directory for local source projects."""
        if not os.path.exists("./local-source-databases"):
            os.makedirs("./local-source-databases")
        return os.path.abspath("./local-source-databases")

    @staticmethod
    def local_semantic_root() -> str:
        """Get the base directory for local semantic projects."""
        if not os.path.exists("./local-semantic-projects"):
            os.makedirs("./local-semantic-projects")
        return os.path.abspath("./local-semantic-projects")
    
    @staticmethod
    def list_files(project_code: str, directory_path: Optional[str] = None) -> Dict:
        """List files in the local project directory.
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            directory_path: Optional subdirectory within the project
            
        Returns:
            dict: Dictionary with files and directories information or error
        """
        base_path = os.path.join(FileOperations.local_models_root(), project_code)
        
        if not os.path.exists(base_path):
            return {"error": f"Project directory not found: {base_path}"}
        
        target_path = base_path
        if directory_path:
            target_path = os.path.join(base_path, directory_path)
            if not os.path.exists(target_path):
                return {"error": f"Directory not found: {directory_path}"}
        
        try:
            files = []
            directories = []
            
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                relative_path = os.path.relpath(item_path, base_path)
                
                if os.path.isdir(item_path):
                    if item != ".git":  # Skip .git directory by default
                        directories.append({
                            "name": item,
                            "path": relative_path,
                            "type": "directory"
                        })
                else:
                    files.append({
                        "name": item,
                        "path": relative_path,
                        "type": "file",
                        "size": os.path.getsize(item_path)
                    })
            
            return {
                "project_code": project_code,
                "path": directory_path or ".",
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
    
    @staticmethod
    def read_file(project_code: str, file_path: str) -> Dict:
        """Read a file from the local project directory.
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            file_path: Path to the file within the project
            
        Returns:
            dict: Dictionary with file content and metadata or error
        """
        base_path = os.path.join(FileOperations.local_models_root(), project_code)
        
        if not os.path.exists(base_path):
            return {"error": f"Project directory not found: {base_path}"}
        
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            return {"error": f"File not found: {file_path}"}
        
        if not os.path.isfile(full_path):
            return {"error": f"Not a file: {file_path}"}
        
        try:
            with open(full_path, 'r') as file:
                content = file.read()
                
            return {
                "project_code": project_code,
                "file_path": file_path,
                "content": content,
                "size": os.path.getsize(full_path)
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    @staticmethod
    def write_file(project_code: str, file_path: str, content: str) -> Dict:
        """Write content to a file in the local project directory.
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            file_path: Path to the file within the project
            content: Content to write to the file
            
        Returns:
            dict: Dictionary with operation status or error
        """
        base_path = os.path.join(FileOperations.local_models_root(), project_code)
        
        if not os.path.exists(base_path):
            return {"error": f"Project directory not found: {base_path}"}
        
        full_path = os.path.join(base_path, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w') as file:
                file.write(content)
                
            return {
                "project_code": project_code,
                "file_path": file_path,
                "status": "success",
                "message": f"File {file_path} written successfully"
            }
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    @staticmethod
    def delete_file(project_code: str, file_path: str) -> Dict:
        """Delete a file from the local project directory.
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            file_path: Path to the file within the project
            
        Returns:
            dict: Dictionary with operation status or error
        """
        base_path = os.path.join(FileOperations.local_models_root(), project_code)
        
        if not os.path.exists(base_path):
            return {"error": f"Project directory not found: {base_path}"}
        
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            return {"error": f"File not found: {file_path}"}
        
        if not os.path.isfile(full_path):
            return {"error": f"Not a file: {file_path}"}
        
        try:
            os.remove(full_path)
            return {
                "project_code": project_code,
                "file_path": file_path,
                "status": "success",
                "message": f"File {file_path} deleted successfully"
            }
        except Exception as e:
            return {"error": f"Failed to delete file: {str(e)}"}
            
    @staticmethod
    def count_files_and_dirs_recursively(directory_path: str) -> Tuple[int, int]:
        """Count all files and directories recursively in a directory, excluding hidden items.
        
        Excludes files and directories that start with '.' (like .DS_Store, .git, .vscode, etc.)
        
        Args:
            directory_path: Path to the directory to count
            
        Returns:
            tuple: (file_count, directory_count) - counts exclude hidden files/dirs
        """
        total_files = 0
        total_dirs = 0
        
        for root, dirs, files in os.walk(directory_path):
            # Filter out hidden directories and prevent os.walk from recursing into them
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Filter out hidden files
            visible_files = [f for f in files if not f.startswith('.')]
            
            total_files += len(visible_files)
            total_dirs += len(dirs)  # dirs is already filtered above
            
        return total_files, total_dirs

    @staticmethod
    def download_dbt_project(project_code: str, server_url: str, access_token: str) -> Dict:
        """Download and extract a dbt project from the server with intelligent timestamp-based sync.
        
        This function compares modification times between server files and local files:
        - Creates new files that don't exist locally
        - Updates existing files only if server version is newer
        - Skips files where local version is newer or same age
        - Deletes local SQL files that no longer exist on server and are older than 1 day
        - Preserves local-only files that aren't in the server archive
        - Excludes hidden files (starting with .) from tracking and statistics
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            server_url: The MCP server URL
            access_token: The access token for authentication
            
        Returns:
            dict: Dictionary with operation status, detailed sync statistics, or error
                - files_created: Number of new files created
                - files_created_list: List of file paths that were created
                - files_updated: Number of files updated (server newer than local)
                - files_updated_list: List of file paths that were updated
                - files_skipped: Number of files skipped (local newer or same)
                - files_deleted: Number of SQL files deleted (no longer on server, older than 1 day)
                - files_deleted_list: List of file paths that were deleted
                - total_file_count: Total files in project after sync
                - local_only_files_count: Files that exist only locally (excluding hidden files)
        """
        import shutil
        import tempfile
        import tarfile
        import time
        
        base_dir = FileOperations.local_models_root()
        project_dir = os.path.join(base_dir, project_code)
        archive_path = os.path.join(base_dir, f"{project_code}.tar.gz")
        
        # Ensure the base directory exists
        os.makedirs(base_dir, exist_ok=True)
        
        # Remove any existing archive file
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        try:
            # Get existing files and their modification times for comparison
            # Skip hidden files (starting with .) as they're typically system files
            existing_files = {}  # rel_path -> modification_time
            if os.path.exists(project_dir):
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        # Skip hidden files (starting with .)
                        if file.startswith('.'):
                            continue
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_dir)
                        # Also skip if any part of the relative path contains hidden directories
                        if any(part.startswith('.') for part in rel_path.split(os.sep)):
                            continue
                        try:
                            existing_files[rel_path] = os.path.getmtime(file_path)
                        except OSError:
                            # If we can't get mtime, treat as if file doesn't exist
                            pass
            
            # Download the project archive
            headers = {
                "Accept": "application/x-gzip",
                "Authorization": f"Bearer {access_token}"
            }
            
            download_url = f"{server_url}/mcp/projects/{project_code}/download"
            
            with requests.get(download_url, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    return {"error": f"Failed to download project: HTTP {response.status_code}"}
                
                with open(archive_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Create project directory after successful download
            os.makedirs(project_dir, exist_ok=True)
            
            # Keep track of files from the downloaded project and statistics
            downloaded_files = set()
            files_created = 0
            files_updated = 0
            files_skipped = 0
            files_created_list = []
            files_updated_list = []
            
            # Create a temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the archive to the temporary directory, preserving timestamps
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(path=temp_dir)
                
                # Walk through the temp directory and intelligently copy files based on timestamps
                for root, dirs, files in os.walk(temp_dir):
                    # Get the relative path from the temp directory
                    rel_path = os.path.relpath(root, temp_dir)
                    
                    # Create corresponding directories in the project directory
                    if rel_path != '.':
                        os.makedirs(os.path.join(project_dir, rel_path), exist_ok=True)
                    
                    # Process each file with timestamp comparison
                    for file in files:
                        temp_file_path = os.path.join(root, file)
                        
                        # Calculate destination path and relative file path
                        if rel_path == '.':
                            dest_path = os.path.join(project_dir, file)
                            rel_file_path = file
                        else:
                            dest_path = os.path.join(project_dir, rel_path, file)
                            rel_file_path = os.path.join(rel_path, file).replace('\\', '/')
                        
                        # Add to downloaded files set
                        downloaded_files.add(rel_file_path)
                        
                        # Skip configuration files from update counting (but still copy them if needed)
                        base_config_files = {'dbt_project.yml', 'packages.yml', 'profiles.yml'}
                        is_base_config_file = file in base_config_files
                        
                        # Get server file modification time
                        try:
                            server_mtime = os.path.getmtime(temp_file_path)
                        except OSError:
                            server_mtime = None
                        
                        # Compare timestamps and decide whether to update
                        if rel_file_path in existing_files:
                            # File exists locally, compare timestamps
                            local_mtime = existing_files[rel_file_path]
                            
                            if server_mtime and server_mtime > local_mtime:
                                # Server file is newer, update it
                                shutil.copy2(temp_file_path, dest_path)
                                if not is_base_config_file:  # Don't count base config files in updates
                                    files_updated += 1
                                    files_updated_list.append(rel_file_path)
                            else:
                                # Local file is newer or same age, skip update
                                if not is_base_config_file:  # Don't count base config files in skipped
                                    files_skipped += 1
                        else:
                            # File doesn't exist locally, create it
                            shutil.copy2(temp_file_path, dest_path)
                            if not is_base_config_file:  # Don't count base config files in created
                                files_created += 1
                                files_created_list.append(rel_file_path)
            
            # Calculate files that exist locally but weren't in the download
            # (Hidden files are already excluded from existing_files)
            local_only_files = set(existing_files.keys()) - downloaded_files
            
            # Handle deleted files from server - remove local SQL files that are:
            # 1. No longer on the server (in local_only_files)
            # 2. Are SQL files (end with .sql)
            # 3. Have local modification time older than 1 day
            files_deleted = 0
            files_deleted_list = []
            # one_day_ago = time.time() - (24 * 60 * 60)  # 1 day in seconds
            one_day_ago = time.time() - (1)  # 1 day in seconds
            
            for local_file in list(local_only_files):
                if local_file.endswith('.sql'):
                    local_file_path = os.path.join(project_dir, local_file)
                    if os.path.exists(local_file_path):
                        try:
                            local_mtime = existing_files[local_file]
                            if local_mtime < one_day_ago:
                                # Delete the local SQL file that's no longer on server and older than 1 day
                                os.remove(local_file_path)
                                files_deleted += 1
                                files_deleted_list.append(local_file)
                                # Remove from local_only_files since we've deleted it
                                local_only_files.discard(local_file)
                        except (OSError, KeyError) as e:
                            print(f"Warning: Could not delete {local_file}: {e}")
            
            # Recalculate local_only_count after deletions
            local_only_count = len(local_only_files)
            if local_only_count > 0:
                print(f"Local only files: {local_only_files}")
            
            # Clean up the archive file
            os.remove(archive_path)
            
            # Get a recursive count of all files and directories
            file_count, dir_count = FileOperations.count_files_and_dirs_recursively(project_dir)
            

            download_response = {
                "project_code": project_code,
                "status": "success",
                "message": f"Project {project_code} downloaded with timestamp-based sync",
                "files_created": files_created,
                "files_created_list": files_created_list,
                "files_updated": files_updated,
                "files_updated_list": files_updated_list,
                "files_skipped": files_skipped,
                "files_deleted": files_deleted,
                "files_deleted_list": files_deleted_list,
                "files_base_config": len(base_config_files),
                "total_file_count": file_count,
                "directory_count": dir_count,
                "local_only_files_count": local_only_count,
                "sync_summary": f"Created: {files_created}, Updated: {files_updated}, Skipped: {files_skipped}, Deleted: {files_deleted}"
            }
            if local_only_count == 0:
                download_response.pop("local_only_files_count")
            if files_created == 0:
                download_response.pop("files_created_list")
            if files_updated == 0:
                download_response.pop("files_updated_list")
            if files_deleted == 0:
                download_response.pop("files_deleted_list")

            return download_response
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error during download: {str(e)}"}
        except tarfile.TarError as e:
            return {"error": f"Failed to extract archive: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to download project: {str(e)}"}
    
    @staticmethod
    def download_semantic_project(project_code: str, server_url: str, access_token: str) -> Dict:
        """Download a semantic project archive from the server (without extraction).
        
        Args:
            project_code: The project code (e.g., 'dbt_project_1')
            server_url: The MCP server URL
            access_token: The access token for authentication
        
        This version only downloads the .tar.gz file for inspection purposes.
        """
        base_dir = FileOperations.local_semantic_root()
        archive_path = os.path.join(base_dir, f"{project_code}_semantic.tar.gz")
        
        # Ensure the base directory exists
        os.makedirs(base_dir, exist_ok=True)
        
        # Remove any existing archive file
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        try:
            # Download the semantic project archive using the /download/semantic endpoint
            headers = {
                "Accept": "application/x-gzip",
                "Authorization": f"Bearer {access_token}"
            }
            
            download_url = f"{server_url}/mcp/projects/{project_code}/download/semantic"
            print(f"Downloading from: {download_url}")
            
            with requests.get(download_url, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    return {"error": f"Failed to download semantic project: HTTP {response.status_code}"}
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")
                
                with open(archive_path, 'wb') as f:
                    total_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        total_size += len(chunk)

            # Get file size
            file_size = os.path.getsize(archive_path)

            return {
                "project_code": project_code,
                "status": "success",
                "message": f"Semantic project {project_code} archive downloaded successfully",
                "archive_path": archive_path,
                "file_size": file_size,
                "download_type": "semantic",
                "note": "Archive downloaded but not extracted. You can inspect the contents manually."
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error during semantic download: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to download semantic project: {str(e)}"}
