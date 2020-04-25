import argparse
import sys
import json
import subprocess

from github import Github, BadCredentialsException

debug = False


def main():
    """CLI for creating a GitHub repo"""

    # parsing input arguments
    parser = argparse.ArgumentParser(description='Create and clone GitHub Repositories')
    parser.add_argument('repo_name', type=str, help='name of the repository')
    parser.add_argument('-p', '--private', action='store_true', help='set repo as private', default=False)
    parser.add_argument('-d', '--desc', type=str, help='add a description')
    parser.add_argument('-r', '--readme', action='store_const', help='initialize with readme', const='readme.md')
    args = parser.parse_args()

    print(f"Creating repository with the following arguments: \n"
          f"name: {args.repo_name} \n"
          f"private: {args.private} \n"
          f"desc: {args.desc} \n"
          f"readme: {args.readme} \n")

    answer = query_yes_no("Continue with those settings?")

    # Terminate script if the user doesn't want to continue
    if not answer:
        exit(1)

    store = False
    # Check cred.json for a GitHub token
    with open('cred.json', 'r') as f:
        cred = json.load(f)
        log(cred)

        token = cred['token']

        if token == "token":
            token = query_token()
        else:
            answer = query_yes_no("Previous token found. Do you want to use it?")
            if not answer:
                token = query_token()
                if query_yes_no("Store as new token?"):
                    store = True

    # Try to connect with GitHub
    # TODO could be improved by only looping when a new token has been submitted since the stored token has
    # proven to be successful
    g = None
    user = None
    success = False
    while not success:
        try:
            g = Github(token)
            user = g.get_user()
            user.get_repos()
            success = True
        except BadCredentialsException:
            success = False
            if query_yes_no('Connection with GitHub failed. Do you want to try another token?'):
                query_token()
            else:
                exit(2)

    # At this point g and user are guaranteed to have values and the token works.
    # Store the new token if requested.
    if store:
        with open('cred.json', 'w') as f:
            f.write(json.dumps({'token': token}))

    # TODO Error handling for duplicate names
    print(f'Creating repository {args.repo_name}')
    repo = user.create_repo(args.repo_name, private=args.private)
    print('Repository created')

    if args.readme is not None:
        # Prepare readme file
        readme = f"# {args.repo_name} \n" \
                 f"{args.desc if args.desc is not None else ''}"
        print(f'Adding {args.readme}')

        repo.create_file(args.readme, 'initial commit', readme)

    url = repo.clone_url
    print(f'Repo url: {url}')

    clone = ["git", "clone", url]
    subprocess.run(clone)


def query_token():
    """Simply asks the user for a token."""

    print("Please enter your GitHub token:")
    token = input()
    return token


def query_yes_no(question, default="yes"):
    """Ask a yes/no question and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


# might be better to just use the built in logging module
def log(m):
    """ Prints a message only if debug flag is set"""
    if debug:
        print(m)


if __name__ == "__main__":
    main()
