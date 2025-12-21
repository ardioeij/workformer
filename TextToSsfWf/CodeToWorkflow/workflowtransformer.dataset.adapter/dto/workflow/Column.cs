using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto.workflow
{
    public class Column
    {

        [JsonPropertyName("Prm")]
        public string Name { get; set; } = "";

        [JsonPropertyName("Type")]
        public string Type { get; set; } = "";

        //public string Key { get; set; } = "";

        //public string Value { get; set; } = "";

        [JsonPropertyName("List")]
        public List<Column> Columns { get; set; } //= new List<Column>();

    }
}
