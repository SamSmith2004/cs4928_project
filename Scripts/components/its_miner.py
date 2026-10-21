"""Mines the issue data for a github repo"""

import logging
from configparser import ConfigParser
from datetime import datetime
from logging import Logger
from threading import Thread

from github import Auth, Github
from github.GithubException import UnknownObjectException
from github.Issue import Issue
from pause import until

from .helper import get_config_variable


class ITSMiner:
    """
    Represents the issue data miner for github.

    ## Attributes:

    __issue_data (list): instance variable that stores all the issue data for a repo
    __config (ConfigParser): config object to hold module configs
    logger (Logger): module level logger object

    ## Methods:

    mine_issue_data(): Class method to get all the issue data for a repo
    """

    def __init__(self, config: ConfigParser) -> None:

        self.__issue_data: list = []
        self.__config: ConfigParser = config
        self.logger: Logger = None

        self.__setup_logger()

    def __setup_logger(self):
        """
        Setup and configure the logger for this module
        """

        # Setting up module level logger
        self.logger = logging.getLogger(__name__)
        console_handler = logging.StreamHandler()
        self.logger.addHandler(console_handler)
        formatter = logging.Formatter(
            fmt="{asctime} - {name} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )
        console_handler.setFormatter(formatter)
        self.logger.setLevel(get_config_variable("LOGGING_LEVEL", ["logging", "level"], self.__config))

    def mine_issue_data(self, repo: str) -> list | None:
        """
        Mines all the issue data for a github repository. The method should be run in a thread because of 
        API rate limiting handling so the program start executing from the same point.

        ## Parameter:

        repo (str): Name of the repository. Has to be of the format `Owner/Repository`

        ## Returns:

        Returns a list with all issue data as a list. Returns `None` if no issue data is found
        """

        auth = Auth.Token(get_config_variable("API_KEY", ["api", "key"], self.__config))
        github = Github(auth=auth)

        try:
            gh_repo = github.get_repo(repo)
        except UnknownObjectException as err:
            self.logger.error(f"Repository {repo} not found on Github. Error: {err}")
            return None
        issues = gh_repo.get_issues(state="all")

        self.logger.info(f"Fetching issues for project {gh_repo.full_name} - total count = {issues.totalCount}")

        # clear previous issues
        self.__issue_data.clear()

        # for each issue get required data
        for issue in issues:

            # pause the program if the ratelimit
            # is about to expire
            if github.rate_limiting[0] < 10:
                self.logger.info(f"Rate limit about to reach - Pausing the issue miner until {datetime.fromtimestamp(github.rate_limiting_resettime)}")
                until(github.rate_limiting_resettime)

            self.logger.debug(f"API rate limit used: {github.get_rate_limit().raw_data["core"]["used"]}")
            self.logger.debug(f"Fetching data for issue: {issue.number}; Project: {gh_repo.full_name}")

            issue_data = {}

            # create threads for seperate newtork request
            # to reduce computation time
            issue_data_thread = Thread(
                target=self.__get_issue_raw_data,
                args=(issue, issue_data,)
            )
            comments_data_thread = Thread(
                target=self.__get_issue_comments,
                args=(issue, issue_data,)
            )
            timeline_data_thread = Thread(
                target=self.__get_issue_timeline,
                args=(issue, issue_data,)
            )

            # start the threads
            issue_data_thread.start()
            comments_data_thread.start()
            timeline_data_thread.start()

            # wait for all threads to
            # process before continuing to the next issue
            issue_data_thread.join()
            comments_data_thread.join()
            timeline_data_thread.join()

            self.__issue_data.append(issue_data)

        return self.__issue_data

    def __get_issue_raw_data(self, issue: Issue, issue_data: dict):
        """
        Get the raw data for issue

        ## Parameters

        issue (Issue): issue instance of the repo

        issue_data (dict): data dictionary in which to insert data
        """

        issue_data.update(issue.raw_data)

    def __get_issue_comments(self, issue: Issue, issue_data: dict):
        """
        Extract the comments of the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        issue_data (dict): data dictionary in which to insert data
        """

        comments = []

        for comment in issue.get_comments():
            comments.append(comment.raw_data)
        issue_data["comments"] = comments

    def __get_issue_timeline(self, issue: Issue, issue_data: dict):
        """
        Get the events related to the issue

        ## Parameters

        issue (Issue): Issue instance of the repo

        issue_data (dict): data dictionary in which to insert data
        """

        timeline = []

        for event in issue.get_timeline():
            timeline.append(event.raw_data)

        issue_data["timeline"] = timeline

    @classmethod
    def __get_issue_events(cls, issue: Issue) -> list:
        """
        Get the events related to the issue

        ## Parameters

        issue (Issue): Issue instance of the repo

        ## Returns

        A list containing the issue events
        """

        events = []

        for event in issue.get_events():
            events.append(event.raw_data)

        return events

    @classmethod
    def __get_issue_number(cls, issue: Issue) -> int:
        """
        Get the number of the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns:

        An int representing the issue number
        """

        issue_number = issue.number
        return issue_number

    @classmethod
    def __get_issue_title(cls, issue: Issue) -> str:
        """
        Get the title of the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns:

        A string representing the issue title
        """

        issue_title = issue.title
        return issue_title

    @classmethod
    def __get_issue_body(cls, issue: Issue) -> str:
        """
        Extract the issue body

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns:

        A string representing the issue body
        """

        issue_body = issue.body
        return issue_body

    @classmethod
    def __get_issue_status(cls, issue: Issue) -> str:
        """
        Extract the status of the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns:

        The issue status as a string
        """

        status = issue.state
        return status

    @classmethod
    def __get_issue_date_created(cls, issue: Issue) -> str:
        """
        Extract the date at which the issue was created.

        Formats the date to a string.

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns
        The issue created date as string
        """

        date_created = issue.created_at
        date_created = datetime.strftime(date_created, "%d.%m.%y-%H.%M.%S")
        return date_created

    @classmethod
    def __get_issue_date_closed(cls, issue: Issue) -> str | None:
        """
        Extract the date at which the issue was closed

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns

        The date the issue was closed at if it exists
        """

        date_closed = issue.closed_at

        if date_closed:
            date_closed = datetime.strftime(date_closed, "%d.%m.%y-%H.%M.%S")

        return date_closed

    @classmethod
    def __get_issue_labels(cls, issue: Issue) -> list:
        """
        Extract the labels asociated with the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns:

        A list containing labels information.
        """

        labels = []

        for label in issue.labels:
            labels.append({
                "name": label.name,
                "color": label.color,
                "description": label.description
            })

        return labels

    @classmethod
    def __get_issue_user_data(cls, issue: Issue) -> dict:
        """
        Extract the user details

        Extract the details of the user that created the issue

        ## Parameters:

        issue (Issue): Issue instance of the repo

        ## Returns

        Dictionary with user data
        """

        user_data = {}
        user_data.update({
            "username": issue.user.login,
            "id": issue.user.id,
            "url": issue.user.url,
            "repos_url": issue.user.repos_url,
            "type": issue.user.type
        })

        return user_data
