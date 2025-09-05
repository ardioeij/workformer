using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public static class Extensions
    {
        public static string TrimToLower(this string szText)
        {
            return szText.Trim().ToLower();
        }

        public static string RemoveBreakLine(this string text)
        {
            return string.IsNullOrWhiteSpace(text) ? ""
                : text.Replace("\r", "").Replace("\n", "").Replace(Environment.NewLine, "");
        }

        public static string RemoveSpecialCharacters(this string str, string allowedChars, string replacement)
        {
            return string.IsNullOrEmpty(str)
                ? string.Empty
                : Regex.Replace(str, "[^a-zA-Z0-9" + allowedChars + "]+", replacement, RegexOptions.Compiled);
        }

        public static string ToTitleCase(this string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return "";

            if (text.Length <= 1)
            {
                return text.Trim().ToUpper();
            }

            text = string.IsNullOrWhiteSpace(text)
                ? string.Empty
                : (text.Split(new[] { " " }, StringSplitOptions.None)
                    .Where(x => x.Length > 1)
                    .Select(s => char.ToUpperInvariant(s[0]) + s[1..])
                    .Aggregate(" ", (s1, s2) => s1 + " " + s2)).Trim();

            return text;
        }

        public static string LowerCaseFirstChar(this string text)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return text;
            }

            if (text.Length <= 1)
            {
                return text.Trim().ToLower();
            }

            return text[0].ToString().ToLower() + text.Substring(1);
        }

        public static string UpperCaseFirstChar(this string text)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return text;
            }

            if (text.Length <= 1)
            {
                return text.Trim().ToUpper();
            }

            return text[0].ToString().ToUpper() + text.Substring(1);
        }

        public static string RemoveIfStartsWith(this string text, string chrstr)
        {
            foreach (char chr in chrstr)
            {
                text = text.StartsWith(chr) && text.Length > 0 ? text.Substring(1) : text;
            }
            return text;
        }

        public static string RemoveIfEndsWith(this string text, string chrstr)
        {
            foreach (char chr in chrstr)
            {
                text = text.EndsWith(chr) && text.Length > 0 ? text.Substring(0, text.Length - 1) : text;
            }
            return text;
        }


    }
}
