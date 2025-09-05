using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public class CodeVault
    {
        [JsonPropertyName("code")]
        public string Code { get; set; } = "";

        [JsonPropertyName("docstring")]
        public string DocString { get; set; } = "";

        [JsonPropertyName("short_docstring")]
        public string ShortDocString { get; set; } = "";

        [JsonPropertyName("docstring_params")]
        public CodeVaultDocStringParam DocStringParams { get; set; } = new CodeVaultDocStringParam();

        [JsonPropertyName("return_type")]
        public string ReturnType { get; set; } = "";

        [JsonPropertyName("comment")]
        public string[] Comments { get; set; } = new string[] { };


    }
}
