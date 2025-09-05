using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.adapter.dto.workflow
{
    public class Node
    {
        //[JsonIgnore]
        //public int Index { get; set; } = 0;

        [JsonIgnore]
        //[JsonPropertyName("Name")]
        public string Name { get; set; } = "";

        [JsonPropertyName("Desc")]
        //[JsonIgnore]
        public string Description { get; set; } = "";

        [JsonPropertyName("Token")]
        public string Token { get; set; } = "";

        ComponentType _componentType = ComponentType.PROC;
        [JsonPropertyName("Comp")]
        public ComponentType ComponentType 
        { 
            get
            {
                return _componentType;
            }
            set
            {
                _componentType = value;
                if (value == ComponentType.WF)
                {
                    Sequences = new List<Node>();
                    //Roles = new string[] { };
                }
                else if (value == ComponentType.PROC)
                {
                    //Sequences = null;
                    //Roles = null;
                    //InputTypes = null;
                    //OutputTypes = null;
                    //DecisionBranchExpressions = null;
                }
                else if (value == ComponentType.IF)
                {
                    Sequences = new List<Node>();
                    //Roles = null;
                    //InputTypes = null;
                    //OutputTypes = null;
                    //DecisionBranchExpressions = null;
                }
                else if (value == ComponentType.ELSE)
                {
                    Sequences = new List<Node>();
                    //Roles = null;
                    //InputTypes = null;
                    //OutputTypes = null;
                    DecisionBranchExpressions = new List<DecisionBranchExpression>();
                }

                else if (value == ComponentType.LOOP)
                {
                    Sequences = new List<Node>();
                    //Roles = null;
                    //InputTypes = null;
                    //OutputTypes = null;
                    //DecisionBranchExpressions = null;
                }
            }
        }

        List<Column> _inputTypes;
        [JsonPropertyName("In")]
        public List<Column> InputTypes 
        { 
            get
            {
                if (ComponentType == ComponentType.WF && _inputTypes == null)
                {
                    _inputTypes = new List<Column>();
                }
                return _inputTypes;
            }
            set
            {
                if (ComponentType == ComponentType.WF)
                {
                    _inputTypes = value;
                }
            }
        }

        List<Column> _outputTypes;
        [JsonPropertyName("Out")]
        public List<Column> OutputTypes
        {
            get
            {
                if (ComponentType == ComponentType.WF && _outputTypes == null)
                {
                    _outputTypes = new List<Column>();
                }
                return _outputTypes;
            }
            set
            {
                if (ComponentType == ComponentType.WF)
                {
                    _outputTypes = value;
                }
            }
        }

        //[JsonPropertyName("Out")]
        //public List<Column> OutputTypes { get; set; } = new List<Column>();

        //public List<Table> DatabaseTables { get; set; } = new List<Table>();

        //public string[] Actors { get; set; }

        //public RoleType[] Roles { get; set; } = new RoleType[] { RoleType.Administrator, RoleType.Director, RoleType.Manager, RoleType.Supervisor, RoleType.Staff, RoleType.Member, RoleType.Visitor };

        //public string[] Roles { get; set; }

        //public string[] Users { get; set; }

        //public string[] Workgroups { get; set; }

        //public string GoTo { get; set; }

        
        //List<Node> _sequences;
        [JsonPropertyName("Seq")]
        public List<Node> Sequences { get; set; }
        //public List<Node> Sequences
        //{
        //    get
        //    {
        //        if (_sequences == null)
        //        {
        //            _sequences = new List<Node>();
        //        }
        //        return _sequences;
        //    }
        //    set
        //    {
        //        _sequences = value;
        //    }
        //}

        //[JsonPropertyName("If")]
        //public List<Node> DecisionBranches { get; set; } //= new List<Node>();

        [JsonPropertyName("Exp")]
        public List<DecisionBranchExpression> DecisionBranchExpressions { get; set; } //= new List<DecisionBranchExpression>();


        /*public override string ToString()
        {
            var sb = new StringBuilder();

            sb.Append($"Comp:{ComponentType.ToString()} ");

            if (InputTypes != null && InputTypes.Count > 0)
            {
                var inputs = string.Join(",", InputTypes.Select(x => $"{x.Type}:{x.Name}"));

                //sb.Append($"In:[{InputTypes.Select(x => x.Type )}]");
            }

            sb.Append($"");
            sb.Append($"");
            sb.Append($"");
            sb.Append($"");

            return sb.ToString();
        }*/

    }
}
