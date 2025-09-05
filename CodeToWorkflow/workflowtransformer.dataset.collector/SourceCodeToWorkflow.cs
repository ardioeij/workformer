using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using workflowtransformer.dataset.adapter.dto.workflow;
using workflowtransformer.dataset.adapter.dto;

using Microsoft.CodeAnalysis;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using workflowtransformer.dataset.collector.generative.source;

namespace workflowtransformer.dataset.collector
{
    public class SourceCodeToWorkflow
    {
        private AbstractSyntaxTreeParser _abstractSyntaxTreeParser = new AbstractSyntaxTreeParser();
        private RetroDataCollector _retroCollector = new RetroDataCollector();

        JsonSerializerOptions _jsonoptions = new JsonSerializerOptions
        {
            ReadCommentHandling = JsonCommentHandling.Skip,
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            //Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };

        public void TrimFile(string datasource, string outputFile)
        {
            Console.WriteLine("Trimming ...");

            if (File.Exists(outputFile))
            {
                File.Delete(outputFile);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFile, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            writer.WriteLine(line);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }
        }

        public void ExtractCodeVaultToFunctions(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
                    string outputFunctions = @"D:\Colleges\PhD\c_sharp\dataset\small_functions.txt")
        {
            if (File.Exists(outputFunctions))
            {
                File.Delete(outputFunctions);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFunctions, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);
                            var sb = new StringBuilder();

                            var code = codeVault.Code.RemoveBreakLine().Replace("\t", " ").Replace("  ", "");
                            writer.WriteLine(code);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }

        }

        public void TransformSourceCodeToFlatStatementLines(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputFile = @"D:\Colleges\PhD\c_sharp\dataset\small_workflows_lines.txt")
        {
            if (File.Exists(outputFile))
            {
                File.Delete(outputFile);
            }

            var writtenLines = new HashSet<string>();

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFile, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);
                            var sb = new StringBuilder();

                            var sourceCodeLines = _abstractSyntaxTreeParser.CodeToSourceCodeStatementLines(codeVault.Code);
                            foreach (var sourceCodeLine in sourceCodeLines)
                            {
                                var normalized = Normalize(sourceCodeLine);
                                if (writtenLines.Add(normalized)) // Add returns false if already exists
                                {
                                    writer.WriteLine(sourceCodeLine);
                                }
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


        public void TransformSourceCodeToFlatASTStatementLines(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputFile = @"D:\Colleges\PhD\c_sharp\dataset\small_workflows_lines.txt")
        {
            if (File.Exists(outputFile))
            {
                File.Delete(outputFile);
            }

            var writtenLines = new HashSet<string>();

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputFile, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);
                            var sb = new StringBuilder();

                            var sourceCodeLines = _abstractSyntaxTreeParser.CodeToSourceCodeASTStatementLines(codeVault.Code);
                            foreach (var sourceCodeLine in sourceCodeLines)
                            {
                                var normalized = Normalize(sourceCodeLine);
                                if (writtenLines.Add(normalized)) // Add returns false if already exists
                                {
                                    writer.WriteLine(sourceCodeLine);
                                }
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

        private string Normalize(string input)
        {
            return Regex.Replace(input, @"\s+", " ").Trim();
        }


        public void TransformSourceCodeToFlatlines(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputWorkflows = @"D:\Colleges\PhD\c_sharp\dataset\small_workflows.ndjson", string trimmedOutputFile = "")
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);
                            var sb = new StringBuilder();

                            var sourceCodeLines = _abstractSyntaxTreeParser.CodeToSourceCodeLines(codeVault.Code);
                            foreach (var sourceCodeLine in sourceCodeLines)
                            {
                                writer.WriteLine(sourceCodeLine);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }

            if (!string.IsNullOrWhiteSpace(trimmedOutputFile))
            {
                TrimFile(outputWorkflows, trimmedOutputFile);
            }
        }

        private void extractLine(Node node, StringBuilder? sb)
        {
            if (sb == null)
            {
                sb = new StringBuilder();
            }

            if (node.ComponentType != ComponentType.WF)
            {
                sb.AppendLine(node.Name);
            }

            if (node.Sequences != null)
            {
                foreach (var child in node.Sequences)
                {
                    extractLine(child, sb);
                }
            }
        }

        public void TransformSourceCodeToWorkflows(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputWorkflows = @"D:\Colleges\PhD\c_sharp\dataset\small_workflows.ndjson", string trimmedOutputFile = "")
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);

                            var workflow = codeVaultToWorkflow(codeVault);
                            if (workflow != null)
                            {
                                var json = JsonSerializer.Serialize(workflow, _jsonoptions);
                                var jsonUnespace = unEscape(json);
                                writer.WriteLine(jsonUnespace);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }

            if (!string.IsNullOrWhiteSpace(trimmedOutputFile))
            {
                TrimFile(outputWorkflows, trimmedOutputFile);
            }
        }

        public void TransformSourceCodeToUserStories(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputUserStories = @"D:\Colleges\PhD\c_sharp\dataset\small_userstories.ndjson")
        {
            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputUserStories, true))
                {
                    //Parallel.ForEach(reader.EnumerateLines(), new ParallelOptions { MaxDegreeOfParallelism = Environment.ProcessorCount }, line =>
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);

                            var userStory = codeVaultToUserStory(codeVault);
                            if (userStory != null)
                            {
                                var json = JsonSerializer.Serialize(userStory, _jsonoptions);
                                writer.WriteLine(json);
                                //sb.AppendLine(json);
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                    //);
                }
            }
        }

        public void TransformSourceCodeToSimpleUserStories(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputUserStories = @"D:\Colleges\PhD\c_sharp\dataset\small_userstories_simple.ndjson")
        {
            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputUserStories, false))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);

                            var userStory = codeVaultToUserStory(codeVault);
                            var acceptanceCriterias = _retroCollector.CleanAcceptanceCriteria(userStory);
                            if (acceptanceCriterias != null && acceptanceCriterias.Length > 0)
                            {
                                var simpleUserStory = new
                                {
                                    Application = userStory.Application.Trim().ToLower().ToTitleCase(),
                                    Name = userStory.Feature.Trim().ToLower().ToTitleCase(),
                                    Descripion = _retroCollector.cleanDescription(userStory),
                                    AcceptanceCriteria = acceptanceCriterias,
                                };
                                var json = JsonSerializer.Serialize(simpleUserStory, _jsonoptions);
                                writer.WriteLine(json);
                            }
                            else
                            {
                                var simpleUserStory = new
                                {
                                    Application = userStory.Application.Trim().ToLower().ToTitleCase(),
                                    Name = userStory.Feature.Trim().ToLower().ToTitleCase(),
                                    Descripion = _retroCollector.cleanDescription(userStory),
                                };
                                var json = JsonSerializer.Serialize(simpleUserStory, _jsonoptions);
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

        public void TransformSourceCodeToPlainUserStories(string datasource = @"D:\Colleges\PhD\c_sharp\small_train.jsonl",
            string outputUserStories = @"D:\Colleges\PhD\c_sharp\dataset\small_userstories.txt", string trimmedOutputFile = "")
        {
            if (File.Exists(outputUserStories))
            {
                File.Delete(outputUserStories);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputUserStories, false))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);

                            var userStory = codeVaultToUserStory(codeVault);

                            var sb = new StringBuilder();

                            if (!string.IsNullOrWhiteSpace(userStory.Feature))
                            {
                                sb.Append(userStory.Feature.UpperCaseFirstChar());
                            }
                            if (!string.IsNullOrWhiteSpace(userStory.Function) && (userStory.Feature.TrimToLower() != userStory.Function.TrimToLower()))
                            {
                                sb.Append(". ");
                                sb.Append(userStory.Function.UpperCaseFirstChar());
                            }
                            if (!string.IsNullOrWhiteSpace(userStory.Goal))
                            {
                                sb.Append(". ");
                                sb.Append(userStory.Goal.UpperCaseFirstChar());
                            }
                            if (!string.IsNullOrWhiteSpace(userStory.Description))
                            {
                                sb.Append(". ");
                                sb.Append(userStory.Description.UpperCaseFirstChar());
                            }
                            var userstory = sb.ToString().RemoveBreakLine().RemoveIfStartsWith(".").RemoveIfEndsWith(".").Trim().RemoveSpecialCharacters(" _,.':=<>+-/\\*", " ").Replace("  ", " ").Replace("  ", " ").Trim();

                            writer.WriteLine(userstory);

                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }

            if (!string.IsNullOrWhiteSpace(trimmedOutputFile))
            {
                TrimFile(outputUserStories, trimmedOutputFile);
            }
        }

        private Node? codeVaultToWorkflow(CodeVault? codeVault)
        {
            if (codeVault == null)
            {
                return null;
            }

            var node = new Node
            {
                Name = codeVault.ShortDocString,
                Description = codeVault.DocString,
                ComponentType = ComponentType.WF,
                InputTypes = codeVaultsParamToColumns(codeVault.DocStringParams.Params.ToList()),
                OutputTypes = codeVaultsParamToColumns(codeVault.DocStringParams.Returns.ToList()),
                //OutputTypes = new List<Column> { new Column { Type = codeVault.ReturnType, Name="return" } }
            };

            var workflow = _abstractSyntaxTreeParser.CodeToWorkflow(codeVault.Code);
            workflow.Name = $"{node.Name} {workflow.Name}".RemoveSpecialCharacters(" ", "");
            //workflow.Description = $"{node.Description} {workflow.Description}";

            return workflow;
        }

        private List<Column> codeVaultsParamToColumns(List<CodeVaultDocStringParamDetail> codeVaultParams)
        {
            var columns = new List<Column>();

            if (codeVaultParams == null || codeVaultParams.Count == 0)
            {
                return columns;
            }

            foreach (var param in codeVaultParams)
            {
                var col = codeVaultParamToColumn(param);
                if (col != null)
                {
                    columns.Add(col);
                }
            }
            return columns;
        }

        private Column? codeVaultParamToColumn(CodeVaultDocStringParamDetail codeVaultParam)
        {
            if (codeVaultParam == null)
            {
                return null;
            }

            var col = new Column
            {
                Name = codeVaultParam.Identifier,
                Type = codeVaultParam.Type,
            };
            return col;
        }

        private UserStory? codeVaultToUserStory(CodeVault? codeVault)
        {
            if (codeVault == null)
            {
                return null;
            }

            var prefixInput = codeVault.DocStringParams.Returns?.Count() == 1 ? "Given inputs " : "Given input ";
            var prefixOutput = codeVault.DocStringParams.Params?.Count() == 1 ? "Result outputs " : "Result output ";

            var userStory = new UserStory
            {
                Feature = codeVault.ShortDocString.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim(),
                Function = codeVault.DocString.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim(),

                Goal = createString(codeVault.DocStringParams.Returns, prefixOutput),
                Description = createString(codeVault.DocStringParams.Params, prefixInput),

                AcceptanceCriterias = codeVault.DocStringParams.Params.Select(x => new AcceptanceCriteria
                {
                    Given = $"{x.DocString?.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim()} {x.Identifier} {x.Type}".RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim(),
                }).ToList()
            };

            return userStory;
        }

        private string createString(List<CodeVaultDocStringParamDetail> codeVaultDocStringParamDetails, string prefix)
        {
            if (codeVaultDocStringParamDetails == null)
            {
                return string.Empty;
            }

            var sbDesc = new StringBuilder();
            foreach (var par in codeVaultDocStringParamDetails)
            {
                var sb = new StringBuilder();
                if (!string.IsNullOrWhiteSpace(par.DocString))
                {
                    if (sbDesc.Length > 0)
                    {
                        sb.Append(", ");

                    }
                    sb.Append(par.DocString.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim().LowerCaseFirstChar());

                    if (!string.IsNullOrWhiteSpace(par.Identifier))
                    {
                        sb.Append(" named ");
                        sb.Append(par.Identifier.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim());

                        if (!string.IsNullOrWhiteSpace(par.Type))
                        {
                            sb.Append(" with type ");
                            sb.Append(par.Type.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim());
                        }
                    }
                }
                else
                {
                    if (!string.IsNullOrWhiteSpace(par.Identifier))
                    {
                        sb.Append("named ");
                        sb.Append(par.Identifier.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim());

                        if (!string.IsNullOrWhiteSpace(par.Type))
                        {
                            sb.Append(" with type ");
                            sb.Append(par.Type.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim());
                        }
                    }
                    else
                    {
                        if (!string.IsNullOrWhiteSpace(par.Type))
                        {
                            sb.Append("with type ");
                            sb.Append(par.Type.RemoveIfEndsWith(".").RemoveIfEndsWith(". ").RemoveBreakLine().Trim());
                        }
                    }
                }
                sbDesc.Append(sb);
            }

            if (sbDesc.Length > 0)
            {
                sbDesc.Insert(0, prefix);
            }

            return sbDesc.ToString();
        }

        private string cleanLine(string line)
        {
            return line.ReplaceLineEndings().Replace("NaN", "null").Replace("undefined", "null");//.Replace("\\", "").Replace("[", "").Replace("]", "").Replace("{","").Replace("}", "");
        }

        private string unEscape(string text)
        {
            var charsToEscape = new string[]
            {
                "\\u003C",
                "\\u003E",
                "\\u002F",
                "\\u0027",
                "\\u0026",
                "\\u0085",
                "\\u0028",
                "\\u0029",
                "\\u0022",
                "\\u005C",
                "\\u002B",
                "\\"
            };

            foreach (var chr in charsToEscape)
            {
                text = text.Replace(chr, string.Empty);
            }

            return text;
        }

        public int Count(string datasource)
        {
            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                var lines = reader.EnumerateLines();
                return lines.Count();
            }
        }



        public void SplitSourceCodeFunctionToFlatlines(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var sb = new StringBuilder();
                            var sourceCodeLines = _abstractSyntaxTreeParser.CodeToSourceCodeTokenLines(line);
                            foreach (var sourceCodeLine in sourceCodeLines)
                            {
                                writer.WriteLine(sourceCodeLine);
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

        public void SplitSourceCodeFunctionToSyntaxNode(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var sb = new StringBuilder();
                            var sourceCodeLines = _abstractSyntaxTreeParser.CodeToSourceCodeNodesLines(line);
                            foreach (var sourceCodeLine in sourceCodeLines)
                            {
                                writer.WriteLine(sourceCodeLine);
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


        public void CodeToText_CodeVault(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().Distinct();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tidyLine = cleanLine(line);
                            var codeVault = JsonSerializer.Deserialize<CodeVault>(tidyLine, _jsonoptions);

                            var codeDescription = _abstractSyntaxTreeParser.CodeToText(codeVault.Code);
                            writer.WriteLine(codeDescription);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }

        }


        public void CodeToText(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var codeDescription = _abstractSyntaxTreeParser.CodeToText(line);
                            writer.WriteLine(codeDescription);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                        }
                    }
                }
            }
        }


        public void CodeToWorkflow(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var workflow = _abstractSyntaxTreeParser.CodeToWorkflow(line);
                            if (workflow != null)
                            {
                                var json = JsonSerializer.Serialize(workflow, _jsonoptions);
                                var jsonUnespace = unEscape(json);
                                writer.WriteLine(jsonUnespace);
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


        public void CodeToToken(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var codeDescription = _abstractSyntaxTreeParser.CodeToToken(line);
                            if (!string.IsNullOrWhiteSpace(codeDescription))
                            {
                                writer.WriteLine(codeDescription);
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

        public void CodeToCodeToken(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tokens = _abstractSyntaxTreeParser.CodeToToken(line);
                            if (!string.IsNullOrWhiteSpace(tokens))
                            {
                                var codeToken = line.Trim() + " ~ " + tokens.Trim();
                                writer.WriteLine(codeToken);
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

        public void CodeToTokenCode(string datasource, string outputWorkflows)
        {
            if (File.Exists(outputWorkflows))
            {
                File.Delete(outputWorkflows);
            }

            using (var file = new FileStream(datasource, FileMode.Open))
            using (var reader = new StreamReader(file))
            {
                using (var writer = new StreamWriter(outputWorkflows, true))
                {
                    var lines = reader.EnumerateLines().ToList();
                    foreach (var line in lines)
                    {
                        try
                        {
                            var tokens = _abstractSyntaxTreeParser.CodeToToken(line);
                            if (!string.IsNullOrWhiteSpace(tokens))
                            {
                                var codeToken = (tokens.Trim() + "~" + line.Trim()).Trim();
                                writer.WriteLine(codeToken);
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

    }
}
