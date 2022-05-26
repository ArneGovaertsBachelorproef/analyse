Doel: model bouwen voor alle tekstgebaseerde eigenschappen samen

<https://spacy.io/usage/training>
<https://medium.com/analytics-vidhya/nlp-tutorial-for-text-classification-in-python-8f19cd17b49e>
<https://towardsdatascience.com/machine-learning-nlp-text-classification-using-scikit-learn-python-and-nltk-c52b92a7c73a>
<https://medium.com/analytics-vidhya/building-a-text-classifier-with-spacy-3-0-dd16e9979a>

<https://medium.com/activewizards-machine-learning-company/comparison-of-top-6-python-nlp-libraries-c4ce160237eb>

```
python -m spacy init fill-config base_config.cfg config.cfg
python preprocess1.py
python -m spacy train config.cfg --output ./output --paths.train ./train.spacy --paths.dev ./train.spacy
python -m spacy evaluate output/model-best train.spacy
python classify.py
```