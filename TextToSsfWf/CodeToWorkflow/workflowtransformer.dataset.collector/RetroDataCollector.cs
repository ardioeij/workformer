using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;
using workflowtransformer.dataset.adapter.dto.workflow;

namespace workflowtransformer.dataset.collector
{
    public class RetroDataCollector
    {
        JsonSerializerOptions _jsonoptions = new JsonSerializerOptions
        {
            ReadCommentHandling = JsonCommentHandling.Skip,
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            
        };

        public void Merge(string sourceFile, string targetFile)
        {
            using (var file1 = new FileStream(sourceFile, FileMode.Open))
            {
                using (var reader1 = new StreamReader(file1))
                {
                    using (var writer = new StreamWriter(targetFile, true))
                    {
                        var lines = reader1.EnumerateLines();
                        foreach (var line in lines)
                        {
                            writer.WriteLine(line);
                        }
                    }
                }
            }
        }

        public void TransformUserStoryToPlainFormat(string inputFile = @"..\..\..\userstories.ndjson", string outputFile = @"D:\Colleges\PhD\c_sharp\userstories.txt")
        {
            var jsonoptions = new JsonSerializerOptions
            {
                ReadCommentHandling = JsonCommentHandling.Skip,
                PropertyNameCaseInsensitive = true,
            };

            using (var file = new FileStream(inputFile, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFile, false))
                {
                    var lines = reader.EnumerateLines();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var formattedUserStory = JsonSerializer.Deserialize<UserStory>(tidyLine, jsonoptions);
                            
                            var application = formattedUserStory.Application.Replace("Application", "").Trim().ToLower().ToTitleCase();
                            var name = formattedUserStory.Feature.Trim().ToLower().ToTitleCase();
                            var descripion = cleanDescription(formattedUserStory);
                            var acceptanceCriteria = CleanAcceptanceCriteria(formattedUserStory);

                            if (acceptanceCriteria != null && acceptanceCriteria.Length > 0)
                            {
                                var userstory = $"Application: {application}. Name: {name}. Description: {descripion} Acceptance Criteria: {string.Join(' ', acceptanceCriteria.Select(x => x))} ".RemoveBreakLine();
                                writer.WriteLine(userstory);
                            }
                            else
                            {
                                var userstory = $"Application: {application}. Name: {name}. Description: {descripion} ".RemoveBreakLine();
                                writer.WriteLine(userstory);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }
        }

        public void TransformUserStoryToSimpleFormat(string inputFile = @"..\..\..\userstories.ndjson", string outputFile = @"D:\Colleges\PhD\c_sharp\userstories.ndjson")
        {
            var jsonoptions = new JsonSerializerOptions
            {
                ReadCommentHandling = JsonCommentHandling.Skip,
                PropertyNameCaseInsensitive = true,
            };

            using (var file = new FileStream(inputFile, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFile, false))
                {
                    var lines = reader.EnumerateLines();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var formattedUserStory = JsonSerializer.Deserialize<UserStory>(tidyLine, jsonoptions);

                            var acceptanceCriteria = CleanAcceptanceCriteria(formattedUserStory);
                            if (acceptanceCriteria != null && acceptanceCriteria.Length > 0)
                            {
                                var simpleUserStory = new
                                {
                                    Application = formattedUserStory.Application.Trim().ToLower().ToTitleCase(),
                                    Name = formattedUserStory.Feature.Trim().ToLower().ToTitleCase(),
                                    Descripion = cleanDescription(formattedUserStory),
                                    AcceptanceCriteria = acceptanceCriteria,
                                };
                                var json = JsonSerializer.Serialize(simpleUserStory, jsonoptions);
                                writer.WriteLine(json);
                            }
                            else
                            {
                                var simpleUserStory = new
                                {
                                    Application = formattedUserStory.Application.Trim().ToLower().ToTitleCase(),
                                    Name = formattedUserStory.Feature.Trim().ToLower().ToTitleCase(),
                                    Descripion = cleanDescription(formattedUserStory),
                                };
                                var json = JsonSerializer.Serialize(simpleUserStory, jsonoptions);
                                writer.WriteLine(json);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }
        }

        public string cleanDescription(UserStory formattedUserStory)
        {
            var role = "";
            var func = "";
            var goal = "";

            if (!string.IsNullOrWhiteSpace(formattedUserStory.Role))
            {
                if (!formattedUserStory.Role.Trim().ToLower().StartsWith("as a"))
                {
                    role = $"As a {formattedUserStory.Role.Trim().LowerCaseFirstChar()}";
                }
                else
                {
                    role = $"{formattedUserStory.Role.Trim().UpperCaseFirstChar()}";
                }

                if (!role.Trim().ToLower().EndsWith(","))
                {
                    role += ", ";
                }
            }

            if (!string.IsNullOrWhiteSpace(formattedUserStory.Feature))
            {
                if (!formattedUserStory.Feature.Trim().ToLower().StartsWith("i want to"))
                {
                    func = $"I want to {formattedUserStory.Feature.Trim().LowerCaseFirstChar()}";
                }
                else
                {
                    func = $"{formattedUserStory.Feature.Trim().ToLower().UpperCaseFirstChar()}";
                }
            }

            if (!string.IsNullOrWhiteSpace(formattedUserStory.Goal))
            {
                if (!string.IsNullOrWhiteSpace(func) && !func.Trim().ToLower().EndsWith(",") && !func.Trim().ToLower().EndsWith("."))
                {
                    goal += ", ";
                }
                else if (!string.IsNullOrWhiteSpace(func))
                {
                    goal += " ";
                }

                if (!formattedUserStory.Goal.Trim().ToLower().StartsWith("so that"))
                {
                    goal += $"so that {formattedUserStory.Goal.Trim().LowerCaseFirstChar()}";
                }
                else
                {
                    goal += $"{formattedUserStory.Goal.Trim().ToLower().UpperCaseFirstChar()}";
                }
                if (!goal.Trim().ToLower().EndsWith("."))
                {
                    goal += ".";
                }
            }

            var desc = $"{role}{func}{goal}";

            desc = desc.Replace(" i ", " I ");

            return desc;
        }

        public string[] CleanAcceptanceCriteria(UserStory userStory)
        {
            var acceptanceCriterias = new List<string>();
            foreach(var us in userStory.AcceptanceCriterias)
            {
                var ac = "";
                if (!string.IsNullOrWhiteSpace(us.Given))
                {
                    if (!us.Given.Trim().ToLower().StartsWith("that") && !us.Given.Trim().ToLower().StartsWith("given that"))
                    {
                        ac = $"Given that {us.Given.Trim().ToLower()}";
                    }
                    else
                    {
                        ac = us.Given.Trim().ToLower().UpperCaseFirstChar();
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ".";
                }

                if (!string.IsNullOrWhiteSpace(us.When))
                {
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        ac += ", ";
                    }
                    if (!us.When.Trim().ToLower().StartsWith("when"))
                    {
                        ac += $"when {us.When.Trim().ToLower()}";
                    }
                    else
                    {
                        ac += us.Given.Trim().ToLower();
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ". ";
                }

                if (!string.IsNullOrWhiteSpace(us.Then))
                {
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        ac += ", ";
                    }
                    if (!us.Then.Trim().ToLower().StartsWith("then"))
                    {
                        ac += $"then {us.Then.Trim().ToLower()}";
                    }
                    else
                    {
                        ac += us.Then.Trim().ToLower();
                    }
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        if (!ac.Trim().EndsWith("."))
                        {
                            ac += ".";
                        }
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ".";
                }

                ac = ac.Replace(" i ", " I ");

                acceptanceCriterias.Add(ac);
            }

            return acceptanceCriterias.ToArray();
        }

        public string[] FlatenenAcceptanceCriteria(UserStory userStory)
        {
            var acceptanceCriterias = new List<string>();
            foreach (var us in userStory.AcceptanceCriterias)
            {
                var ac = "";
                if (!string.IsNullOrWhiteSpace(us.Given))
                {
                    if (!us.Given.Trim().ToLower().StartsWith("that") && !us.Given.Trim().ToLower().StartsWith("given that"))
                    {
                        ac = $"Given that {us.Given.Trim().ToLower()}";
                    }
                    else
                    {
                        ac = us.Given.Trim().ToLower().UpperCaseFirstChar();
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ".";
                }

                if (!string.IsNullOrWhiteSpace(us.When))
                {
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        ac += ", ";
                    }
                    if (!us.When.Trim().ToLower().StartsWith("when"))
                    {
                        ac += $"when {us.When.Trim().ToLower()}";
                    }
                    else
                    {
                        ac += us.Given.Trim().ToLower();
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ". ";
                }

                if (!string.IsNullOrWhiteSpace(us.Then))
                {
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        ac += ", ";
                    }
                    if (!us.Then.Trim().ToLower().StartsWith("then"))
                    {
                        ac += $"then {us.Then.Trim().ToLower()}";
                    }
                    else
                    {
                        ac += us.Then.Trim().ToLower();
                    }
                    if (!string.IsNullOrWhiteSpace(ac))
                    {
                        if (!ac.Trim().EndsWith("."))
                        {
                            ac += ".";
                        }
                    }
                }
                else if (!ac.Trim().EndsWith("."))
                {
                    ac += ".";
                }

                ac = ac.Replace(" i ", " I ");

                acceptanceCriterias.Add(ac);
            }

            return acceptanceCriterias.ToArray();
        }

        public void MergeUserStory_Workflow(string baseDir = @"..\..\..\sampledata", string outputFile = @"..\..\..\userstory_workflow.json")
        {
            //var sb = new StringBuilder();

            var list = new List<dynamic>();

            var workflowsDir = @$"{baseDir}\\workflow";
            var workflows = Directory.GetFiles(workflowsDir).Select(x => JsonSerializer.Deserialize<dynamic>(File.ReadAllText(x))).ToArray();

            var userStoriesDir = @$"{baseDir}\\userstory";
            var userStoriesSubDirs = Directory.GetDirectories(userStoriesDir);
            foreach (var subdir in userStoriesSubDirs)
            {
                var files = Directory.GetFiles(subdir);
                for (int i = 0; i < files.Length; i++)
                {
                    var userStoryJson = File.ReadAllText(files[i]);
                    var userStory = JsonSerializer.Deserialize<dynamic>(userStoryJson);
                    var keyvalue = new 
                    {
                        Key = userStory,
                        Value = workflows[i]
                    };

                    list.Add(keyvalue);
                }
            }

            var json = JsonSerializer.Serialize(list);

            File.WriteAllText(outputFile, json);

        }

        public void MergeUserStory_Workflow_NdJson(string baseDir = @"..\..\..\sampledata", string outputUserStoryFile = @"..\..\..\userstories.ndjson", string outputWorkflowFile = @"D:\Colleges\PhD\c_sharp\dataset\workflows.ndjson")
        {
            var sbUserStory = new StringBuilder();
            var sbWorkflow = new StringBuilder();

            var workflowsDir = @$"{baseDir}\\workflow";

            var workflows = Directory.GetFiles(workflowsDir)
                .Select(x => Newtonsoft.Json.JsonConvert.DeserializeObject<Node>(File.ReadAllText(x)
                .Replace("\"Workflow\"", "\"WF\"").Replace("\"Process\"", "\"PROC\"").Replace("\"ForEach\"", "\"LOOP\"")
                .Replace("\"Decision\"", "\"IF\"").Replace("\"DecisionBranch\"", "\"ELSE\"")
                )).ToArray();

            var userStoriesDir = @$"{baseDir}\\userstory";
            var userStoriesSubDirs = Directory.GetDirectories(userStoriesDir);
            foreach (var subdir in userStoriesSubDirs)
            {
                var files = Directory.GetFiles(subdir);
                for (int i = 0; i < files.Length; i++)
                {
                    var userStory = JsonSerializer.Deserialize<dynamic>(File.ReadAllText(files[i]));
                    var userStoryJson = JsonSerializer.Serialize(userStory);
                    sbUserStory.AppendLine(userStoryJson);

                    var workflowJson = JsonSerializer.Serialize<Node>(workflows[i], _jsonoptions);
                    sbWorkflow.AppendLine(workflowJson);
                }
            }

            File.WriteAllText(outputUserStoryFile, sbUserStory.ToString());
            File.WriteAllText(outputWorkflowFile, sbWorkflow.ToString());
        }


        private string cleanLine(string line)
        {
            return line.ReplaceLineEndings().Replace("NaN", "null").Replace("undefined", "null");
        }

    }

}
