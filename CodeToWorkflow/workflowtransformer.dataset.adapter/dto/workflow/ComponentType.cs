using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto.workflow
{
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum ComponentType
    {

        //[EnumMember(Value = "WF")]
        WF,
        //Workflow
        //[EnumMember(Value = "PROC")]
        PROC,
        //Process
        //[EnumMember(Value = "IF")]
        IF,
        //Decision
        //[EnumMember(Value = "ELSE")]
        ELSE,
        //DecisionBranch
        //[EnumMember(Value = "FOR")]
        LOOP,
        //ForEach
        //While,
        //UserInput
        //GoTo
    }


    /*public enum ProcessType
    {
        Function,

        Sql,
        SqlQuery,
        SqlFind,
        SqlSave,
        SqlDelete,

        Email,
        Notification,

        Http,
        HttpHash,
        HttpJwt,

        Export,
        Import,
        Transform,

        Assembly,
        Get,
        Set,
    }*/

}
