import os
import unittest
import tempfile
import shutil
from unittest.mock import patch
import io

# Import the functions under test
from main import list_files, navigate_to_folder, go_up_directory


class TestSmartFileManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        self.sub_dir1 = os.path.join(self.test_dir, "folder_a")
        self.sub_dir2 = os.path.join(self.test_dir, "folder_b")
        os.mkdir(self.sub_dir1)
        os.mkdir(self.sub_dir2)
        
        # Create dummy files
        self.file1 = os.path.join(self.test_dir, "file1.txt")
        self.file2 = os.path.join(self.sub_dir1, "file2.log")
        with open(self.file1, "w") as f:
            f.write("test content")
        with open(self.file2, "w") as f:
            f.write("nested test content")

    def tearDown(self):
        # Clean up temporary directories and files
        shutil.rmtree(self.test_dir)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_files_success(self, mock_stdout):
        list_files(self.test_dir)
        output = mock_stdout.getvalue()
        
        # Verify headers
        self.assertIn("Name", output)
        self.assertIn("Type", output)
        
        # Verify items and types
        self.assertIn("folder_a", output)
        self.assertIn("[Folder]", output)
        self.assertIn("folder_b", output)
        self.assertIn("file1.txt", output)
        self.assertIn("[File]", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_files_empty(self, mock_stdout):
        list_files(self.sub_dir2)
        output = mock_stdout.getvalue()
        self.assertIn("The directory is empty.", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_files_non_existent(self, mock_stdout):
        non_existent_dir = os.path.join(self.test_dir, "does_not_exist")
        list_files(non_existent_dir)
        output = mock_stdout.getvalue()
        self.assertIn("[Error]", output)

    @patch("builtins.input", return_value="folder_a")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_navigate_to_folder_success(self, mock_stdout, mock_input):
        new_dir = navigate_to_folder(self.test_dir)
        self.assertEqual(new_dir, self.sub_dir1)
        self.assertIn("Successfully navigated to", mock_stdout.getvalue())

    @patch("builtins.input", return_value="")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_navigate_to_folder_empty(self, mock_stdout, mock_input):
        new_dir = navigate_to_folder(self.test_dir)
        self.assertEqual(new_dir, self.test_dir)
        self.assertIn("[Error] Folder name cannot be empty.", mock_stdout.getvalue())

    @patch("builtins.input", return_value="non_existent_folder")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_navigate_to_folder_not_exist(self, mock_stdout, mock_input):
        new_dir = navigate_to_folder(self.test_dir)
        self.assertEqual(new_dir, self.test_dir)
        self.assertIn("[Error] The path 'non_existent_folder' does not exist.", mock_stdout.getvalue())

    @patch("builtins.input", return_value="file1.txt")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_navigate_to_folder_not_a_dir(self, mock_stdout, mock_input):
        new_dir = navigate_to_folder(self.test_dir)
        self.assertEqual(new_dir, self.test_dir)
        self.assertIn("[Error] 'file1.txt' is not a directory.", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_go_up_directory_success(self, mock_stdout):
        parent = go_up_directory(self.sub_dir1)
        # Using realpath/abspath to normalize path comparison
        self.assertEqual(os.path.abspath(parent), os.path.abspath(self.test_dir))
        self.assertIn("Moved up to", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_go_up_directory_root(self, mock_stdout):
        # We can't easily go past '/' on linux or 'C:\' on Windows, but let's test at actual root
        root = os.path.abspath("/")
        parent = go_up_directory(root)
        self.assertEqual(parent, root)
        self.assertIn("Already at the root directory.", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
