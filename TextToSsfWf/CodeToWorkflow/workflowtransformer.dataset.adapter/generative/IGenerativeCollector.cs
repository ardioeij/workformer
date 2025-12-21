using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.generative
{
    public interface IGenerativeCollector
    {
        void CreateSourceCodeDataset(string outputFile = "dataset\\sourcecode.txt");

        void SourceCodesToWorkflows(string inputFile = "dataset\\sourcecode.txt");

        void WorkflowsToUserStories(string inputFile = "dataset\\workflow.txt");

    }
}
