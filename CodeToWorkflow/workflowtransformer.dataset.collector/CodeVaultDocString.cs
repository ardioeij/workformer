using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public class CodeVaultDocString
    {
        [JsonPropertyName("docstring")]
        public string DocString { get; set; } = "";


    }
}
