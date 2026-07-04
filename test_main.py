import os
import unittest
import tempfile
import shutil
from unittest.mock import patch
import io

# Import the functions under test
from main import list_files, navigate_to_folder, go_up_directory, view_item, rename_file, create_item, delete_item, find_item, find_duplicates, find_duplicate_files


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

    @patch("builtins.input", side_effect=["file1.txt", "1"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_view_item_file(self, mock_stdout, mock_input):
        view_item(self.test_dir)
        output = mock_stdout.getvalue()
        self.assertIn("test content", output)

    @patch("builtins.input", side_effect=["folder_a", "1"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_view_item_dir(self, mock_stdout, mock_input):
        view_item(self.test_dir)
        output = mock_stdout.getvalue()
        self.assertIn("Contents of Directory: folder_a", output)


    @patch("builtins.input", side_effect=["file1.txt", "new_name.txt", "y"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_rename_file_success(self, mock_stdout, mock_input):
        rename_file(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "new_name.txt")))
        self.assertFalse(os.path.exists(self.file1))

    @patch("builtins.input", side_effect=["file1.txt", "new_name.txt", "n"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_rename_file_cancel(self, mock_stdout, mock_input):
        rename_file(self.test_dir)
        self.assertTrue(os.path.exists(self.file1))
        self.assertIn("Renaming cancelled.", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["file1.txt", "1", "n"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_find_item_success(self, mock_stdout, mock_input):
        find_item(self.test_dir)
        self.assertIn("Found 1 item(s) matching 'file1.txt':", mock_stdout.getvalue())
        self.assertIn("file1.txt", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["new_file.txt", "f"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_file(self, mock_stdout, mock_input):
        create_item(self.test_dir)
        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, "new_file.txt")))

    @patch("builtins.input", side_effect=["new_dir", "d"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_dir(self, mock_stdout, mock_input):
        create_item(self.test_dir)
        self.assertTrue(os.path.isdir(os.path.join(self.test_dir, "new_dir")))

    @patch("builtins.input", side_effect=["folder_a", "1", "yes"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_delete_item_folder(self, mock_stdout, mock_input):
        delete_item(self.test_dir)
        self.assertFalse(os.path.exists(self.sub_dir1))

    def test_find_duplicates_logic(self):
        dup_dir = tempfile.mkdtemp(dir=self.test_dir)
        
        # Create duplicate content files
        with open(os.path.join(dup_dir, "file1.txt"), "w") as f: f.write("contentA")
        with open(os.path.join(dup_dir, "file2.txt"), "w") as f: f.write("contentA")
        
        with open(os.path.join(dup_dir, "file3.jpg"), "w") as f: f.write("contentB")
        with open(os.path.join(dup_dir, "file4.jpg"), "w") as f: f.write("contentB")
        with open(os.path.join(dup_dir, "file5.jpg"), "w") as f: f.write("contentB")
        
        # Unique file
        with open(os.path.join(dup_dir, "unique.txt"), "w") as f: f.write("contentC")
        
        duplicates = find_duplicates(dup_dir)
        
        # Should find 2 groups (contentA, contentB)
        self.assertEqual(len(duplicates), 2)
        
        # Verify contentA duplicates
        for h, files in duplicates.items():
            if len(files) == 2:
                self.assertEqual(set(files), {"file1.txt", "file2.txt"})
            elif len(files) == 3:
                self.assertEqual(set(files), {"file3.jpg", "file4.jpg", "file5.jpg"})
            else:
                self.fail(f"Unexpected duplicate group size: {len(files)}")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_find_duplicate_files_output(self, mock_stdout):
        # Use a new directory
        dup_dir = tempfile.mkdtemp(dir=self.test_dir)
        with open(os.path.join(dup_dir, "dup1.txt"), "w") as f: f.write("dup")
        with open(os.path.join(dup_dir, "dup2.txt"), "w") as f: f.write("dup")
        
        find_duplicate_files(dup_dir)
        output = mock_stdout.getvalue()
        self.assertIn("Duplicate Files Found:", output)
        self.assertIn("Group 1 [MD5:", output)
        self.assertIn("- dup1.txt", output)
        self.assertIn("- dup2.txt", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_find_duplicate_files_none(self, mock_stdout):
        empty_dir = tempfile.mkdtemp(dir=self.test_dir)
        find_duplicate_files(empty_dir)
        output = mock_stdout.getvalue()
        self.assertIn("No duplicate files found in this directory.", output)



if __name__ == "__main__" :
    unittest.main()
