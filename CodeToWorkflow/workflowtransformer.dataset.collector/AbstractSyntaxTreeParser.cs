using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using workflowtransformer.dataset.adapter.dto.workflow;
using System.Text.RegularExpressions;
using Column = workflowtransformer.dataset.adapter.dto.workflow.Column;


namespace workflowtransformer.dataset.collector
{
    public class AbstractSyntaxTreeParser
    {
        public string AnalyzeSyntaxNode(string code)
        {
            var sb = new StringBuilder();

            var syntaxNode = generateSyntaxTree(code);

            //var wf = ToWorkflow(syntaxNode);

            foreach (var node in syntaxNode.DescendantNodes())
            {
                var children = node.DescendantNodes();
                
                if (children != null && children.Count() > 0)
                {
                    sb.AppendLine($"{new string(' ', 0)}{node.Kind()} - {node}");
                }
            }

            //var json = JsonSerializer.Serialize(wf, new JsonSerializerOptions { WriteIndented = true });
            //File.WriteAllText("D:\\Colleges\\PhD\\c_sharp\\test01c.json", json);

            return sb.ToString();
        }
        
        public Node? CodeToWorkflow(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var wf = ToWorkflow(syntaxNode);

            if (wf.Sequences == null ||  wf.Sequences.Count == 0)
            {
                wf.Sequences = new List<Node> { new Node { ComponentType = ComponentType.PROC, Name = "Process" } };
            }

            return wf;
        }

        public string[] CodeToSourceCodeLines(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var skips = new string[] { "{", "}", "});", "};", "},", ")", "(", "),", ";", "," };

            var lines = syntaxNode.ToFullString().Split('\n').Select(x => x.Trim()).Where(x => !string.IsNullOrWhiteSpace(x) && !skips.Contains(x)).ToArray();

            return lines;
        }

        public string[] CodeToSourceCodeTokenLines(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var sourceCodeLinesKind = getChildNodes(syntaxNode);

            var skips = new string[] { "{", "}", "});", "};", "},", ")", "(", "),", ";", "," };

            var lines = sourceCodeLinesKind.Select(x => x.ToFullString()).Where(x => !string.IsNullOrWhiteSpace(x) && !skips.Contains(x)).ToArray();

            return lines;
        }

        public string[] CodeToSourceCodeNodesLines(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var sourceCodeLinesKind = getChildNodesTokens(syntaxNode);

            var skips = new string[] { "{", "}", "});", "};", "},", ")", "(", "),", ";", "," };

            var lines = sourceCodeLinesKind.Select(x => string.Join(' ', x.Select(x => x.Kind().ToString()))).ToArray();

            return lines;
        }

        private List<SyntaxNode> getChildNodes(SyntaxNode syntaxNode)
        {
            var results = new List<SyntaxNode>();
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return results;
            }
            
            var list = syntaxNode.IsKind(SyntaxKind.Block) ? syntaxNode.ChildNodes() : syntaxNode.DescendantNodes()?.FirstOrDefault(x => x.IsKind(SyntaxKind.Block))?.ChildNodes();
            if (list == null)
            {
                results.Add(syntaxNode);
                return results;
            }

            foreach (var node in list)
            {
                results.Add(node);

                //var childs = getChildNodes(node);
                //results.AddRange(childs);
            }

            return results;
        }

        private List<List<SyntaxNode>> getChildNodesTokens(SyntaxNode syntaxNode, bool isGetDescendantNodes = false)
        {
            var results = new List<List<SyntaxNode>>();
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return results;
            }

            IEnumerable<SyntaxNode> list;
            if (isGetDescendantNodes)
            {
                list = syntaxNode.DescendantNodes();
            }
            else
            {
                list = syntaxNode.IsKind(SyntaxKind.Block) ? syntaxNode.ChildNodes() : syntaxNode.DescendantNodes()?.FirstOrDefault(x => x.IsKind(SyntaxKind.Block))?.ChildNodes();
            }

            if (list == null)
            {
                results.Add(new List<SyntaxNode>() { syntaxNode });
                return results;
            }

            foreach (var node in list)
            {
                var childs = getChildNodesTokensRecursive(node);
                if (childs?.Count > 0)
                {
                    results.Add(childs);
                }
            }

            return results;
        }

        private List<SyntaxNode> getChildNodesTokensRecursive(SyntaxNode syntaxNode)
        {
            var results = new List<SyntaxNode>();
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return results;
            }

            var list = syntaxNode.ChildNodes()?.FirstOrDefault()?.ChildNodes();
            if (list == null)
            {
                results.Add(syntaxNode);
                return results;
            }

            foreach (var node in list)
            {
                var childs = getChildNodesTokensRecursive(node);
                if (childs?.Count > 0)
                {
                    results.AddRange(childs);
                }
                else
                {
                    results.Add(node);
                }
            }

            return results;
        }

        private SyntaxNode generateSyntaxTree(string code)
        {
            SyntaxTree syntaxTree = CSharpSyntaxTree.ParseText(code);
            
            return syntaxTree.GetRoot();
        }

        private Node? ToWorkflow(SyntaxNode syntaxNode)
        {
            var kind = syntaxNode.Kind();
            if (kind != SyntaxKind.CompilationUnit)
            {
                return null;
            }

            var workflow = new Node { ComponentType = ComponentType.WF };

            SyntaxNode localStatement = null;

            List<SyntaxNode> descendants = new List<SyntaxNode>();

            if (syntaxNode?.DescendantNodes()?.FirstOrDefault() is GlobalStatementSyntax globalStatementSyntax)
            {
                if (globalStatementSyntax.Statement is LocalFunctionStatementSyntax localFunctionStatementSyntax)
                {
                    localStatement = localFunctionStatementSyntax;

                    workflow.Name = localFunctionStatementSyntax?.Identifier.Text?.ToTitleCase();
                    descendants = localFunctionStatementSyntax?.ParameterList?.DescendantNodes()?.ToList();

                    if (localFunctionStatementSyntax.ReturnType != null)
                    {
                        workflow.OutputTypes.Add(new Column { Type = convertTypeToString(localFunctionStatementSyntax.ReturnType.ToString()) });
                    }
                }
            }
            else if (syntaxNode?.DescendantNodes()?.FirstOrDefault() is MethodDeclarationSyntax methodDeclarationSyntax)
            {
                workflow.Name = methodDeclarationSyntax?.Identifier.Text?.ToTitleCase();
                descendants = methodDeclarationSyntax?.ParameterList?.DescendantNodes()?.ToList();
                if (methodDeclarationSyntax.ReturnType != null)
                {
                    workflow.OutputTypes.Add(new Column { Type = convertTypeToString(methodDeclarationSyntax.ReturnType.ToString()) });
                }
            }
            else
            {
                localStatement = syntaxNode;
            }

            workflow.Name = cleanUpText(workflow.Name);

            foreach (var prm in descendants)
            {
                if (!prm.IsKind(SyntaxKind.Parameter))
                {
                    continue;
                }

                var paramType = prm.ToFullString();
                var col = new Column
                {
                    Name = cleanUpText(paramType.Split(' ')[^1]),
                    Type = cleanUpText(convertTypeToString(paramType.Split(' ')[0])),
                };
                workflow.InputTypes.Add(col);
            }

            getChildNodes(workflow, localStatement);

            return workflow;
        }

        private void getChildNodes(Node workflow, SyntaxNode syntaxNode)
        {
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return;
            }

            if (workflow.ComponentType != ComponentType.WF)
            {
                if (string.IsNullOrWhiteSpace(workflow.Token))
                {
                    workflow.Token = getTokenString(syntaxNode);
                }
                else
                {
                    workflow.Token = $"{workflow.Token} {getTokenString(syntaxNode)}";
                }
            }

            var list = syntaxNode.IsKind(SyntaxKind.Block) 
                ? syntaxNode.ChildNodes() 
                : syntaxNode.DescendantNodes()?.FirstOrDefault(x => x.IsKind(SyntaxKind.Block))?.ChildNodes();
            if (list == null)
            {
                return;
            }

            foreach (var node in list)
            {
                if (node.IsKind(SyntaxKind.IfStatement))
                {
                    parseIfStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.ForEachStatement))
                {
                    parseForEachStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.ForStatement))
                {
                    parseForStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.WhileStatement))
                {
                    parseWhileStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.LocalDeclarationStatement))
                {
                    parseLocalDeclarationStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.ExpressionStatement))
                {
                    parseLocalExpressionStatement(workflow, node);
                }
                else if (node.IsKind(SyntaxKind.ReturnStatement))
                {
                    parseLocalReturnStatement(workflow, node);
                }
                else
                {
                    parseCommonProcess(workflow, node);
                }

                if (string.IsNullOrWhiteSpace(workflow.Description) 
                    && workflow.ComponentType != ComponentType.WF)
                {
                    workflow.Description = node.ToFullString().RemoveBreakLine().Trim().Replace("  ", "");
                }
            }
        }

        private string getTokenString(SyntaxNode node)
        {
            var sourceCodeLinesKind = getChildNodesTokens(node, true);

            var lines = sourceCodeLinesKind.SelectMany(x => x).Select(x => x.Kind().ToString().Trim().RemoveBreakLine()).Where(x => !string.IsNullOrWhiteSpace(x)).Distinct();

            var tokens = string.Join(' ', lines);

            return tokens;
        }

        private Node? parseIfStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not IfStatementSyntax statement)
            {
                return null;
            }

            var node = new Node() 
            { 
                ComponentType = ComponentType.IF, 
                Name = $"if ({statement.Condition.ToFullString()})",
            };

            buildDecisionBranchRecursive(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private void buildDecisionBranchRecursive(Node node, IfStatementSyntax statement)
        {
            var branch = new Node
            {
                Name = $"if ({cleanUpText(statement.Condition.ToFullString())})",
                ComponentType = ComponentType.ELSE,
                DecisionBranchExpressions = new List<DecisionBranchExpression>()
            };

            if (statement.Condition is BinaryExpressionSyntax binaryExpressionSyntax)
            {
                if (binaryExpressionSyntax.Left is BinaryExpressionSyntax leftExp)
                {
                    branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                    {
                        Conjunction = binaryExpressionSyntax.OperatorToken.Text,
                        Left = leftExp.Left.ToFullString(),
                        Operator = leftExp.OperatorToken.ToString(),
                        Right = leftExp.Right.ToFullString(),
                    });
                    buildDecisionBranchExpressionRecursive(branch, leftExp);
                }
                else
                {
                    if (binaryExpressionSyntax.Left != null)
                    {
                        branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                        {
                            Left = binaryExpressionSyntax.Left.ToFullString(),
                        });
                    }
                    else
                    {
                        branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                        {
                            Left = binaryExpressionSyntax.ToFullString(),
                        });
                    }
                }

                if (binaryExpressionSyntax.Right is BinaryExpressionSyntax rightExp)
                {
                    branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                    {
                        Conjunction = binaryExpressionSyntax.OperatorToken.Text,
                        Left = rightExp.Left.ToFullString(),
                        Operator = rightExp.OperatorToken.ToString(),
                        Right = rightExp.Right.ToFullString(),
                    });
                    buildDecisionBranchExpressionRecursive(branch, rightExp);
                }
            }
            else if (statement.Condition is PrefixUnaryExpressionSyntax prefixUnaryExpressionSyntax)
            {
                branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                {
                    Conjunction = prefixUnaryExpressionSyntax.OperatorToken.Text,
                    Left = prefixUnaryExpressionSyntax.Operand.ToFullString(),
                    Operator = prefixUnaryExpressionSyntax.OperatorToken.ToString(),
                });
            }
            else if (statement.Condition is MemberAccessExpressionSyntax memberAccessExpression)
            {
                branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                {
                    Conjunction = memberAccessExpression.OperatorToken.Text,
                    Left = memberAccessExpression.ToFullString(),
                    Operator = memberAccessExpression.OperatorToken.ToString(),
                });
            }
            else if (statement.Condition != null)
            {
                branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                {
                    Left = statement.Condition.ToFullString(),
                });
            }
            else
            {
                branch.DecisionBranchExpressions.Add(new DecisionBranchExpression
                {
                    Left = statement.ToFullString(),
                });
            }

            if (statement.Statement != null && statement.Statement is BlockSyntax blocks)
            {
                getChildNodes(branch, blocks);
            }
            
            if (statement.Else != null && statement.Else.Statement is IfStatementSyntax elseStatement)
            {
                buildDecisionBranchRecursive(node, elseStatement);
            }

            if (node.Sequences == null)
            {
                node.Sequences = new List<Node>();
            }

            node.Sequences.Add(branch);
        }

        private void analyzeCondition(ExpressionSyntax condition)
        {
            switch (condition)
            {
                case BinaryExpressionSyntax binaryExpression:
                    Console.WriteLine($"Binary expression: {binaryExpression}");
                    analyzeCondition(binaryExpression.Left);
                    analyzeCondition(binaryExpression.Right);
                    break;
                case ParenthesizedExpressionSyntax parenthesizedExpression:
                    Console.WriteLine($"Parenthesized expression: {parenthesizedExpression}");
                    analyzeCondition(parenthesizedExpression.Expression);
                    break;
                case PrefixUnaryExpressionSyntax prefixUnaryExpression:
                    Console.WriteLine($"Prefix unary expression: {prefixUnaryExpression}");
                    analyzeCondition(prefixUnaryExpression.Operand);
                    break;
                case LiteralExpressionSyntax literalExpression:
                    Console.WriteLine($"Literal expression: {literalExpression}");
                    break;
                case IdentifierNameSyntax identifierName:
                    Console.WriteLine($"Identifier name: {identifierName}");
                    break;
                case InvocationExpressionSyntax invocationExpression:
                    Console.WriteLine($"Invocation expression: {invocationExpression}");
                    break;
                case MemberAccessExpressionSyntax memberAccessExpression:
                    Console.WriteLine($"Member access expression: {memberAccessExpression}");
                    break;
                case ConditionalExpressionSyntax conditionalExpression:
                    Console.WriteLine($"Conditional expression: {conditionalExpression}");
                    break;
                case CastExpressionSyntax castExpression:
                    Console.WriteLine($"Cast expression: {castExpression}");
                    break;
                case TypeOfExpressionSyntax typeOfExpression:
                    Console.WriteLine($"TypeOf expression: {typeOfExpression}");
                    break;
                case ThisExpressionSyntax thisExpression:
                    Console.WriteLine($"This expression: {thisExpression}");
                    break;
                case BaseExpressionSyntax baseExpression:
                    Console.WriteLine($"Base expression: {baseExpression}");
                    break;
                case ElementAccessExpressionSyntax elementAccessExpression:
                    Console.WriteLine($"Element access expression: {elementAccessExpression}");
                    break;
                default:
                    Console.WriteLine($"Other expression: {condition}");
                    break;
            }
        }

        private void buildDecisionBranchExpressionRecursive(Node branch, BinaryExpressionSyntax binaryExpressionSyntax)
        {
            if (binaryExpressionSyntax != null && binaryExpressionSyntax.Left is BinaryExpressionSyntax leftExp)
            {
                var decisionBranch = new DecisionBranchExpression
                {
                    Conjunction = binaryExpressionSyntax.OperatorToken.Text,
                    Left = leftExp.Left.ToFullString(),
                    Operator = leftExp.OperatorToken.ToString(),
                    Right = leftExp.Right.ToFullString(),
                };
                branch.DecisionBranchExpressions.Add(decisionBranch);

                if (leftExp.Left != null && leftExp.Left is BinaryExpressionSyntax leftLeftExp)
                {
                    buildDecisionBranchExpressionRecursive(branch, leftLeftExp);
                }
            }
        }

        private Node? parseForEachStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not ForEachStatementSyntax statement)
            {
                return null;
            }
            
            var node = new Node()
            {
                ComponentType = ComponentType.LOOP,
                Name = $"For each {cleanUpText(statement.Identifier.Text)} {cleanUpText(statement.Expression.GetText().ToString())}",
                DecisionBranchExpressions = new List<DecisionBranchExpression>()
            };

            // Add the foreach variable and collection as a decision branch expression
            node.DecisionBranchExpressions.Add(new DecisionBranchExpression
            {
                Left = "Item",
                Operator = "in",
                Right = statement.Expression.ToString(),
                Conjunction = "" // No conjunction for a single iteration expression
            });

            getChildNodes(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private Node? parseForStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not ForStatementSyntax statement)
            {
                return null;
            }

            var node = new Node()
            {
                ComponentType = ComponentType.LOOP,
                Name = $"For {cleanUpText(statement?.Declaration?.ToString())}; {cleanUpText(statement?.Condition?.ToString())} {cleanUpText(statement?.Incrementors.ToString())}",
                DecisionBranchExpressions = new List<DecisionBranchExpression>()
            };

            // Extract the condition of the for loop and break it into expressions
            if (statement.Condition is BinaryExpressionSyntax binaryExpression)
            {
                parseBinaryExpression(binaryExpression, node.DecisionBranchExpressions, null);
            }

            getChildNodes(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private void parseBinaryExpression(BinaryExpressionSyntax binaryExpression, List<DecisionBranchExpression> decisionBranchExpressions, string? conjunction)
        {
            // Create a DecisionBranchExpression for the current binary expression
            var decisionBranch = new DecisionBranchExpression
            {
                Left = binaryExpression.Left.ToString(),
                Operator = binaryExpression.OperatorToken.Text,
                Right = binaryExpression.Right.ToString(),
                Conjunction = conjunction ?? ""
            };
            if (decisionBranchExpressions == null)
            {
                decisionBranchExpressions = new List<DecisionBranchExpression>();
            }
            decisionBranchExpressions.Add(decisionBranch);

            // Check for compound conditions (e.g., with AND/OR)
            if (binaryExpression.Left is BinaryExpressionSyntax leftBinary)
            {
                parseBinaryExpression(leftBinary, decisionBranchExpressions, binaryExpression.OperatorToken.Text);
            }
            if (binaryExpression.Right is BinaryExpressionSyntax rightBinary)
            {
                parseBinaryExpression(rightBinary, decisionBranchExpressions, binaryExpression.OperatorToken.Text);
            }
        }

        private Node? parseWhileStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not WhileStatementSyntax statement)
            {
                return null;
            }

            var node = new Node()
            {
                ComponentType = ComponentType.LOOP,
                Name = $"While {cleanUpText(statement.Condition.ToString())}",
                //InputTypes = parent.InputTypes.CloneList()
            };

            // Extract the condition of the for loop and break it into expressions
            if (statement.Condition is BinaryExpressionSyntax binaryExpression)
            {
                parseBinaryExpression(binaryExpression, node.DecisionBranchExpressions, null);
            }

            getChildNodes(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private Node? parseLocalDeclarationStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not LocalDeclarationStatementSyntax statement)
            {
                return null;
            }

            var node = new Node()
            {
                ComponentType = ComponentType.PROC,
            };

            if (statement.Declaration is VariableDeclarationSyntax variableDeclarationSyntax)
            {
                node.Name = cleanUpText(statement?.Declaration?.ToString());
                node.Description = statement?.Declaration?.ToString().Trim();
                //node.Token = getTokenString(statement.Declaration);
            }
            else
            {
                node.Name = cleanUpText(statement?.Declaration?.ToString().Split('.')[^1]);
                node.Description = statement?.Declaration?.ToString().Split('.')[^1].Trim();
                //node.Token = getTokenString(statement.Declaration);
            }

            /*foreach (var variable in statement.Declaration.Variables) 
            {
                if (variable?.Initializer?.Value is InvocationExpressionSyntax invocationExpression)
                {
                    foreach(var arg in invocationExpression.ArgumentList.Arguments)
                    {
                        node.InputTypes.Add(new Column
                        {
                            Name = arg.ToString(),
                            Type = "var"
                        });
                    }
                }
                else
                {
                    node.InputTypes.Add(new Column
                    {
                        Name = variable?.Identifier.Text,
                        Type = "var"
                    });
                }
            }*/

            getChildNodes(node, statement);

            //node.Description = $"Local declaration statement has {node.Sequences.Count} sequences: {string.Join(", ", node.Sequences.Select(x => x.Name))}";

            //node.OutputTypes = node.Sequences.SelectMany(x => x.OutputTypes).ToList().CloneList();

            //node.OutputTypes.Add(new Column { Type = statement.Declaration.Type.ToString() });

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private Node? parseLocalExpressionStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not ExpressionStatementSyntax statement)
            {
                return null;
            }

            var node = new Node()
            {
                Name = cleanUpText(statement.GetText().ToString()),
                Description = statement.GetText().ToString().Trim(),
                ComponentType = ComponentType.PROC,
            };

            getChildNodes(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private Node? parseLocalReturnStatement(Node parent, SyntaxNode syntaxNode)
        {
            if (syntaxNode is not ReturnStatementSyntax statement)
            {
                return null;
            }

            var node = new Node()
            {
                Name = cleanUpText(statement.GetText().ToString()),
                Description = statement.GetText().ToString().Trim(),
                ComponentType = ComponentType.PROC,
            };

            getChildNodes(node, statement);

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private Node? parseCommonProcess(Node parent, SyntaxNode syntaxNode)
        {
            var node = new Node()
            {
                Name = cleanUpText(syntaxNode.ToFullString().Trim()),
                Description = syntaxNode.ToFullString().Trim(),
                ComponentType = ComponentType.PROC,
            };

            if (parent.Sequences == null)
            {
                parent.Sequences = new List<Node>();
            }
            parent.Sequences.Add(node);

            return node;
        }

        private string cleanUpText(string text)
        {
            return Regex.Unescape(text.RemoveBreakLine().Replace("\t", "").Replace("  ", "").RemoveSpecialCharacters(" _.", ""));
        }

        public string convertTypeToString(string type)
        {
            if (isInteger(type))
            {
                return DataType.Integer.ToString();
            }
            else if (isDecimal(type))
            {
                return DataType.Decimal.ToString();
            }
            else if (isDateTime(type))
            {
                return DataType.DateTime.ToString();
            }
            else if (isString(type))
            {
                return DataType.String.ToString();
            }
            else if (isBoolean(type))
            {
                return DataType.Boolean.ToString();
            }
            else
            {
                return DataType.Object.ToString();
            }
        }

        public bool isInteger(string type)
        {
            var datatypes = new string[] {
                "int",
                "double",
                "byte",
                "short",
                "ushort",
                "long",
                "ulong",
                "uint",
                "Int16",
                "Int32",
                "Int64",
                "UInt16",
                "UInt32",
                "UInt64",
                "Single",
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public bool isDecimal(string type)
        {
            var datatypes = new string[] {
                "float",
                "decimal",
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public bool isNumeric(string type)
        {
            var datatypes = new string[] {
                "int",
                "float",
                "decimal",
                "double",
                "byte",
                "short",
                "ushort",
                "long",
                "ulong",
                "uint",
                "Int16",
                "Int32",
                "Int64",
                "UInt16",
                "UInt32",
                "UInt64",
                "Single",
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public bool isDateTime(string type)
        {
            var datatypes = new string[] {
                "DateTime",
                "TimeSpan",
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public bool isString(string type)
        {
            var datatypes = new string[] {
                "string",
                "char",
                "Guid"
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public bool isBoolean(string type)
        {
            var datatypes = new string[] {
                "bool",
                "Boolean",
            };

            return datatypes.Any(x => x.TrimToLower() == type.TrimToLower());
        }

        public string CodeToToken(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var sourceCodeLinesKind = getChildNodesTokens(syntaxNode, true);

            var lines = sourceCodeLinesKind.SelectMany(x => x).Select(x => x.Kind().ToString().Trim().RemoveBreakLine()).Where(x => !string.IsNullOrWhiteSpace(x)).Distinct();

            return string.Join(' ', lines);
        }

        public string CodeToText(string code)
        {
            var syntaxNode = generateSyntaxTree(code);

            var sourceCodeLinesKind = getChildNodesTokensToText(syntaxNode);

            var lines = sourceCodeLinesKind.Select(x => x.ToString()).ToArray();

            return string.Join(' ', lines);
        }

        private List<StringBuilder> getChildNodesTokensToText(SyntaxNode syntaxNode)
        {
            var results = new List<StringBuilder>();
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return results;
            }

            var list = syntaxNode.IsKind(SyntaxKind.Block) ? syntaxNode.ChildNodes() : syntaxNode.DescendantNodes()?.FirstOrDefault(x => x.IsKind(SyntaxKind.Block))?.ChildNodes();
            if (list == null)
            {
                results.Add(new StringBuilder(generateText(syntaxNode)));
                return results;
            }

            foreach (var node in list)
            {
                var childs = getChildNodesTokensRecursiveToText(node);
                if (childs?.Length > 0)
                {
                    results.Add(childs);
                }
            }

            if (results.Count == 0)
            {
                results.Add(new StringBuilder(syntaxNode.Kind().ToString()));
            }

            return results;
        }

        private StringBuilder getChildNodesTokensRecursiveToText(SyntaxNode syntaxNode)
        {
            var results = new StringBuilder();
            if (syntaxNode == null || syntaxNode.IsMissing)
            {
                return results;
            }

            var list = syntaxNode.ChildNodes()?.FirstOrDefault()?.ChildNodes();
            if (list == null)
            {
                results.Append($"{generateText(syntaxNode)} ");
                return results;
            }

            foreach (var node in list)
            {
                var childs = getChildNodesTokensRecursiveToText(node);
                if (childs?.Length > 0)
                {
                    results.Append(childs);
                }
                else
                {
                    results.Append(generateText(node));
                }
            }

            if (results.Length == 0)
            {
                results.Append(syntaxNode.Kind().ToString());
                results.Append(' ');
            }

            return results;
        }

        private string generateText(SyntaxNode syntaxNode)
        {
            var result = ExplainCondition(syntaxNode);
            if (string.IsNullOrWhiteSpace(result))
            {
                return syntaxNode.Kind().ToString();
            }
            return result;
        }

        public string ExplainCondition(SyntaxNode condition)
        {
            if (condition.IsKind(SyntaxKind.LogicalAndExpression))
            {
                return $"Both conditions need to be true: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.LogicalOrExpression))
            {
                return $"At least one of the conditions needs to be true: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.EqualsExpression))
            {
                return $"Check if both values are the same: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.NotEqualsExpression))
            {
                return $"Check if the values are different: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.GreaterThanExpression))
            {
                return $"Check if one value is larger than the other: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.GreaterThanOrEqualExpression))
            {
                return $"Check if one value is larger than or equal to the other: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.LessThanExpression))
            {
                return $"Check if one value is smaller than the other: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.LessThanOrEqualExpression))
            {
                return $"Check if one value is smaller than or equal to the other: {ExplainBinaryExpression((BinaryExpressionSyntax)condition)}.";
            }
            else if (condition.IsKind(SyntaxKind.ParenthesizedExpression))
            {
                var innerExplanation = ExplainCondition(((ParenthesizedExpressionSyntax)condition).Expression);
                return $"First, evaluate the expression inside the parentheses: {innerExplanation}.";
            }
            else if (condition.IsKind(SyntaxKind.LogicalNotExpression))
            {
                var innerExplanation = ExplainCondition(((PrefixUnaryExpressionSyntax)condition).Operand);
                return $"Check if the following condition is false: {innerExplanation}.";
            }
            else if (condition.IsKind(SyntaxKind.NumericLiteralExpression) ||
                     condition.IsKind(SyntaxKind.StringLiteralExpression) ||
                     condition.IsKind(SyntaxKind.TrueLiteralExpression) ||
                     condition.IsKind(SyntaxKind.FalseLiteralExpression))
            {
                return $"Use the constant value: {condition}.";
            }
            else if (condition.IsKind(SyntaxKind.IdentifierName))
            {
                return $"Use the value of the variable or method named: {((IdentifierNameSyntax)condition).Identifier.Text}.";
            }
            else if (condition.IsKind(SyntaxKind.InvocationExpression))
            {
                return $"Call the method: {((InvocationExpressionSyntax)condition).Expression}.";
            }
            else if (condition.IsKind(SyntaxKind.SimpleMemberAccessExpression))
            {
                return $"Access the member: {((MemberAccessExpressionSyntax)condition).Name.Identifier.Text}.";
            }
            else if (condition.IsKind(SyntaxKind.ConditionalExpression))
            {
                var conditionExplanation = ExplainCondition(((ConditionalExpressionSyntax)condition).Condition);
                return $"Based on whether the condition is true or false, return one of two values: {conditionExplanation}.";
            }
            else if (condition.IsKind(SyntaxKind.CastExpression))
            {
                var innerExplanation = ExplainCondition(((CastExpressionSyntax)condition).Expression);
                return $"Convert the value to the specified type and then {innerExplanation}.";
            }
            else if (condition.IsKind(SyntaxKind.TypeOfExpression))
            {
                return $"Get the type information for: {((TypeOfExpressionSyntax)condition).Type}.";
            }
            else if (condition.IsKind(SyntaxKind.ThisExpression))
            {
                return "Refer to the current instance of the class.";
            }
            else if (condition.IsKind(SyntaxKind.BaseExpression))
            {
                return "Refer to the base class of the current instance.";
            }
            else if (condition.IsKind(SyntaxKind.ElementAccessExpression))
            {
                var innerExplanation = ExplainCondition(((ElementAccessExpressionSyntax)condition).Expression);
                return $"Get an element from an array or collection using the specified index: {innerExplanation}.";
            }
            else
            {
                return $"Encountered an unhandled expression of type: {condition.Kind()}.";
            }
        }

        public string ExplainBinaryExpression(BinaryExpressionSyntax binaryExpression)
        {
            var str1 = ExplainCondition(binaryExpression.Left);
            var str2 = $"Apply the operator '{binaryExpression.OperatorToken}' to the left expression.";
            var str3 = ExplainCondition(binaryExpression.Right);
            var str4 = $"Combine the result of the left expression with the right expression using the operator '{binaryExpression.OperatorToken}'.";

            return $"{str1} {str2} {str3} {str4}";
        }

        public string[] CodeToSourceCodeStatementLines(string code)
        {
            var tree = CSharpSyntaxTree.ParseText(code);
            var root = tree.GetRoot();

            var results = new List<string>();
            ExtractStatements(root, results);

            var lines = results
                .Where(x => !string.IsNullOrWhiteSpace(x) && x.EndsWith(';'))
                .Select(NormalizeSpaces)
                .Distinct(StringComparer.Ordinal)
                .ToArray();

            return lines;
        }

        public string[] CodeToSourceCodeASTStatementLines(string function_code)
        {
            var tree = CSharpSyntaxTree.ParseText(function_code);
            var root = tree.GetRoot();

            var results = new List<string>();
            ExtractStatementsWithLabels(root, results);

            var code_lines = results
                .Where(x => !string.IsNullOrWhiteSpace(x) && x.EndsWith(';') && !x.StartsWith(" ~ ") && !x.EndsWith(" ~ "))
                .Select(NormalizeSpaces)
                .Distinct(StringComparer.Ordinal)
                .ToArray();

            return code_lines;
        }

        private void ExtractStatements(SyntaxNode node, List<string> output)
        {
            foreach (var child in node.ChildNodes())
            {
                if (child is StatementSyntax stmt)
                {
                    // Only add if it does NOT contain nested statements
                    bool hasNestedStatements = stmt.DescendantNodes()
                                                   .OfType<StatementSyntax>()
                                                   .Any();

                    if (!hasNestedStatements)
                    {
                        output.Add(Normalize(stmt.ToString()));
                    }
                }

                ExtractStatements(child, output); // Continue walk
            }
        }

        private void ExtractStatementsWithLabels(SyntaxNode node, List<string> output)
        {
            foreach (var child in node.ChildNodes())
            {
                if (child is StatementSyntax stmt)
                {
                    // Only add if it does NOT contain nested statements
                    bool hasNestedStatements = stmt.DescendantNodes()
                                                   .OfType<StatementSyntax>()
                                                   .Any();

                    if (!hasNestedStatements)
                    {
                        var kinds = CollectAstKindsExcludingParent(stmt);
                        var label = string.Join(" ", kinds.Distinct());
                        output.Add($"{label} ~ {Normalize(stmt.ToString())}");
                    }
                }

                ExtractStatementsWithLabels(child, output);
            }
        }

        private List<string> CollectAstKindsExcludingParent(SyntaxNode statement)
        {
            var ignoreKinds = new HashSet<SyntaxKind>
            {
                SyntaxKind.Block,
                SyntaxKind.CompilationUnit,
                SyntaxKind.GlobalStatement,
                SyntaxKind.UsingDirective,
                SyntaxKind.QualifiedName,
                SyntaxKind.Parameter,
                SyntaxKind.ParameterList,
                SyntaxKind.VariableDeclarator,
                SyntaxKind.EmptyStatement,
            };

            var kinds = new List<string>();

            // Only visit children, not the statement node itself
            foreach (var child in statement.ChildNodes())
            {
                foreach (var descendant in child.DescendantNodesAndSelf())
                {
                    var kind = descendant.Kind();
                    if (!ignoreKinds.Contains(kind))
                    {
                        kinds.Add(kind.ToString());
                    }
                }
            }

            return kinds;
        }

        private string Normalize(string input)
        {
            return Regex.Replace(input, @"\s+", " ").Trim();
        }

        private string NormalizeSpaces(string input)
        {
            // Replace all whitespace types with a single space
            string simplified = Regex.Replace(input, @"\s+", " ");

            // Normalize Unicode (e.g., NFC)
            simplified = simplified.Normalize(NormalizationForm.FormC);

            // Trim and remove non-visible characters (e.g., zero-width space, NBSP)
            simplified = new string(simplified
                .Where(c => !char.IsControl(c) && c != '\u200B' && c != '\u00A0')
                .ToArray());

            return simplified.Trim();
        }

    }
}
