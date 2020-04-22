import json

from github import Github
from sys import argv

debug = True


def main():
    # check that usage is correct
    if not len(argv) in range(2, 4):
        print("Usage: gc.py reponame [template]")
        exit(1)

    log(argv)

    print(f"Creating GitHub Repository '{argv[1]}'")

    # load login configuration
    with open('cred.json', 'r+') as f:
        cred = json.load(f)
        log(cred)

    # extract information from config
    user = cred['user']
    token = cred['token']
    method = cred['method']

    if method == 'user':
        # check if user credentials have been set
        if user['name'] != 'username' and user['password'] != 'password':
            # establish connection with GitHub API
            print(f"Logging into GitHub as {user['name']}")
            g = Github(user['name'], user['password'])
        else:
            # TODO let user update his login information or switch to token method
            print('No login information found. Please update your login information in the cred.json file.\n'
                  'Exiting script, no files have been created.')
            exit(2)
    elif method == 'token':
        # check if token has been set
        if token != 'token':
            g = Github(token)


# authenticate user


# might be better to just use the built in logging module
def log(m):
    """ Prints a message only if the debug flag is set"""
    if debug:
        print(m)


if __name__ == "__main__":
    main()
