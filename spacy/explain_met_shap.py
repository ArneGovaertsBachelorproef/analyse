import spacy, shap

nlp = spacy.load('output/model-best')
tokenizer_spacy = spacy.tokenizer.Tokenizer(nlp.vocab)

# Run the spacy pipeline on some random text just to retrieve the classes
doc = nlp('hey')
classes = list(doc.cats.keys())

# Define a function to predict
def predict(texts):
    # convert texts to bare strings
    texts = [str(text) for text in texts]
    results = []
    for doc in nlp.pipe(texts):
        # results.append([{'label': cat, 'score': doc.cats[cat]} for cat in doc.cats])
        results.append([ doc.cats[cat] for cat in classes ])
    return results

# Create a function to create a transformers-like tokenizer to match shap's expectations
def tok_adapter(text, return_offsets_mapping=False):
    doc = tokenizer_spacy(text)
    out = {"input_ids": [tok.norm for tok in doc]}
    if return_offsets_mapping:
        out["offset_mapping"] = [(tok.idx, tok.idx + len(tok)) for tok in doc]
    return out

# Create the Shap Explainer
# - predict is the "model" function, adapted to a transformers-like model
# - masker is the masker used by shap, which relies on a transformers-like tokenizer
# - algorithm is set to permuation, which is the one used for transformers models
# - output_names are the classes (altough it is not propagated to the permutation explainer currently, which is why plots do not have the labels)
# - max_evals is set to a high number to reduce the probability of cases where the explainer fails because there are too many tokens
explainer = shap.Explainer(
    predict,
    masker=shap.maskers.Text(tok_adapter),
    algorithm="permutation",
    output_names=classes,
    max_evals=1500
)

sample = '''Dag oma, kan je morgen met ons mee naar de zee? We komen je halen met de auto vertrekken om 9 uur.
Vergeet je zwempak niet mee te nemen want we gaan samen zwemmen in het zwembad van Oostende.
Natuurlijk gaan we ook iets lekkers eten en een lekkere koffie gaan drinken.'''

# Process the text using SpaCy
doc = nlp(sample)

# Get the shap values
shap_values = explainer([sample])
shap.text_plot(shap_values)