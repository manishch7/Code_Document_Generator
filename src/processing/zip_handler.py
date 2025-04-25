import os
import tempfile
import zipfile
import shutil
from typing import List, Dict, Set, Tuple

# File extensions to process
ALLOWED_EXTENSIONS = {'.py'}

# File extensions to explicitly ignore
IGNORED_EXTENSIONS = {
    # Video files
    '.mp4', '.avi', '.mov', '.flv', '.mkv', '.webm', '.m4v',
    # Image files
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
    # Audio files
    '.mp3', '.wav', '.aac', '.flac', '.ogg',
    # Document files (keep .txt for requirements.txt, etc.)
    '.doc', '.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xlsx',
    # Archive files
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # Other binary files
    '.exe', '.dll', '.bin', '.dat'
}

def process_zip_file(zip_file_path: str, extract_dir: str = None) -> Tuple[str, Dict]:
    """
    Extract a zip file to a temporary directory and return the path and file statistics.
    
    Args:
        zip_file_path: Path to the zip file
        extract_dir: Optional directory to extract to (if None, creates a temp dir)
        
    Returns:
        Tuple of (extract_dir_path, file_stats_dict)
    """
    # Create temp directory if not provided
    if extract_dir is None:
        extract_dir = tempfile.mkdtemp()
    
    file_stats = {
        'total_files': 0,
        'python_files': 0,
        'other_files': 0,
        'directories': 0,
        'extracted_files': [],
        'all_files': []
    }
    
    try:
        # First attempt: extract only Python files
        _extract_python_files(zip_file_path, extract_dir, file_stats)
        
        # If no Python files were found, try a more aggressive approach
        if file_stats['python_files'] == 0 and file_stats['total_files'] > 0:
            _extract_non_binary_files(zip_file_path, extract_dir, file_stats)
    
    except Exception as e:
        file_stats['error'] = str(e)
    
    return extract_dir, file_stats

def _extract_python_files(zip_file_path: str, extract_dir: str, file_stats: Dict):
    """Extract Python files from the zip and update file statistics."""
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # First, get stats about the ZIP content
        for file_info in zip_ref.infolist():
            file_stats['all_files'].append(file_info.filename)
            
            if file_info.filename.endswith('/'):
                file_stats['directories'] += 1
                continue
            
            file_stats['total_files'] += 1
            _, ext = os.path.splitext(file_info.filename.lower())
            
            if ext == '.py':
                file_stats['python_files'] += 1
            else:
                file_stats['other_files'] += 1
        
        # Now extract all Python files
        for file_info in zip_ref.infolist():
            # Skip directories
            if file_info.filename.endswith('/'):
                continue
            
            # Get file extension
            _, ext = os.path.splitext(file_info.filename.lower())
            
            # Extract Python files and other allowed files like .txt
            if ext in ALLOWED_EXTENSIONS or (ext not in IGNORED_EXTENSIONS and ext != ''):
                zip_ref.extract(file_info, extract_dir)
                file_stats['extracted_files'].append(file_info.filename)

def _extract_non_binary_files(zip_file_path: str, extract_dir: str, file_stats: Dict):
    """Extract all non-binary files from the zip as a fallback."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                # Skip directories
                if file_info.filename.endswith('/'):
                    continue
                
                # Get file extension
                _, ext = os.path.splitext(file_info.filename.lower())
                
                # Extract everything except explicitly ignored extensions
                if ext not in IGNORED_EXTENSIONS:
                    zip_ref.extract(file_info, extract_dir)
                    if file_info.filename not in file_stats['extracted_files']:
                        file_stats['extracted_files'].append(file_info.filename)
            
            # Check if any Python files are in the extracted directory
            extracted_python_files = []
            for root, _, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, extract_dir)
                        extracted_python_files.append(rel_path)
            
            file_stats['extracted_python_files'] = extracted_python_files
            file_stats['python_files_found_after_extraction'] = len(extracted_python_files)
    
    except Exception as e:
        file_stats['fallback_error'] = str(e)

def list_all_files_in_directory(directory: str) -> List[str]:
    """
    List all files (recursively) in a directory for debugging.
    
    Args:
        directory: Path to the directory
        
    Returns:
        List of file paths
    """
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, directory)
            files.append(rel_path)
    return files
