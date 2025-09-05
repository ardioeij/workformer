using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace workflowtransformer.dataset.collector
{
    public static class StreamReaderExtensions
    {
        public static IEnumerable<string> EnumerateLines(this StreamReader reader)
        {
            while (!reader.EndOfStream)
            {
                yield return reader.ReadLine();
            }
        }

    }
}
