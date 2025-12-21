using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;
using workflowtransformer.dataset.adapter.dto.workflow;

namespace workflowtransformer.dataset.adapter.generative
{
    public interface IGrabber
    {
        List<string> SourceCodeToWorkflow(string[] sourceCodeLines, string workflowOutputFile = "dataset\\sourcecode_workflows.txt");

        List<UserStory> WorkflowToUserStory(string[] workflows, string userStoriesOutputFile = "dataset\\workflow_userstories.txt", string workflowsOutputFile = "dataset\\workflows.txt");

        List<UserStory> SourceCodeToUserStory(string[] sourceCodeLines, string userStoriesOutputFile = "dataset\\sourcecode_userstories.txt");

    }
}
