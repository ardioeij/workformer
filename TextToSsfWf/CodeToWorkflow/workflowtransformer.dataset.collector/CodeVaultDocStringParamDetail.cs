using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public class CodeVaultDocStringParamDetail
    {
        [JsonPropertyName("identifier")]
        public string Identifier { get; set; } = "";

        [JsonPropertyName("type")]
        public string Type { get; set; } = "";

        [JsonPropertyName("docstring")]
        public string DocString { get; set; } = "";

    }
}
