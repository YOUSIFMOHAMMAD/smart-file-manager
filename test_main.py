import os
import unittest
import tempfile
import shutil
from unittest.mock import patch
import io

# Import the functions under test
from main import list_files, navigate_to_folder, go_up_directory, view_file, rename_file, delete_file, get_categorized_files, categorize_files, find_duplicates, find_duplicate_files


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

    @patch("builtins.input", return_value="file1.txt")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_view_file_success(self, mock_stdout, mock_input):
        view_file(self.test_dir)
        output = mock_stdout.getvalue()
        self.assertIn("test content", output)

    @patch("builtins.input", return_value="non_existent.txt")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_view_file_failure(self, mock_stdout, mock_input):
        view_file(self.test_dir)
        output = mock_stdout.getvalue()
        self.assertIn("[Error]", output)

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

    @patch("builtins.input", side_effect=["file1.txt", "yes"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_delete_file_success(self, mock_stdout, mock_input):
        delete_file(self.test_dir)
        self.assertFalse(os.path.exists(self.file1))
        self.assertIn("Deleted successfully.", mock_stdout.getvalue())

    @patch("builtins.input", side_effect=["file1.txt", "no"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_delete_file_cancel(self, mock_stdout, mock_input):
        delete_file(self.test_dir)
        self.assertTrue(os.path.exists(self.file1))
        self.assertIn("Deletion cancelled.", mock_stdout.getvalue())

    def test_get_categorized_files_success(self):
        # Create a special directory structure to verify categorization
        cat_dir = tempfile.mkdtemp(dir=self.test_dir)
        
        # Documents/Text
        open(os.path.join(cat_dir, "doc1.pdf"), "w").close()
        open(os.path.join(cat_dir, "doc2.TXT"), "w").close()  # check case-insensitivity
        open(os.path.join(cat_dir, "doc3.doc"), "w").close()
        open(os.path.join(cat_dir, "doc4.docx"), "w").close()
        
        # Scripts/Code
        open(os.path.join(cat_dir, "script1.py"), "w").close()
        open(os.path.join(cat_dir, "script2.js"), "w").close()
        open(os.path.join(cat_dir, "script3.sh"), "w").close()
        open(os.path.join(cat_dir, "script4.c"), "w").close()
        open(os.path.join(cat_dir, "script5.java"), "w").close()
        
        # Images
        open(os.path.join(cat_dir, "img1.png"), "w").close()
        open(os.path.join(cat_dir, "img2.JPG"), "w").close()  # check case-insensitivity
        open(os.path.join(cat_dir, "img3.gif"), "w").close()
        open(os.path.join(cat_dir, "img4.bmp"), "w").close()

        # Videos
        open(os.path.join(cat_dir, "vid1.mp4"), "w").close()
        open(os.path.join(cat_dir, "vid2.MKV"), "w").close()
        open(os.path.join(cat_dir, "vid3.avi"), "w").close()
        
        # Other
        open(os.path.join(cat_dir, "archive.zip"), "w").close()
        open(os.path.join(cat_dir, "config.ini"), "w").close()
        open(os.path.join(cat_dir, "no_ext_file"), "w").close()
        
        # Directories
        os.mkdir(os.path.join(cat_dir, "sub_folder_x"))
        os.mkdir(os.path.join(cat_dir, "sub_folder_y"))
        
        categories = get_categorized_files(cat_dir)
        
        # Verify correctness and sorting (sorting is case-insensitive, but we can check actual sorted output)
        self.assertEqual(sorted(categories["Documents/Text"], key=str.lower), categories["Documents/Text"])
        self.assertEqual(sorted(categories["Scripts/Code"], key=str.lower), categories["Scripts/Code"])
        self.assertEqual(sorted(categories["Images"], key=str.lower), categories["Images"])
        self.assertEqual(sorted(categories["Videos"], key=str.lower), categories["Videos"])
        self.assertEqual(sorted(categories["Directories"], key=str.lower), categories["Directories"])
        self.assertEqual(sorted(categories["Other"], key=str.lower), categories["Other"])
        
        # Verify elements are in the expected list
        self.assertEqual(set(categories["Documents/Text"]), {"doc1.pdf", "doc2.TXT", "doc3.doc", "doc4.docx"})
        self.assertEqual(set(categories["Scripts/Code"]), {"script1.py", "script2.js", "script3.sh", "script4.c", "script5.java"})
        self.assertEqual(set(categories["Images"]), {"img1.png", "img2.JPG", "img3.gif", "img4.bmp"})
        self.assertEqual(set(categories["Videos"]), {"vid1.mp4", "vid2.MKV", "vid3.avi"})
        self.assertEqual(set(categories["Directories"]), {"sub_folder_x", "sub_folder_y"})
        self.assertEqual(set(categories["Other"]), {"archive.zip", "config.ini", "no_ext_file"})

    def test_get_categorized_files_empty(self):
        empty_dir = tempfile.mkdtemp(dir=self.test_dir)
        categories = get_categorized_files(empty_dir)
        for cat in categories:
            self.assertEqual(categories[cat], [])

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_categorize_files_success(self, mock_stdout):
        # We can run on self.test_dir (which has folder_a, folder_b, and file1.txt)
        categorize_files(self.test_dir)
        output = mock_stdout.getvalue()
        
        # Should contain headings
        self.assertIn("[Documents/Text]", output)
        self.assertIn("[Scripts/Code]", output)
        self.assertIn("[Images]", output)
        self.assertIn("[Videos]", output)
        self.assertIn("[Directories]", output)
        self.assertIn("[Other]", output)
        
        # Should show folder_a, folder_b, and file1.txt under their respective headings
        self.assertIn("- folder_a", output)
        self.assertIn("- folder_b", output)
        self.assertIn("- file1.txt", output)
        self.assertIn("(No items)", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_categorize_files_non_existent(self, mock_stdout):
        non_existent_dir = os.path.join(self.test_dir, "does_not_exist")
        categorize_files(non_existent_dir)
        output = mock_stdout.getvalue()
        self.assertIn("[Error]", output)

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
