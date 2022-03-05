import os
from numpy import array_split
from google.cloud import dlp_v2

from pii_benchmarking import utils


class Masker:
    BATCH_LIMIT = 1000  # avoid character limit for GCP DLP

    def __init__(self):
        self.masker = dlp_v2.DlpServiceClient().from_service_account_json(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        self.parent = 'projects/lpgprj-sbo-n-cnveng-gl-01'

    def mask_text(self, text):
        result = self.masker.inspect_content(request={'parent': self.parent, 'item': {'value': text}})
        return self._standardize_result(text, result.result.findings)

    def batch_mask(self, list_of_text):
        result = list()
        # split based on batch size limit
        n_split = int(len(list_of_text) / self.BATCH_LIMIT) + 1
        split_text = array_split(list_of_text, n_split)

        for batch in split_text:
            headers = [{'name': 'input_text'}]
            rows = [{'values': [{'string_value': b}]} for b in batch]
            table = {'headers': headers, 'rows': rows}

            temp = self.masker.inspect_content(request={'parent': self.parent, 'item': {'table': table}})
            temp = self._standardize_multi_result(batch, temp.result.findings)
            result.extend(temp)

        return result

    def _standardize_multi_result(self, list_of_text, result):
        # sort results into bins based on their correspondence with row number
        temp_results = [list() for _ in list_of_text]
        for i in range(len(result)):
            row_number = result[i].location.content_locations[0].record_location.table_location.row_index
            temp_results[row_number].append(result[i])

        # standardize each bin
        processed_results = list()
        for i in range(len(temp_results)):
            processed_results.append(self._standardize_result(list_of_text[i], temp_results[i]))
        return processed_results

    @staticmethod
    def _standardize_result(text, result):
        entities = list()
        for r in result:
            temp = {'entity_label': r.info_type.name,
                    'start_char': r.location.byte_range.start,
                    'end_char': r.location.byte_range.end,
                    'likelihood_label': r.likelihood.name
                    }
            temp = utils.standardized_person_ent(temp)
            entities.append(temp)
        return utils.get_standardized_result('gcp', text, entities)
