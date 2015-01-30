#!/usr/bin/python

import sketchToDroidRes

import mock
import unittest
import subprocess
import sys


def mock_stdout():
    sys.stdout = mock.Mock()


def mock_stdout_reset():
    sys.stdout = sys.__stdout__


class test_check_sketchtoolTest(unittest.TestCase):

    @mock.patch('sketchToDroidRes.subprocess.check_output')
    def test_check_sketchtool_present(self, mock_check_output):
        sketchToDroidRes.check_sketchtool()
        mock_check_output.assert_called_once_with(
            "sketchtool --version", shell=True)

    @mock.patch('sketchToDroidRes.sys.exit')
    @mock.patch('sketchToDroidRes.subprocess.check_output')
    def test_check_sketchtool_not_present(self, mock_check_output,
                                          mock_sys_exit):
        try:
            mock_stdout()
            mock_check_output.side_effect = subprocess.CalledProcessError(
                "", "")
            sketchToDroidRes.check_sketchtool()
        finally:
            mock_stdout_reset()
        mock_sys_exit.assert_called_once_with(2)


class test_is_sketch_file(unittest.TestCase):

    @mock.patch('sketchToDroidRes.isfile')
    def test_is_sketch_file_valid(self, mock_isfile):
        mock_isfile.return_value = True
        result = sketchToDroidRes.is_sketch_file("/hello/test.sketch")
        self.assertTrue(result)

    @mock.patch('sketchToDroidRes.isfile')
    def test_is_sketch_file_not_a_file(self, mock_isfile):
        mock_isfile.return_value = False
        result = sketchToDroidRes.is_sketch_file("/hello/test.sketch")
        self.assertFalse(result)

    @mock.patch('sketchToDroidRes.isfile')
    def test_is_sketch_file_not_dot_sketch(self, mock_isfile):
        mock_isfile.return_value = True
        result = sketchToDroidRes.is_sketch_file("/hello/test.hello")
        self.assertFalse(result)

    @mock.patch('sketchToDroidRes.isfile')
    def test_is_sketch_file_no_extension(self, mock_isfile):
        mock_isfile.return_value = True
        result = sketchToDroidRes.is_sketch_file("/hello/test")
        self.assertFalse(result)


class test_get_artboards(unittest.TestCase):

    @mock.patch('sketchToDroidRes.subprocess.check_output')
    def test_single_page_multiple_artboards(self, mock_check_output):
        mock_check_output.return_value = """
{
  "pages" : [
    {
      "name" : "Page 1",
      "artboards" : [{"name" : "test1"}, {"name" : "test2"}]
    }
  ]
}"""
        result = sketchToDroidRes.get_artboards("/test/fake_file")
        mock_check_output.assert_called_once_with(
            "sketchtool list artboards \"/test/fake_file\"", shell=True)
        self.assertEqual(["test1", "test2"], result)

    @mock.patch('sketchToDroidRes.subprocess.check_output')
    def test_multiple_pages_multiple_artboards(self, mock_check_output):
        mock_check_output.return_value = """
{
  "pages" : [
    {
      "name" : "Page 1",
      "artboards" : [{"name" : "test1"}, {"name" : "test2"}]
    },
    {
      "name" : "Page 2",
      "artboards": [{"name" : "test3"}]
    }
  ]
}"""
        result = sketchToDroidRes.get_artboards("/test/fake_file")
        mock_check_output.assert_called_once_with(
            "sketchtool list artboards \"/test/fake_file\"", shell=True)
        self.assertEqual(["test1", "test2", "test3"], result)

    @mock.patch('sketchToDroidRes.subprocess.check_output')
    def test_no_artboard(self, mock_check_output):
        mock_check_output.return_value = """
{
  "pages" : [
    {
      "name" : "Page 1",
      "artboards" : []
    }
  ]
}"""
        result = sketchToDroidRes.get_artboards("fake_file")
        mock_check_output.assert_called_once_with(
            "sketchtool list artboards \"fake_file\"", shell=True)
        self.assertEqual([], result)


class test_strip_sketch_scale_suffix(unittest.TestCase):

    @mock.patch('sketchToDroidRes.os.rename')
    def test_rename_at_x_files(self, mock_os_rename):
        sketchToDroidRes.strip_sketch_scale_suffix("/meDir/", "ic_test@3x.png")
        mock_os_rename.assert_called_once_with(
            "/meDir/ic_test@3x.png", "/meDir/ic_test.png")

    @mock.patch('sketchToDroidRes.os.rename')
    def test_rename_complex_at_x_files(self, mock_os_rename):
        sketchToDroidRes.strip_sketch_scale_suffix("/meDir/", "ic_test@3.1x.png")
        mock_os_rename.assert_called_once_with(
            "/meDir/ic_test@3.1x.png", "/meDir/ic_test.png")

    @mock.patch('sketchToDroidRes.os.rename')
    def test_dont_rename_not_matching_files(self, mock_os_rename):
        sketchToDroidRes.strip_sketch_scale_suffix("/meDir/", "ic_test.png")
        self.assertFalse(mock_os_rename.called)


if __name__ == '__main__':
    unittest.main()
