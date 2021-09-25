BASE_URL = 'https://leetcode.com'
GRAPHQL_URL = 'https://leetcode.com/graphql'
API_URL = BASE_URL + '/api/problems/algorithms/'
HOME_URL = BASE_URL + '/problemset/algorithms'
SUBMISSION_URL = BASE_URL + '/submissions/detail/{id}/check/'

LANG_MAPPING = {
    'C++': 'cpp',
    'Python': 'python',
    'Python3': 'python3',
    'Java': 'java',
    'C': 'c',
    'C#': 'csharp',
    'Javascript': 'javascript',
    'Ruby': 'ruby',
    'Swift': 'swift',
    'Go': 'go',
}


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
