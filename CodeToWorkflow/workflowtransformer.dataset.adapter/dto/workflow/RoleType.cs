using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto.workflow
{
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum RoleType
    {
        Visitor,
        Member,
        Staff,
        Supervisor,
        Manager,
        Director,
        Administrator
    }
}
