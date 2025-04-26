import os

class PathManager:
    def __init__(self, base_directory=None):
        """
        Initialize the PathManager with a base directory.
        If no base directory is provided, use the current working directory.
        """
        self.base_directory = base_directory or os.getcwd()
        print(f"[DEBUG] Base directory set to: {self.base_directory}")

    def resolve_path(self, relative_path):
        """
        Resolve a relative path to an absolute path within the base directory.
        """
        absolute_path = os.path.abspath(os.path.join(self.base_directory, relative_path))
        print(f"[DEBUG] Resolved path: {absolute_path}")
        return absolute_path

    def ensure_directory_exists(self, file_path):
        """
        Ensure the directory for the given file path exists.
        """
        directory = os.path.dirname(file_path)
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"[DEBUG] Directory ensured: {directory}")
            except Exception as e:
                print(f"[ERROR] Failed to create directory: {directory}. Error: {e}")
                raise

    def ensure_file_exists(self, file_path):
        """
        Ensure the file exists by creating it if it doesn't.
        """
        self.ensure_directory_exists(file_path)  # Ensure the directory exists first
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as f:
                    pass  # Create an empty file
                print(f"[DEBUG] File ensured: {file_path}")
            except PermissionError as e:
                print(f"[ERROR] Permission denied: {file_path}. Error: {e}")
                raise
            except Exception as e:
                print(f"[ERROR] Failed to create file: {file_path}. Error: {e}")
                raise
