import spacy
from utils import filter_it, number_filter, syntactic_filter, sub_span, top_np
from indicator import (
    obliqueness, 
    indicating_verb, 
    lexical_reiteration, 
    section_heading_match,
    collocation_match, 
    immediate_reference,
    sequential_instruction,
    term_preference,
    indefiniteness_penalty,
    prepositional_np_penalty,
    referential_distance,
    boost_pronoun,
    syntactic_parallelism,
    frequent_candidate
)


class MARS:
    def __init__(self, model="en_core_web_lg"):
        self.nlp = spacy.load(model)
    
    # Phase 1
    def phase_1(self, text):
        self.doc = self.nlp(text)
        self.sentences = list(self.doc.sents)
        self.np_frequencies = {}
        for chunk in self.doc.noun_chunks:
            lemma = chunk.root.lemma_.lower()
            self.np_frequencies[lemma] = self.np_frequencies.get(lemma, 0) + 1
    
    # Phase 2
    def phase_2(self):
        PRONOUNS = {"he", "she", "it", "they", "him", "her", "them", "his", "hers", "its", "their", "theirs"}
        self.anaphors = []
        for i, sentence in enumerate(self.sentences):
            for token in sentence:
                lower = token.text.lower()
                if lower in PRONOUNS and token.pos_ == "PRON":
                    if lower == "it" and filter_it(token):
                        continue
                    self.anaphors.append((i, token))
    
    # Phase 3
    def phase_3(self):
        self.candidates = {}
        for anaphor_idx, anaphor_token in self.anaphors:
            candidate_list = []
            sentences = self.sentences[max(0, anaphor_idx-2):anaphor_idx+1]
            for sentence in sentences:
                for chunk in sentence.noun_chunks:
                    if chunk.root.pos_ == "PRON":
                        continue
                    if chunk.start <= anaphor_token.i <= chunk.end:
                        continue
                    if number_filter(anaphor_token, chunk.root) and syntactic_filter(anaphor_token, chunk):
                        candidate_list.append(chunk)
                    sub_spans = sub_span(self.doc, chunk)
                    for span in sub_spans:
                        if number_filter(anaphor_token, span.root) and syntactic_filter(anaphor_token, span):
                            candidate_list.append(span)
            self.candidates[anaphor_token] = candidate_list
    
    # Phase 4
    def phase_4(self, print_=False):
        top_terms = top_np(self.np_frequencies)
        self.all_candidate_scores = {}
        for anaphor_token, candidate_list in self.candidates.items():
            candidate_scores = [] 
            for chunk in candidate_list:
                indicators = {}  
                indicators["obliqueness"] = obliqueness(chunk)
                indicators["indicating_verb"] = indicating_verb(chunk)
                indicators["lexical_reiteration"] = lexical_reiteration(anaphor_token, chunk)
                indicators["section_heading_match"] = section_heading_match(chunk)
                indicators["collocation_match"] = collocation_match(anaphor_token, chunk)
                indicators["immediate_reference"] = immediate_reference(anaphor_token, chunk)
                indicators["sequential_instruction"] = sequential_instruction(anaphor_token, chunk)
                indicators["term_preference"] = term_preference(chunk, top_terms)
                indicators["indefiniteness_penalty"] = indefiniteness_penalty(chunk)
                indicators["prepositional_np_penalty"] = prepositional_np_penalty(chunk)
                indicators["referential_distance"] = referential_distance(anaphor_token, chunk)
                indicators["boost_pronoun"] = boost_pronoun(chunk)
                indicators["syntactic_parallelism"] = syntactic_parallelism(anaphor_token, chunk)
                indicators["frequent_candidate"] = frequent_candidate(chunk, self.np_frequencies)
                total_score = sum(indicators.values())  
                candidate_scores.append((chunk, total_score, indicators))  
                if print_:
                    print(f"Candidate: {chunk.text}")
                    for k, v in indicators.items():
                        print(f"  {k}: {v}")
                    print(f"  Total Score: {total_score}\n")
            self.all_candidate_scores[anaphor_token] = candidate_scores
        return self.all_candidate_scores
    
    # Phase 5
    def phase_5(self):
        self.antecedents = {}
        for anaphor_token, candidate_list in self.all_candidate_scores.items():
            if not candidate_list:
                self.antecedents[anaphor_token] = None
                continue
            max_score = max(candidate_list, key=lambda x: x[1])[1]
            top_candidates = [cand for cand in candidate_list if cand[1] == max_score]
            noun_candidates = []
            for cand in top_candidates:
                tokens_ok = all(t.pos_ in {"ADJ", "NOUN", "PROPN", "DET"} for t in cand[0]) 
                if cand[0].root.pos_ in {"NOUN", "PROPN"} and tokens_ok:
                    noun_candidates.append(cand)
            if noun_candidates:
                best_chunk = min(noun_candidates, key=lambda x: x[0].start)
            else:
                best_chunk = min(top_candidates, key=lambda x: x[0].start)

            self.antecedents[anaphor_token] = best_chunk[0]

    # Resolve the anaphors in the text
    def resolve(self, text, print_=False):
        self.phase_1(text)
        self.phase_2()
        self.phase_3()
        self.phase_4(print_=print_) 
        self.phase_5()
        return self.antecedents

    # Replace the anaphors in the text with their antecedents
    def replace(self, text):
        self.resolve(text)
        new_tokens = []
        for token in self.doc:
            replaced = False
            for anaphor_token, antecedent in self.antecedents.items():
                if token == anaphor_token and antecedent:
                    new_tokens.append(antecedent.text)
                    replaced = True
                    break
            if not replaced:
                new_tokens.append(token.text)
        output = ""
        for i, token in enumerate(new_tokens):
            if i > 0 and token not in ",.:;!?":
                output += " "
            output += token
        return output.strip()


