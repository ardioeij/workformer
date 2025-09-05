using System;
using System.Linq;
using System.IO;
using System.Collections;
using System.Collections.Generic;

using workflowtransformer.dataset.collector.generative;
using workflowtransformer.dataset.collector.generative.grabber;
using System.Text.Json;
using System.Net.Http.Headers;
using System.Text.RegularExpressions;
using workflowtransformer.dataset.collector;
using workflowtransformer.dataset.collector.generative.source;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.Extensions.Logging;

var generativeCollector = new GenerativeCollector();

const string basePath = @"D:\Colleges\PhD\";

Console.WriteLine("Input the menu number, then press enter");
Console.WriteLine("0. Custom Temp");
Console.WriteLine("1. Create Source-Code Dataset");
Console.WriteLine("2. Source-Code to Workflow");
Console.WriteLine("3. Workflow to User-Story");
Console.WriteLine("4. Source-Code to User-Story");
Console.WriteLine("5. Genetic Algorithm Synthetic Data Generation");
Console.WriteLine("6. Merge User-Story");
Console.WriteLine("7. VaultCode To UserStories");
Console.WriteLine("8. VaultCode To Workflows");
Console.WriteLine("9. Count dataset");
Console.WriteLine("10. Transform Function Code To Flatlines AST + Code ");
Console.WriteLine("11. Transform to plain user story");
Console.WriteLine("12. Transform to plain user story and Source Code To Workflow");
Console.WriteLine("13. Transform Workflow To Flatlines");
Console.WriteLine("14. Split Source Code Function To Flatlines");
Console.WriteLine("15. Code To String");
Console.WriteLine("16. Code To Workflow");
Console.WriteLine("17. Code To Token");


static void rosly_parsing()
{
    string inputFile = basePath + @"\src\WorkflowTransformer\transformer\translation\text2code\dataset\trimmed_small_medium_code.txt";  // Your dataset file
    string outputFile = "csharp_token_vocab.txt";

    var tokenSet = new HashSet<string>();

    foreach (var line in File.ReadLines(inputFile))
    {
        if (string.IsNullOrWhiteSpace(line))
            continue;

        var syntaxTree = CSharpSyntaxTree.ParseText(line);
        var tokens = syntaxTree.GetRoot().DescendantTokens();

        foreach (var token in tokens)
        {
            var kind = token.Kind();

            // Skip comments, whitespace, directives, etc.
            if (kind == SyntaxKind.WhitespaceTrivia ||
                kind == SyntaxKind.EndOfLineTrivia ||
                kind == SyntaxKind.SingleLineCommentTrivia ||
                kind == SyntaxKind.MultiLineCommentTrivia ||
                kind == SyntaxKind.RegionDirectiveTrivia ||
                kind == SyntaxKind.EndRegionDirectiveTrivia)
            {
                continue;
            }

            string text = token.Text.Trim();
            if (!string.IsNullOrEmpty(text))
            {
                tokenSet.Add(text);
            }
        }
    }

    File.WriteAllLines(outputFile, tokenSet.OrderBy(t => t));
    Console.WriteLine($"Saved {tokenSet.Count} unique C# tokens from file to {outputFile}");
}


var opt = Console.ReadLine();
if (string.IsNullOrWhiteSpace(opt))
{
    Console.WriteLine("Invalid Menu");
    return;
}

if (opt == "1")
{
    generativeCollector.CreateSourceCodeDataset(basePath + @"\c_sharp\sourcecode.txt");

    Console.WriteLine($"CreateSourceCodeDataset Done");
}
else if (opt == "2")
{
    generativeCollector.SourceCodesToWorkflows();
    Console.WriteLine($"SourceCodesToWorkflows Created");
}
else if (opt == "3")
{
    generativeCollector.WorkflowsToUserStories();
    Console.WriteLine($"WorkflowsToUserStories Done");
}
else if (opt == "4")
{
    generativeCollector.SourceCodeToUserStories();
    Console.WriteLine($"SourceCodeToUserStories Done");
}
else if (opt == "6")
{
    var collector = new RetroDataCollector();
    collector.MergeUserStory_Workflow_NdJson();
    Console.WriteLine($"MergeUserStory_Workflow Done");
}
else if (opt == "7")
{
    var collector = new SourceCodeToWorkflow();
    collector.TransformSourceCodeToUserStories(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\dataset\full_userstories.ndjson");
    Console.WriteLine($"TransformSourceCodeToUserStories Done");
}
else if (opt == "8")
{
    var collector = new SourceCodeToWorkflow();

    Console.WriteLine($"TransformSourceCodeToWorkflows Small");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_workflows_2025.ndjson");

    Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_workflows_2025.ndjson");

    Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_workflows_2025.ndjson");
}
else if (opt == "9")
{
    var collector = new SourceCodeToWorkflow();
    var rows = 0;


    rows = collector.Count(basePath + @"\c_sharp\small_workflows.ndjson");
    Console.WriteLine($"Small Workflows = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\small_workflows.ndjson").Length) / 1024 / 1024)} MB ");

    rows = collector.Count(basePath + @"\c_sharp\small_userstories.txt");
    Console.WriteLine($"Small UserStories = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\small_userstories.txt").Length) / 1024 / 1024)} MB ");

    
    rows = collector.Count(basePath + @"\c_sharp\medium_workflows.ndjson");
    Console.WriteLine($"Full Workflows = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\medium_workflows.ndjson").Length) / 1024 / 1024)} MB ");

    rows = collector.Count(basePath + @"\c_sharp\medium_userstories.txt");
    Console.WriteLine($"Full UserStories = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\medium_userstories.txt").Length) / 1024 / 1024)} MB ");


    rows = collector.Count(basePath + @"\c_sharp\full_workflows.ndjson");
    Console.WriteLine($"Full Workflows = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\full_workflows.ndjson").Length) / 1024 / 1024)} MB ");

    rows = collector.Count(basePath + @"\c_sharp\full_userstories.txt");
    Console.WriteLine($"Full UserStories = {rows}, Size={((new FileInfo(basePath + @"\c_sharp\full_userstories.txt").Length) / 1024 / 1024)} MB ");
}
else if (opt == "10")
{
    var collector = new SourceCodeToWorkflow();

    Console.WriteLine($"TransformSourceCodeToWorkflows Small Lines");
    collector.TransformSourceCodeToFlatStatementLines(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_sourcecode_statement_lines.txt");
    Console.WriteLine($"TransformSourceCodeToWorkflows Small AST Lines");
    collector.TransformSourceCodeToFlatASTStatementLines(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_sourcecode_ast_statement_lines.txt");

    Console.WriteLine($"TransformSourceCodeToWorkflows Medium Lines");
    collector.TransformSourceCodeToFlatStatementLines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_statement_lines.txt");
    Console.WriteLine($"TransformSourceCodeToWorkflows Medium AST Lines");
    collector.TransformSourceCodeToFlatASTStatementLines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_ast_statement_lines.txt");

    Console.WriteLine($"TransformSourceCodeToWorkflows Full Lines");
    collector.TransformSourceCodeToFlatStatementLines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_statement_lines.txt");
    Console.WriteLine($"TransformSourceCodeToWorkflows Full AST Lines");
    collector.TransformSourceCodeToFlatASTStatementLines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_ast_statement_lines.txt");
}
else if (opt == "11")
{
    Console.WriteLine($"TransformSourceCodeToPlainUserStories Small");
    new SourceCodeToWorkflow().TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_userstories.txt");

    Console.WriteLine($"TransformSourceCodeToPlainUserStories Medium");
    new SourceCodeToWorkflow().TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_userstories.txt");

    Console.WriteLine($"TransformSourceCodeToPlainUserStories Full");
    new SourceCodeToWorkflow().TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\full_userstories.txt");
}
else if (opt == "12")
{
    var collector = new SourceCodeToWorkflow();

    Console.WriteLine($"TransformSourceCodeToWorkflows Small");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_workflows.ndjson");

    Console.WriteLine($"TransformSourceCodeToPlainUserStories Small");
    collector.TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_userstories.txt");


    Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_workflows.ndjson");

    Console.WriteLine($"TransformSourceCodeToPlainUserStories Medium");
    collector.TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_userstories.txt");


    Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    collector.TransformSourceCodeToWorkflows(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_workflows.ndjson");

    Console.WriteLine($"TransformSourceCodeToPlainUserStories Full");
    collector.TransformSourceCodeToPlainUserStories(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\full_userstories.txt");
}
else if (opt == "13")
{
    var collector = new SourceCodeToWorkflow();

    Console.WriteLine($"TransformSourceCodeToWorkflows Small");
    collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_sourcecode_lines.txt");

    Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_lines.txt");

    Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_lines.txt");
}
else if (opt == "14")
{
    Console.WriteLine($"CreateSourceCodeDataset");
    var outputFileSourceCodeFunction = basePath + @"\c_sharp\sourcecode_functions.txt";

    var localSource = new LocalSource();
    localSource.Folders = new List<LocalSourceFolderOption>
        {
        };
    var content = localSource.CreateSourceCodeDataset();

    var collector = new SourceCodeToWorkflow();
    var i = 1;
    foreach(var folder in localSource.Folders)
    {
        Console.WriteLine($"SplitSourceCodeFunctionToFlatlines {folder.OutputFile}");
        collector.SplitSourceCodeFunctionToFlatlines(folder.OutputFile, @$"{basePath}\c_sharp\ardvro_ast_sourcecode_lines_{i.ToString().PadLeft(2, '0')}.txt");
        i++;
    }

    //Console.WriteLine($"TransformSourceCodeToWorkflows Small");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_sourcecode_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_lines.txt");
}
else if (opt == "15")
{
    var collector = new SourceCodeToWorkflow();
    collector.CodeToText_CodeVault(basePath + @"\c_sharp\small_train.jsonl", @$"D:\Colleges\PhD\c_sharp\small_ast_requirements.txt");

    collector.CodeToText(basePath + @"\c_sharp\sourcecode_lines_01.txt", basePath + @"\c_sharp\ast_requirements_lines_01.txt");
}
else if (opt == "16")
{
    var collector = new SourceCodeToWorkflow();
    for(var i=1; i <= 8; i++)
    {
        Console.WriteLine($"collector.CodeToWorkflow {i}");
        collector.CodeToWorkflow(basePath + @"\c_sharp\sourcecode_functions_{i.ToString().PadLeft(2, '0')}.txt", basePath + @"\c_sharp\workflow_{i.ToString().PadLeft(2, '0')}_2025.ndjson");
    }

}
else if (opt == "17")
{
    var collector = new SourceCodeToWorkflow();
    // collector.CodeToText_CodeVault(basePath + @"\c_sharp\small_train.jsonl", @$"D:\Colleges\PhD\c_sharp\small_ast_requirements.txt");

    //collector.CodeToToken(basePath + @"\c_sharp\sourcecode_lines_01.txt", basePath + @"\c_sharp\ast_tokens_lines_01.txt");
    //ast_sourcecode_lines_


    collector.CodeToTokenCode(basePath + @"\c_sharp\ardvro_ast_sourcecode_lines_01.txt", basePath + @"\c_sharp\ardvro_token_code_lines.txt");

    //for (var i = 1; i <= 8; i++)
    //{
    //    Console.WriteLine($"collector.CodeToCodeToken {i}");
    //    collector.CodeToCodeToken($basePath + @"\c_sharp\ast_sourcecode_lines_{i.ToString().PadLeft(2, '0')}.txt", $basePath + @"\c_sharp\code_token_lines_{i.ToString().PadLeft(2, '0')}.txt");
    //}

    //Console.WriteLine($"collector.CodeToWorkflow small_sourcecode_lines.txt");
    //collector.CodeToCodeToken($basePath + @"\c_sharp\small_sourcecode_lines.txt", $basePath + @"\c_sharp\small_code_token_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_lines.txt");
}
else if (opt == "0")
{
    //var collector = new SourceCodeToWorkflow();

    //Console.WriteLine($"TransformSourceCodeToWorkflows Small");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_sourcecode_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Medium");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_sourcecode_lines.txt");

    //Console.WriteLine($"TransformSourceCodeToWorkflows Full");
    //collector.TransformSourceCodeToFlatlines(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_sourcecode_lines.txt");


    //Console.WriteLine($"collector.CodeToWorkflow medium_sourcecode_lines.txt");
    //collector.CodeToCodeToken($basePath + @"\c_sharp\medium_sourcecode_lines.txt", $basePath + @"\c_sharp\medium_code_token_lines.txt");

    //Console.WriteLine($"collector.CodeToWorkflow full_sourcecode_lines.txt");
    //collector.CodeToCodeToken($basePath + @"\c_sharp\full_sourcecode_lines.txt", $basePath + @"\c_sharp\full_code_token_lines.txt");

    //collector.ExtractCodeVaultToFunctions(basePath + @"\c_sharp\small_train.jsonl", basePath + @"\c_sharp\small_functions.txt");

    //collector.ExtractCodeVaultToFunctions(basePath + @"\c_sharp\medium_train.jsonl", basePath + @"\c_sharp\medium_functions.txt");
    //collector.ExtractCodeVaultToFunctions(basePath + @"\c_sharp\full_train.jsonl", basePath + @"\c_sharp\full_functions.txt");

    rosly_parsing();
}

Console.WriteLine("Finished");
Console.ReadKey();
