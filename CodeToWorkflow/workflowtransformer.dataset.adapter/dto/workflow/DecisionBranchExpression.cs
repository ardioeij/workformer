using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto.workflow
{
    public class DecisionBranchExpression
    {
        [JsonPropertyName("Lt")]
        public string Left { get; set; } = "";

        [JsonPropertyName("Op")]
        public string Operator { get; set; } = "";

        [JsonPropertyName("Rt")]
        public string Right { get; set; } = "";

        [JsonPropertyName("Conj")]
        public string Conjunction { get; set; } = ""; // AND / OR

    }
}
