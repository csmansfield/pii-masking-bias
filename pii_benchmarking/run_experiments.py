import sys
import os
import pandas as pd
from pii_benchmarking import pii_engine


def is_labeled(entities, start_char, end_char):
    for entity in entities:
        if entity['start_char'] <= start_char and entity['end_char'] >= end_char:
            return entity['entity_label']
    return 'NONE'


def main(eval_dir):
    eval_files = os.listdir(eval_dir)

    for file in eval_files:
        if file.endswith('.csv'):
            service_names = ['aws', 'gcp', 'presidio']
            for service_name in service_names:
                print(f"Masking {file} with {service_name}...")
                df = pd.read_csv(os.path.join(eval_dir, file), index_col=0)

                masker = pii_engine.Masker(service_name)
                masked_results = masker.batch_mask(df['Text'].tolist())

                assert df.shape[0] == len(masked_results)

                masked_col_name = f"Masked_{service_name}"
                df[masked_col_name] = pd.Series([x['masked_input'] for x in masked_results])

                entities_col_name = f"Entities_{service_name}"
                df[entities_col_name] = pd.Series([x['results'] for x in masked_results])
                df[f"Recall_{service_name}"] = df.apply(lambda x: is_labeled(x[entities_col_name],
                                                                             x['Start_index'], x['End_index']), axis=1)
                df.to_csv(os.path.join(eval_dir, file))


if __name__ == "__main__":
    eval_dir = sys.argv[1]
    main(eval_dir)
