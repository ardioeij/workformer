from io import StringIO
import os
import pathlib
import re
import sys
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import tensorflow as tf

import tensorflow_text as text
import faiss
import numpy as np
import csv
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize


reserved_tokens=["[PAD]", "[UNK]", "[START]", "[END]"]

START = tf.argmax(tf.constant(reserved_tokens) == "[START]")
END = tf.argmax(tf.constant(reserved_tokens) == "[END]")

MAX_TOKENS = 128


def to_csv(rows, output_file):
    with open(output_file, 'a', encoding='utf8') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        wr.writerows(rows)
            

def progress(current, total, desc):
    sys.stdout.write('\r')
    sys.stdout.write(str(current) + ' / ' + str(total) + ' ' + desc)
    sys.stdout.flush()  


class SourceCodeClusterization:

    def __init__(self, vocab_path, max_tokens, inputFiles, indexFile):
        self.tokenizer = text.BertTokenizer(vocab_path, lower_case=True, split_unknown_characters=True, preserve_unused_token=True)
        self._reserved_tokens = reserved_tokens
        self._vocab_path = tf.saved_model.Asset(vocab_path)
        vocab = pathlib.Path(vocab_path).read_text(encoding='utf-8').splitlines()
        self.vocab = tf.Variable(vocab)
        self.input_files = inputFiles
        self.index_file = indexFile
        self.embedding_layer = tf.keras.layers.Embedding(len(vocab) + len(reserved_tokens), max_tokens)


    def add_start_end(self, ragged):
        count = ragged.bounding_shape()[0]
        starts = tf.fill([count,1], START)
        ends = tf.fill([count,1], END)
        return tf.concat([starts, ragged, ends], axis=1)


    def pad_array(self, arr, max_length, padding_value=0):
        """
        Pads the array to the maximum length.

        Args:
            arr (list or np.ndarray): The array to be padded.
            max_length (int): The maximum length of the array after padding.
            padding_value (int, optional): The value to use for padding. Default is 0.

        Returns:
            np.ndarray: The padded array.
        """
        arr = np.array(arr)
        if len(arr) >= max_length:
            return arr[:max_length]
        else:
            padding = np.full((max_length - len(arr),), padding_value)
            return np.concatenate((arr, padding))
    

    def cleanup_text(self, reserved_tokens, token_txt):
        # Drop the reserved tokens, except for "[UNK]".
        bad_tokens = [re.escape(tok) for tok in reserved_tokens if tok != "[UNK]"]
        bad_token_re = "|".join(bad_tokens)

        bad_cells = tf.strings.regex_full_match(token_txt, bad_token_re)
        result = tf.ragged.boolean_mask(token_txt, ~bad_cells)

        # Join them into strings.
        result = tf.strings.reduce_join(result, separator=' ', axis=-1)

        return result


    def prepare_data(self, max_tokens):

        chunk_emb = []

        for inputFile in self.input_files:

            with open(inputFile, 'r', encoding='utf8') as f:
                text = f.read()

            lines = text.splitlines()

            count = len(lines)

            print()
            for i in range(0, count, 1):
                line = lines[i]
                enc = self.tokenizer.tokenize(line)
                # Merge the `word` and `word-piece` axes.
                enc = enc.merge_dims(-2,-1)
                enc = self.add_start_end(enc)

                enc = enc[:, :max_tokens]    # type: ignore # Trim to MAX_TOKENS.
                enc = enc.to_tensor().numpy()[0]  # Convert to 0-padded dense Tensor
                
                enc = self.pad_array(enc, max_tokens)

                chunk_emb.append(enc)

                progress(i, count, 'File ' + inputFile + ' : ')

        return chunk_emb


    def do_clustering(self, chunk_emb, max_clusters):

        kmeans = faiss.Kmeans(d=MAX_TOKENS, k=max_clusters, verbose=True)

        if os.path.isfile(self.index_file):
            print('Loading Index File')
            kmeans.index = faiss.read_index(self.index_file)
        else:
            print('Creating new index')

        kmeans.train(chunk_emb)

        faiss.write_index(kmeans.index, self.index_file)

        centroids = kmeans.centroids
        print('Centroid = ' + str(len(centroids))) # type: ignore


    def to_csv(self, num_features, num_clusters, input_files, output_file):

        clusters_count = {}
        for cluster in range(0, num_clusters, 1):
            clusters_count[cluster] = 0

        clusters = []

        kmeans = faiss.Kmeans(d=num_features, k=num_clusters, verbose=True)
        if os.path.isfile(self.index_file):
            kmeans.index = faiss.read_index(self.index_file)
        else:
            print('Index file not found')

        with open(output_file, 'w', encoding='utf8') as csvfile:

            wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
            wr.writerow(['TokenCode', 'Cluster', 'Distance'])
            for inputFile in input_files:
                i=0
                with open(inputFile, 'r', encoding='utf8') as f:
                    text = f.read()

                lines = text.splitlines()

                for line in lines:
                    D, I = self.search(line, num_features, num_clusters, kmeans)

                    cluster_number = int(I[0][0])
                    proc = 'PROC' + str(cluster_number).zfill(4)
                    distance = float(D[0][0])

                    row = [str(line), str(proc), f"{float(distance):.4f}"] 
                    wr.writerow(row)

                    clusters.append([float(D[0][0]), float(I[0][0])])

                    clusters_count[cluster_number] = int(clusters_count[cluster_number]) + 1

                    progress(i, len(lines), 'To CSV File ' + inputFile + ' : ')
                    
                    i = i + 1
        
        cluster_sizes = np.array(list(clusters_count.values()))  # Convert values to a list before passing to np.array
        max = np.max(cluster_sizes)
        min = np.min(cluster_sizes)
        if (min == 0):
            min = 1

        clusters = clusters / np.linalg.norm(clusters) # type: ignore

        return clusters, int(max), int(min), clusters_count
    

    def search(self, text, num_features, num_clusters, kmeans=None):

        if kmeans == None :
            kmeans = faiss.Kmeans(d=num_features, k=num_clusters, verbose=True)
            if os.path.isfile(self.index_file):
                kmeans.index = faiss.read_index(self.index_file)
            else:
                print('Index file not found')

        enc = self.tokenizer.tokenize(text)
        enc = enc.merge_dims(-2,-1)
        enc = self.add_start_end(enc)

        enc = enc[:, :num_features]    # type: ignore # Trim to MAX_TOKENS.
        enc = enc.to_tensor().numpy()  # Convert to 0-padded dense Tensor
        
        arr = self.pad_array(enc[0], num_features)

        enc = tf.constant([arr])

        D, I = kmeans.index.search(enc, 1) # type: ignore

        return D, I


    def to_graph(self, num_features, num_clusters, inputFile):

        kmeans = faiss.Kmeans(d=num_features, k=num_clusters, verbose=True)
        if os.path.isfile(self.index_file):
            kmeans.index = faiss.read_index(self.index_file)
        else:
            print('Index file not found')
        
        results = []

        with open(inputFile, 'r', encoding='utf8') as f:
            text = f.read()

            lines = text.splitlines()

            for line in lines:

                D, I = self.search(line, num_features, num_clusters, kmeans)

                results.append((D[0][0], I[0][0]))

        
        self.plot_clusters(results) # type: ignore


    def plot_clusters(self, results, title, xlabel, ylabel):
        # Separate distances and indices
        distances = np.array([res[0] for res in results])
        indices = np.array([res[1] for res in results])

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(indices, distances, c=distances, cmap='rainbow', alpha=0.6)
        plt.title('FAISS KMeans Clustering Results')
        plt.xlabel('Cluster Index')
        plt.ylabel('Distance to Nearest Cluster')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.colorbar(scatter)
        plt.grid(True)
        plt.savefig('data/clusters/normalized01' + title + '.png')
        plt.close()
        #plt.show(block=False)
        

    def read_csv(self, inputFile, d_index, i_index):

        clusters=[]
        i = 0
        with open(inputFile, 'r', encoding='utf8') as csvfile:

            csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
            for row in csv_reader:
                d = float(row[i_index])
                i = float(str(row[d_index]).replace('PROC', ''))
                clusters.append([d, i])

                progress(i, 0, 'csv_to_graph Read File ' + inputFile + ' : ')
                i = i + 1

        clusters = clusters / np.linalg.norm(clusters) # type: ignore

        return clusters



def calculate_silhouette_score(clusters, number_of_cluster):
    """ Apply KMeans clustering and calculate silhouette score for each K. """

    print("Predicting:", number_of_cluster)

    kmeans = KMeans(n_clusters=number_of_cluster)
    cluster_labels = kmeans.fit_predict(clusters)
    
    # Calculate silhouette score for each K
    score = silhouette_score(clusters, cluster_labels)
    print(f"Silhouette Score: {score} {number_of_cluster}")

    return score


def cluster_to_csv(base_path, num_clusters, inputFiles, fileNamePrefix, list_to_clusters):

    clusterIndexFile = base_path + fileNamePrefix + str(num_clusters).zfill(4) + '.index'
    clusterCsvFile = base_path + fileNamePrefix + str(num_clusters).zfill(4) + '.csv'
    cluster = SourceCodeClusterization('data/uswf/code_token_vocab.txt', MAX_TOKENS, inputFiles, clusterIndexFile)

    if (os.path.isfile(clusterIndexFile) == False):
        cluster.do_clustering(list_to_clusters, num_clusters)
    
    clusters, max, min, clusters_count = cluster.to_csv(MAX_TOKENS, num_clusters, inputFiles, clusterCsvFile)
    
    clusters_list = [[ str('PROC' + str(key).zfill(4)), int(value)] for key, value in clusters_count.items()]
    clusters_list.insert(0, ['Cluster', 'Count'])
    clusterCountCsvFile = base_path + fileNamePrefix + str(num_clusters).zfill(4) + '_count.csv'
    to_csv(clusters_list, clusterCountCsvFile)

    return clusters, max, min


def generate_clusters_csv_token_code(start, end, increment):
    summaries = []
    summaries.append(['Clusters', 'Silhouette', 'Imbalance', 'Objective', 'Max', 'Min' ])
    inputFiles = [
        'clusters/token_code_lines_0500k.txt',
    ]
    prefix = 'token_code_desc_'
    base_path = 'clusters/'
    tempClusterIndexFile = base_path + 'initial.index'
    cluster = SourceCodeClusterization('data/uswf/code_token_vocab.txt', MAX_TOKENS, inputFiles, tempClusterIndexFile)
    list_to_clusters = cluster.prepare_data(MAX_TOKENS)

    for i in range(start, (end + 1), increment):
        
        filetitle = prefix + str(i).zfill(4)
        print('Clustering Token Code Desc:', filetitle)
        clusters, max, min = cluster_to_csv(base_path, i, inputFiles, prefix, list_to_clusters)
        
        print('Calculate Silhouette Scores:', filetitle)
        silhouette_score = calculate_silhouette_score(clusters, i)

        row = [i, f"{float(silhouette_score):.8f}",  0, 0, max, min]
        summaries.append(row)
        
        csv_summary_file_name = base_path + 'token_code_summary_0256_1024.csv'
        print(row)
        
        to_csv(summaries, csv_summary_file_name)

        summaries = []


if __name__ == '__main__':

    print()
    
    generate_clusters_csv_token_code(256, 1024, 128)
