using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto
{
    public class UserStory
    {
        public string Application { get; set; } = "";

        public string Feature { get; set; } = "";

        public string Function { get; set; } = "";

        public string Goal { get; set; } = "";

        public string Role { get; set; } = "";

        public string Description { get; set; } = "";

        [JsonPropertyName("AcceptanceCriteria")]
        public List<AcceptanceCriteria> AcceptanceCriterias { get; set; } = new List<AcceptanceCriteria>();

        [JsonIgnore]
        public int Index { get; set; }

    }

    public class AcceptanceCriteria
    {
        public string Given { get; set; } = "";
        public string When { get; set; } = "";
        public string Then { get; set; } = "";

        public string Description { get; set; } = "";
    }

}
