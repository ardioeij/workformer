using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;

namespace workflowtransformer.dataset.adapter.generative
{
    public interface ISource
    {
        string CreateSourceCodeDataset();

    }
}
