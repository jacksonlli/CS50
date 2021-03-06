import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_dict = {}
    for file in os.listdir(directory):
        with open(os.path.join(directory, file), encoding="utf8") as f:
            file_dict[file] = f.read()
    return file_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    raw_words = nltk.word_tokenize(document)
    processed_words = []
    for word in raw_words:
        if word.isalpha() and not word in string.punctuation and word not in nltk.corpus.stopwords.words("english"):
            processed_words.append(word.lower())
    return processed_words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idf_dict = {}
    for doc in documents:
        words = documents[doc]
        for word in words:
            if not word in idf_dict:
                doc_frequency = 0
                for doc in documents:
                    if word in documents[doc]:
                        doc_frequency += 1
                idf_dict[word] = math.log((len(documents)+1)/(doc_frequency+1))+1
    return idf_dict


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idf_dict = {}
    for file in files:
        words = files[file]
        tf_idf = 0
        for word in query:
            if word in idfs:
                tf = words.count(word)
                tf_idf += tf*idfs[word]
        tf_idf_dict[file] = tf_idf
    tf_idf_list = [i[0] for i in sorted(tf_idf_dict.items(), key=lambda x:x[1], reverse = True)]
    return tf_idf_list[:n]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    top_sentences = []
    for sentence in sentences:
        sentence_words = sentences[sentence]
        matching_word_measure = 0
        query_term_density = 0
        for query_word in query:
            if query_word in sentence_words:
                matching_word_measure += idfs[query_word]
                query_term_density += 1/len(sentence_words)
        top_sentences.append((matching_word_measure, query_term_density, sentence))
    top_sentences = [i[2] for i in sorted(top_sentences, reverse = True)]
    return top_sentences[:n]


if __name__ == "__main__":
    main()
