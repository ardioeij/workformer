using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;
using workflowtransformer.dataset.adapter.dto.workflow;
using workflowtransformer.dataset.adapter.generative;
using workflowtransformer.dataset.collector.generative.grabber;
using workflowtransformer.dataset.collector.generative.source;

namespace workflowtransformer.dataset.collector.generative
{
    public class GenerativeCollector : IGenerativeCollector
    {
        private volatile object _lock = new object();

        private List<ISource> Sources { get; set; } = new List<ISource>
        {
            new LocalSource{ },
            //new GithubSource{ },
        };

        private List<IGrabber> Grabbers { get; set; } = new List<IGrabber> 
        {
            //new ChatGptGrabber(),
            new LocalGrabber(),
        };

        public GenerativeCollector()
        {
        }

        public void CreateSourceCodeDataset(string outputFile = "dataset\\sourcecode.txt")
        {
            outputFile = FileUtil.FixPath(outputFile);

            var sb = new StringBuilder();

            foreach (var source in Sources)
            {
                var content = source.CreateSourceCodeDataset();
                if (!string.IsNullOrWhiteSpace(content)) 
                {
                    sb.AppendLine(content);
                }
            }

            var lines = sb.ToString().Split(Environment.NewLine).Where(x => !string.IsNullOrWhiteSpace(x));
            lock (_lock)
            {
                File.WriteAllLines(outputFile, lines);
            }
        }

        public void SourceCodesToWorkflows(string inputFile = "dataset\\sourcecode.txt")
        {
            var sourceCodeLines = File.ReadAllLines(FileUtil.FixPath(inputFile, false));
            var codeWorkflowsList = new List<string>();
            foreach (var grabber in Grabbers)
            {
                var codeWorkflows = grabber.SourceCodeToWorkflow(sourceCodeLines.Take(100).ToArray());
                codeWorkflowsList.AddRange(codeWorkflows);
            }
        }

        public void WorkflowsToUserStories(string inputFile = "dataset\\sourcecode_workflows.txt")
        {
            inputFile = FileUtil.FixPath(inputFile);

            var workflowLines = File.ReadAllLines(FileUtil.FixPath(inputFile, false));

            var userStoriesWorkflowList = new List<UserStory>();

            foreach (var grabber in Grabbers)
            {
                var userStoriesWorkflows = grabber.WorkflowToUserStory(workflowLines);
                userStoriesWorkflowList.AddRange(userStoriesWorkflows);
            }
        }

        public void SourceCodeToUserStories(string inputFile = "dataset\\sourcecode.txt")
        {
            inputFile = FileUtil.FixPath(inputFile);

            var sourceCodeLines = File.ReadAllLines(FileUtil.FixPath(inputFile, false));

            var userStoriesWorkflowList = new List<UserStory>();

            foreach (var grabber in Grabbers)
            {
                var userStoriesWorkflows = grabber.SourceCodeToUserStory(sourceCodeLines.Skip(250).Take(300).ToArray());
                userStoriesWorkflowList.AddRange(userStoriesWorkflows);
            }
        }

    }
}
