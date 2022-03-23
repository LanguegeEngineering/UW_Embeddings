# -*- coding: utf-8 -*-
"""Word2Vec

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LUllcaYhGQhZO9V43RYN2emyzIz2UxCJ

## Moduły
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

torch.manual_seed(1)

"""## Przykład losowych wektorow"""

word_to_ix = {"hello": 0, "world": 1}
embeds = nn.Embedding(2, 5)  # 2 words in vocab, 5 dimensional embeddings
lookup_tensor = torch.tensor([word_to_ix["hello"]], dtype=torch.long)
hello_embed = embeds(lookup_tensor)
print(hello_embed)

"""## Tworzenie wektorow dla krotkiego tekstu"""

def make_context_vector(context, word_to_id):
    """
    Stworzenie tensora z indeksami dla calego kontekstu
    """
    idxs = [word_to_id[w] for w in context]
    return torch.tensor(idxs, dtype=torch.long)

def get_index_of_max(input):
    index = 0
    for i in range(1, len(input)):
        if input[i] > input[index]:
            index = i
    return index

def get_max_prob_result(input, id_to_word):
    return id_to_word[get_index_of_max(input)]

CONTEXT_SIZE = 2  # 2 words to the left, 2 to the right
EMDEDDING_DIM = 100

word_to_id = {}
id_to_word = {}

raw_text = """We are about to study the idea of a computational process.
Computational processes are abstract beings that inhabit computers.
As they evolve, processes manipulate other abstract things called data.
The evolution of a process is directed by a pattern of rules
called a program. People create programs to direct processes. In effect,
we conjure the spirits of the computer with our spells.""".split()

vocab = set(raw_text)
vocab_size = len(vocab)
print(vocab)
print(len(vocab))

for i, word in enumerate(vocab):
    word_to_id[word] = i
    id_to_word[i] = word

data = []
for i in range(2, len(raw_text) - 2):
    context = [raw_text[i - 2], raw_text[i - 1],
               raw_text[i + 1], raw_text[i + 2]]
    target = raw_text[i]
    data.append((context, target))

print(data[:5])

class CBOW(torch.nn.Module):

    def __init__(self, vocab_size, embedding_dim):
        super(CBOW, self).__init__()

        #out: 1 x emdedding_dim
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)

        self.linear1 = nn.Linear(embedding_dim, 128)

        self.activation_function1 = nn.ReLU()
        
        #out: 1 x vocab_size
        self.linear2 = nn.Linear(128, vocab_size)

        self.activation_function2 = nn.LogSoftmax(dim = -1)
        

    def forward(self, inputs):
        embeds = sum(self.embeddings(inputs)).view(1,-1)
        out = self.linear1(embeds)
        out = self.activation_function1(out)
        out = self.linear2(out)
        out = self.activation_function2(out)
        return out

    def get_word_emdedding(self, word):
        word = torch.LongTensor([word_to_id[word]])
        return self.embeddings(word).view(1,-1)

model = CBOW(vocab_size, EMDEDDING_DIM)

loss_function = nn.NLLLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

loss_list = []

for epoch in range(3):
    total_loss = 0
    for context, target in data:
        context_vector = make_context_vector(context, word_to_id) 
        #print(context_vector)
        #print(word_to_id[target])
        model.zero_grad()
        log_probs = model(context_vector)
        #print(log_probs)
        loss = loss_function(log_probs, torch.tensor([word_to_id[target]], dtype=torch.long))
        loss.backward()
        optimizer.step()
        

        total_loss += loss.data
    loss_list.append(total_loss)

# TEST
context = ['about', 'process', 'inhabit', 'directed']
context_vector = make_context_vector(context, word_to_id)
result = model(context_vector).data.numpy()
print('Raw text: {}\n'.format(' '.join(raw_text)))
print('Context: {}\n'.format(context))
print('Prediction: {}'.format(get_max_prob_result(result[0], id_to_word)))

"""### Zadania

1. Wyrysować wykresy straty, pobawić się parametrami
2. Zmienić dane tekstowe na polski

"""

