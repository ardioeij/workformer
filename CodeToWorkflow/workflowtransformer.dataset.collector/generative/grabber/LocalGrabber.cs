using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;
using workflowtransformer.dataset.adapter.dto.workflow;
using workflowtransformer.dataset.adapter.generative;

namespace workflowtransformer.dataset.collector.generative.grabber
{
    public class LocalGrabber : IGrabber
    {
        public List<UserStory> SourceCodeToUserStory(string[] sourceCodeLines, string userStoriesOutputFile = "dataset\\sourcecode_userstories.txt")
        {
            return new List<UserStory>();
        }

        public List<string> SourceCodeToWorkflow(string[] sourceCodeLines, string workflowOutputFile = "dataset\\workflow.txt")
        {
            return new List<string>();
        }

        public List<UserStory> WorkflowToUserStory(string[] workflows, string outputFile = "dataset\\userstory.txt", string workflowsOutputFile = "dataset\\workflows.txt")
        {
            return new List<UserStory>();
        }
    }
}
