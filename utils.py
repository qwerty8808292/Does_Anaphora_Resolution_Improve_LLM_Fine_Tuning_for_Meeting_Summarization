import spacy

## Filter it in phase 2 (Paice & Husk, 1987)
def filter_it(token):
    TASK_STATUS_WORDS = {
        "abnormal", "advantageous", "advisable", "appropriate", "bad", "beneficial", "best", "better", "common", "correct", "customary", "dangerous", "decided",
        "difficult", "easier", "easiest", "easy", "essential", "faster", "feasible", "fitting", "foolish", "good", "hard", "harder", "hardest", "helpful",
        "importance", "important", "impossibility", "impossible", "impracticable", "inadvisable", "inappropriate", "incorrect", "incumbent", "infeasible",
        "intended", "interest", "interesting", "irrelevant", "job", "justified", "necessary", "normal", "obligatory", "policy", "possible", "practicable",
        "practice", "preferred", "rare", "rarer", "rarest", "reasonable", "relevant", "remains", "right", "safe", "safer", "safest", "sensible", "shock",
        "simple", "simpler", "simplest", "sufficient", "tempting", "traditional", "trivial", "uncommon", "unhelpful", "unnecessary", "unreasonable", "unsafe",
        "unscientific", "unusual", "unwise", "useful", "useless", "usual", "wise", "wiser", "wisest", "worthwhile", "wrong"
    }
    PREPOSITIONS = {
        "among", "at", "before", "below", "beneath", "beside", "between", "by", "despite", "during", "from", "in", "inside", "into", "near", "of", "off",
        "on", "onto", "outside", "over", "through", "to", "under", "until", "via", "with", "within", "without"
    }
    STATE_OF_KNOWLEDGE_WORDS = {
        "certain", "debatable", "known", "questionable", "uncertain", "wondered", "clear", "doubted", "doubtful", "dubious", "questioned", "unclear",
        "understood", "unknown"
    }
    IDIOMS = {
        "on the face of it", "if it wasn't for", "as it were", "as we know it", "it remains to", "i think it was", "it is important to",
        "it is necessary to", "it seems that", "it appears that", "it happens that", "it remains to be seen", "as it turms out",
        "if it weren't for", "if it were not for", "it is raining", "it is snowing", "it is sunny", "it is cloudy", "it is windy"
    }

    next_tokens = list(token.doc[token.i+1:])

    # it + be + that
    if next_tokens:
        if next_tokens[0].lemma_ == "be":
            for t in next_tokens[1:]:
                if t.text.lower() == "that":
                    if t.i > 0 and token.doc[t.i - 1].lemma_ in PREPOSITIONS:
                        continue
                    return True

    # it + be + to
    if next_tokens:
        if next_tokens[0].lemma_ == "be":
            for t in next_tokens[1:]:
                if t.text.lower() == "to":
                    if next_tokens[1].pos_ == "ADJ" and next_tokens[1].lemma_.lower() in TASK_STATUS_WORDS:
                        return True
                    return True

    # it + be + adj + to/that
    if len(next_tokens) >= 2 and next_tokens[0].lemma_ == "be" and next_tokens[1].pos_ == "ADJ":
        adj = next_tokens[1]
        if adj.lemma_.lower() in TASK_STATUS_WORDS:
            for t in next_tokens[2:]:
                if t.text.lower() in {"to", "that"}:
                    return True

    # it + be + state-of-knowledge + whether/if
    if next_tokens:
        if next_tokens[0].lemma_ == "be":
            for i, t in enumerate(next_tokens[1:], start=1):
                if t.text.lower() in {"whether", "if"}:
                    if any(nt.lemma_.lower() in STATE_OF_KNOWLEDGE_WORDS for nt in next_tokens[1:i]):
                        return True

    # idioms
    span_text = " ".join(t.text.lower() for t in [token] + next_tokens[:5])
    for idiom in IDIOMS:
        if idiom in span_text:
            return True

    # parenthetical it
    if token.i > 0 and token.nbor(-1).text == ",":
        if any(t.text == "," for t in next_tokens[:5]):
            return True

    return False


## Functions in phase 3
# Agree with the pronoun with respect to number
def number_filter(pronoun, np_head):
    pronoun_number = pronoun.morph.get("Number")
    np_number = np_head.morph.get("Number")
    if not pronoun_number or not np_number:
        return False
    return pronoun_number == np_number

#  Syntactic filter
def syntactic_filter(pronoun, np_chunk):
    # A pronoun cannot refer with a co-argument
    if np_chunk.root.head == pronoun.head:
        return False
    # A pronoun cannot corefer with a non-pronominal constituent which it both commands and precedes
    if np_chunk.start < pronoun.i and np_chunk.root.head == pronoun.head:
        return False
    # A pronoun cannot corefer with a constituent which contains it
    if np_chunk.start <= pronoun.i <= np_chunk.end:
        return False
    return True

# Find all possible spans in a chunk
def sub_span(doc, chunk):
    spans = []
    tokens = [token for token in chunk if token.pos_ in {"ADJ", "NOUN", "PROPN"}]
    for i in range(len(tokens)):
        for j in range(i, len(tokens)):
            sub_tokens = tokens[i:j+1]
            if sub_tokens:
                start = sub_tokens[0].i
                end = sub_tokens[-1].i + 1
                span = doc[start:end]
                spans.append(span)
    return spans


## Find the most frequent noun phrases (for term preference in phase 4)
def top_np(np_frequencies, top_n=10):
    return set(sorted(np_frequencies, key=np_frequencies.get, reverse=True)[:top_n])


