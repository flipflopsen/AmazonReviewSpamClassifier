from enum import Enum


class NlpTraining(Enum):
    SpamBatchSize = 500_000
    HamBatchSize = 500_000
    Iterations = 10
    TfidfFeatureSize = 50000
    TestSize = 0.2
    CreateVectorizer = True
    SaveVocabulary = True
    LoadVocabulary = False


class NlpPrediction(Enum):
    BatchSize = 1_000_000
    Iterations = 10


class AnnParameters(Enum):
    FirstHiddenSize = 64
    SecondHiddenSize = 64
    ThirdHiddenSize = 32
    ReLu = 'relu'
    Optimizer = 'adam'


class AnnTraining(Enum):
    ChunkSizeSpam = 420_000
    ChunkSizeHam = 420_000
    Iterations = 10
    Epochs = 10
    BatchSize = 400000


class AnnPrediction(Enum):
    ChunkSize = 420_000
    Iterations = 10
