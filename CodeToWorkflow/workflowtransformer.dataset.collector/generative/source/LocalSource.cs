using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using workflowtransformer.dataset.adapter.generative;
using workflowtransformer.dataset.adapter.dto;

namespace workflowtransformer.dataset.collector.generative.source
{
    public class LocalSource : ISource
    {
        public List<LocalSourceFolderOption> Folders { get; set; } = new List<LocalSourceFolderOption>
        {
        };

        public LocalSource()
        {
        }

        public string CreateSourceCodeDataset()
        {
            var sourceCodeDatasets = new StringBuilder();

            foreach (var folder in Folders)
            {

                var files = Directory.GetFiles(folder.FolderName, folder.FilePattern, folder.EnumerationOptions);
                foreach (var file in files)
                {
                    try
                    {
                        var fileContent = File.ReadAllText(file);

                        var functions = SourceCodeUtils.ExtractFunctions(fileContent);

                        foreach (var func in functions)
                        {
                            if (!string.IsNullOrWhiteSpace(func.Code) && func.Code != Environment.NewLine && func.Code != "\n" && func.Code != "\r" && func.Code != "\r\n" && func.Code != "\n\r")
                            {
                                sourceCodeDatasets.AppendLine(func.Code);
                            }
                        }
                    }
                    catch (Exception ex1)
                    {
                        continue;
                    }
                }

                if (!string.IsNullOrWhiteSpace(folder.OutputFile))
                {
                    var fileContent = sourceCodeDatasets.ToString();
                    File.WriteAllText(folder.OutputFile, fileContent);
                    sourceCodeDatasets = new StringBuilder();
                }
            }

            var content = sourceCodeDatasets.ToString();
            return content;
        }


    }
}
