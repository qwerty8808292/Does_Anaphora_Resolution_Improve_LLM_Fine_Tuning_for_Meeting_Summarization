import spacy

def obliqueness(chunk):
    dependency = chunk.root.dep_.lower()
    if dependency in {"nsubj", "nsubjpass"}:  
        return 2
    elif dependency in {"dobj", "obj"}:       
        return 1
    elif dependency in {"iobj"}:               
        return 0
    else:
        return -1

def indicating_verb(chunk):
    INDICATING_VERBS = {
        "analyze", "assess", "check", "consider", "cover", "define", "describe", "develop", "discuss", "examine", "explore", "highlight", "identify",
        "illustrate", "investigate", "outline", "present", "report", "review", "show", "study", "summarize", "survey", "synthesise"
    }
    head_verb = chunk.root.head
    if head_verb.pos_ == "VERB" and head_verb.lemma_.lower() in INDICATING_VERBS:
        return 1
    return 0

def lexical_reiteration(anaphor, chunk):
    candidate_lemma = chunk.root.lemma_.lower()
    freq = 0
    for np in anaphor.doc.noun_chunks:
        if np.root.lemma_.lower() == candidate_lemma:
            freq += 1
    freq -= 1  
    if freq >= 2:
        return 2
    elif freq == 1:
        return 1
    else:
        return 0

def section_heading_match(chunk):
    return 0

def collocation_match(anaphor, chunk):
    verb1 = chunk.root.head
    verb2 = anaphor.head
    if verb1.pos_ in {"VERB", "AUX"} and verb2.pos_ in {"VERB", "AUX"}:
        if verb1.lemma_.lower() == verb2.lemma_.lower():
            return 2
    return 0

def immediate_reference(anaphor, chunk):
    if anaphor.sent != chunk.root.sent:
        return 0
    verb1 = chunk.root.head
    verb2 = anaphor.head
    if verb1.pos_ != "VERB" or verb2.pos_ != "VERB":
        return 0
    conjunctions = {"and", "or", "before", "after", "until"}
    for token in verb1.children:
        if token.dep_ == "cc" and token.text.lower() in conjunctions:
            for sibling in verb1.conjuncts:
                if sibling == verb2:
                    return 2
    return 0

def sequential_instruction(anaphor, chunk):
    chunk_sentence = chunk.root.sent
    anaphor_sentence = anaphor.sent
    if chunk_sentence.start >= anaphor_sentence.start:
        return 0
    tokens = list(chunk_sentence)
    if len(tokens) < 2:
        return 0
    if tokens[0].text.lower() != "to" or tokens[1].pos_ != "VERB":
        return 0
    if anaphor.head.pos_ != "VERB":
        return 0
    sentence_list = list(anaphor.doc.sents)
    chunk_idx = sentence_list.index(chunk_sentence)
    anaphor_idx = sentence_list.index(anaphor_sentence)
    if anaphor_idx - chunk_idx > 2:
        return 0
    return 2

def term_preference(chunk, top_terms):
    lemma = chunk.root.lemma_.lower()
    if lemma in top_terms:
        return 1  
    return 0

def indefiniteness_penalty(chunk):
    for token in chunk:
        if token.dep_ == "det" and token.lower_ in {"a", "an"}:
            return -1
    return 0

def prepositional_np_penalty(chunk):
    if chunk.root.dep_ == "pobj":
        return -1
    return 0

def referential_distance(anaphor, chunk):
    anaphor_sentence_idx = list(anaphor.doc.sents).index(anaphor.sent)
    chunk_sentence_idx = list(chunk.root.doc.sents).index(chunk.root.sent)
    distance = anaphor_sentence_idx - chunk_sentence_idx
    if distance == 0:
        return 2
    elif distance == 1:
        return 1
    elif distance == 2:
        return 0
    else:
        return -1

def boost_pronoun(chunk):
    return 0

def syntactic_parallelism(anaphor, chunk):
    if anaphor.dep_ == chunk.root.dep_:
        return 1
    return 0

def frequent_candidate(chunk, np_frequencies):
    lemma = chunk.root.lemma_.lower()
    freq = np_frequencies.get(lemma, 0)
    if freq >= 5:
        return 2
    elif freq >= 2:
        return 1
    else:
        return 0


