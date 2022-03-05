from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from pii_benchmarking import utils


class Masker:

    def __init__(self):
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_trf"}]
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        self.masker = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

    def mask_text(self, text):
        result = self.masker.analyze(text=text,
                                     entities=["PERSON"],
                                     language="en")
        return self._standardize_result(text, result)

    def batch_mask(self, list_of_text):
        result = list()
        for text in list_of_text:
            result.append(self.mask_text(text))
        return result

    @staticmethod
    def _standardize_result(text, result):
        key_map = {'entity_type': 'entity_label', 'start': 'start_char', 'end': 'end_char', 'score': 'score'}
        entities = list()
        for r in result:
            r = {key_map[k]: v for (k, v) in r.to_dict().items() if k in key_map.keys()}
            r = utils.standardized_person_ent(r)
            entities.append(r)
        return utils.get_standardized_result('presidio', text, entities)
