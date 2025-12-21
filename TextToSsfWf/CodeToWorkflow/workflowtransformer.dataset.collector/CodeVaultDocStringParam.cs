using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public class CodeVaultDocStringParam
    {
        [JsonPropertyName("returns")]
        public List<CodeVaultDocStringParamDetail> Returns { get; set; } = new List<CodeVaultDocStringParamDetail>();

        [JsonPropertyName("params")]
        public List<CodeVaultDocStringParamDetail> Params { get; set; } = new List<CodeVaultDocStringParamDetail>();

    }
}
