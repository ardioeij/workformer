using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector.generative.source
{
    public class LocalSourceFolderOption
    {

        public string FolderName { get; set; }

        public string FilePattern { get; set; } = "*.*";

        public SearchOption SearchOption { get; set; } = SearchOption.AllDirectories;

        public string[] SubFolders { get; set; } 

        public string OutputFile { get; set; }

        public EnumerationOptions EnumerationOptions { get; set; } = new EnumerationOptions
        {
            AttributesToSkip = FileAttributes.Hidden | FileAttributes.Compressed | FileAttributes.Encrypted | FileAttributes.Device | FileAttributes.IntegrityStream | FileAttributes.Offline | FileAttributes.ReparsePoint | FileAttributes.SparseFile | FileAttributes.System | FileAttributes.Temporary,
            IgnoreInaccessible = true,
            MatchCasing = MatchCasing.CaseInsensitive,
            RecurseSubdirectories = true,
            ReturnSpecialDirectories = false,
            MaxRecursionDepth = 16,
            MatchType = MatchType.Simple,
            BufferSize = 0,
        };

    }
}
