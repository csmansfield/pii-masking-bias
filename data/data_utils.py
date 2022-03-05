from scipy.stats import mannwhitneyu
from numpy.random import default_rng

# Set up a random generator for reproducibility
bg = default_rng(2019).bit_generator


def get_random_gen(n=2019):
    # Generates a random state generator
    return default_rng(n)


def name_lists_by_race(df, column, threshold=75, sample_size=None, queries=[], label=''):
    # df: the dataframe containing demographic info
    # column: which column (pctrace) to sort by
    # threshold: how many people self-identifed as race corresponding to column
    # sample_size: max number of samples
    # queries: restrictions on the data
    # label: group name for print statement
    query = f"{column} >= {threshold}"
    predominantly_x_names = df.query(query).copy()
    
    # If the data isn't 'randomly' sampled, we look at only uncommon names, because some race/ethnicity
    # groups only include these less common names.  This gives roughly equal levels of 'commonness' in names.
    if queries:
        for q in queries:
            predominantly_x_names = predominantly_x_names.query(q).copy()
    if sample_size and sample_size < predominantly_x_names.shape[0]:
        predominantly_x_names = predominantly_x_names.sample(sample_size, random_state=bg)

    print(f"Found {predominantly_x_names.shape[0]} predominant {label} names")
    return predominantly_x_names


def sig_of_means(df, queries, col, label=""):
    test = mannwhitneyu(df.query(queries[0])[col], df.query(queries[1])[col])
    print(f"Report for {label}: {test}")
