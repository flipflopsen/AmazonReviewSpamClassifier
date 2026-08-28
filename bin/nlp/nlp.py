from bin.nlp.classifiers import nlp_classifiers as nlp


def create_and_train():
    nlp.train_nb()
    nlp.save_model()
    print('Training is done!')
    nlp.load_model()
    nlp.measure_accuracy()


def predict():
    print('Starting to make predictions..')
    nlp.load_model()
    nlp.predict()


if __name__ == '__main__':
    create_and_train()
    predict()