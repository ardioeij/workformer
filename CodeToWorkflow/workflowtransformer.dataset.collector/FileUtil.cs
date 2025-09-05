using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Runtime.InteropServices;

namespace workflowtransformer.dataset.collector
{
    public struct FileUtil
    {
        public static string FixPath(string path, bool createIfNotExist = true)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "";
            }

            if (createIfNotExist)
            {
                FileInfo fi = new FileInfo(path);
                if (!fi.Directory.Exists)
                {
                    fi.Directory.Create();
                }
            }

            return path;
        }

        public static void DirectoryCopy(string sourceDirName, string destDirName, bool copySubDirs, bool overwrite = true)
        {
            // Get the subdirectories for the specified directory.
            DirectoryInfo dir = new DirectoryInfo(sourceDirName);

            if (!dir.Exists)
            {
                throw new DirectoryNotFoundException(
                    "Source directory does not exist or could not be found: "
                    + sourceDirName);
            }

            DirectoryInfo[] dirs = dir.GetDirectories();
            // If the destination directory doesn't exist, create it.
            if (!Directory.Exists(destDirName))
            {
                Directory.CreateDirectory(destDirName);
            }

            // Get the files in the directory and copy them to the new location.
            FileInfo[] files = dir.GetFiles();
            foreach (FileInfo file in files)
            {
                string temppath = Path.Combine(destDirName, file.Name);
                file.CopyTo(temppath, overwrite);
            }

            // If copying subdirectories, copy them and their contents to new location.
            if (copySubDirs)
            {
                foreach (DirectoryInfo subdir in dirs)
                {
                    string temppath = Path.Combine(destDirName, subdir.Name);
                    DirectoryCopy(subdir.FullName, temppath, copySubDirs, overwrite);
                }
            }
        }

    }
}
