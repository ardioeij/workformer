using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Reflection.Metadata;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto;
using workflowtransformer.dataset.adapter.dto.workflow;

namespace workflowtransformer.dataset.collector
{
    public class SourceCodeUtils
    {

        public static string Serialize(object obj)
        {
            var jsonOption = new JsonSerializerOptions
            {
                WriteIndented = true,
            };

            var json = JsonSerializer.Serialize(obj, jsonOption);
            return json;
        }

        public static string CleanUpJson(string json)
        {
            if (string.IsNullOrWhiteSpace(json))
            {
                return string.Empty;
            }
            return json.ReplaceLineEndings("").Replace("  ", " ").Replace("  ", " ").Replace("\":", "\" :").Replace("\",", "\" ,").Replace("null,", "null ,").Replace("[]}", "[ ] }")
                .Replace("],", "] ,").Replace("},", "} ,").Replace("]}", "] }").Replace("\\u0027", "'")
                ;
        }

        public static List<Function> ExtractFunctions(string sourceCodeContent)
        {
            var result = new List<Function>();
            try
            {
                var pattern = @"(?<function>(?<modifiers>(public|private|protected|internal|static|partial|async|override|virtual|abstract|sealed|extern|unsafe)*)\s+(?<returnType>[\w<>,. ]+)\s+(?<functionName>\w+)\s*\((?<parameters>[^\)]*)\)\s*\{(?<content>([^{}]+|\{(?<DEPTH>)|\}(?<-DEPTH>))*(?(DEPTH)(?!)))\})";

                // Use Regex.Replace to remove indentation and break line
                var removeIndentioanPattern = @"^\s+|\r\n?|\n";
                var codeWithoutIndentation = Regex.Replace(sourceCodeContent, removeIndentioanPattern, " ", RegexOptions.Multiline, TimeSpan.FromSeconds(5));

                var matches = Regex.Matches(codeWithoutIndentation, pattern, RegexOptions.Multiline, TimeSpan.FromSeconds(5));

                // Loop through the matched functions
                foreach (Match match in matches)
                {
                    // Access captured groups to get function details
                    var modifiers = match.Groups["modifiers"].Value.Trim();
                    var returnType = match.Groups["returnType"].Value.Trim();
                    var functionName = match.Groups["functionName"].Value.Trim();
                    var parameters = match.Groups["parameters"].Value;
                    var content = match.Groups["content"].Value;

                    var code = cleanCode(modifiers, returnType, functionName, parameters, content);

                    if (!isValid(modifiers, returnType, functionName, parameters, code))
                    {
                        continue;
                    }

                    var func = new Function
                    {
                        Name = functionName,
                        Code = code
                    };

                    result.Add(func);
                }

                return result;
            }
            catch (Exception ex)
            {
                return result;
            }
        }

        private static string cleanCode(string modifiers, string returnType, string functionName, string parameters, string content)
        {
            var removeCommentPattern = @"(//.*?$|/\*.*?\*/)";
            var codeWithoutComments = Regex.Replace(content, removeCommentPattern, string.Empty, RegexOptions.Multiline | RegexOptions.Singleline);
            codeWithoutComments = codeWithoutComments.Replace("\t", " ");

            var code = $"{modifiers} {returnType} {functionName}({parameters}){{{codeWithoutComments}}}".Trim();

            return code;
        }

        private static bool isValid(string modifiers, string returnType, string functionName, string parameters, string fullCode)
        {
            var syntaxModifiers = new string[] { "public", "private", "internal", "protected" };
            var syntaxBasic = new string[] { "if", "else", "for", "while", "foreach" };

            if (syntaxModifiers.Contains(returnType) && string.IsNullOrWhiteSpace(modifiers))
            {
                return false;
            }

            if (string.IsNullOrWhiteSpace(functionName)
                || (string.IsNullOrWhiteSpace(fullCode) || fullCode.Replace(" ", "").Length == 0)
                || (!string.IsNullOrWhiteSpace(modifiers) && !syntaxModifiers.Contains(modifiers))
                )
            {
                return false;
            }

            if (string.IsNullOrWhiteSpace(fullCode) || fullCode == Environment.NewLine || fullCode == "\n" || fullCode == "\r" || fullCode == "\r\n" ||
                string.IsNullOrWhiteSpace(functionName) || functionName == Environment.NewLine || functionName == "\n" || functionName == "\r" || functionName == "\r\n"
                )
            {
                return false;
            }

            if (syntaxBasic.Any(x => functionName.StartsWith(x)) || syntaxBasic.Any(x => fullCode.StartsWith(x)))
            {
                return false;
            }



            return true;
        }


    }
}
