# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime, timedelta, date
import time
import gitlab
from settings import GIT_SETTINGS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gitlab-ranking-list")


class ProjectMetadata:

    def __init__(self):
        self.path_with_namespace = ''
        self.http_url_to_repo = ''
        self.commit_count = 0
        self.branch_count = 0
        self.tag_count = 0
        self.contributors_count = 0
        self.forks_count = 0
        self.repository_size = 0
        self.last_activity_at = ''

    def __str__(self):
        return "project metadata:{ " \
               "path_with_namespace: '%s'  " \
               "http_url_to_repo: '%s' ," \
               "commit_count: %d ," \
               "branch_count: %d ," \
               "tag_count: %d ," \
               "contributors_count: %d ," \
               "forks_count: %d ," \
               "repository_size: %d " \
               "last_activity_at: %s " \
               "}" % (
                   self.path_with_namespace,
                   self.http_url_to_repo,
                   self.commit_count,
                   self.branch_count,
                   self.tag_count,
                   self.contributors_count,
                   self.forks_count,
                   self.repository_size,
                   self.last_activity_at
               )


def get_gitlab_instance():
    gitlab_url = GIT_SETTINGS.get('gitlab_url')
    private_token = GIT_SETTINGS.get('private_token')
    gitlab_server = gitlab.Gitlab(gitlab_url, private_token=private_token)
    gitlab_server.auth()
    return gitlab_server


def get_all_project_metadata():
    logger.info("get all project metadata[begin]")
    all_project_metadata = []
    gitlab_instance = get_gitlab_instance()
    page = 1
    while True:
        logger.info("page number: %d" % page)
        per_page = 30
        projects = gitlab_instance.projects.list(statistics=True, page=page, per_page=per_page)
        logger.info("projects number is: %d" % len(projects))
        for project in projects:
            # ignore forked project
            if not hasattr(project, 'forked_from_project'):
                project_metadata = ProjectMetadata()
                project_metadata.path_with_namespace = project.path_with_namespace
                project_metadata.http_url_to_repo = project.http_url_to_repo
                project_metadata.commit_count = project.statistics['commit_count']
                project_metadata.repository_size = project.statistics['repository_size']
                project_metadata.forks_count = project.forks_count
                project_metadata.last_activity_at = project.last_activity_at

                try:
                    branches = project.branches.list(all=True)
                    project_metadata.branch_count = len(branches)
                    tags = project.tags.list(all=True)
                    project_metadata.tag_count = len(tags)
                    contributors = project.repository_contributors(all=True)
                    project_metadata.contributors_count = len(contributors)
                except gitlab.exceptions.GitlabError:
                    # the project dose not has a repository
                    pass
                all_project_metadata.append(project_metadata)
        if len(projects) < per_page:
            logger.info("get all project metadata[end]")
            break
        page += 1

    return all_project_metadata


def last_activity_at_convert(last_activity_at):
    """
    2020-02-26T09:55:47.215Z --> 2020-02-26 17:55:47
    :param last_activity_at:
    :return:
    """
    last_activity_at = last_activity_at[:19].replace("T", " ")
    last_activity_at_dt = datetime.strptime(last_activity_at, "%Y-%m-%d %H:%M:%S")
    last_activity_at_dt_plus_8_hours = last_activity_at_dt + timedelta(hours=8)
    return str(last_activity_at_dt_plus_8_hours)


def date_compare_with_thirty_days_ago(last_changed_date):
    if last_changed_date == "":
        return False
    thirty_days_ago = (date.today() + timedelta(days=-30)).strftime("%Y-%m-%d")
    thirty_days_ago_seconds = time.mktime(time.strptime(thirty_days_ago, "%Y-%m-%d"))
    last_changed_date_seconds = time.mktime(time.strptime(last_changed_date, "%Y-%m-%d"))
    if last_changed_date_seconds > thirty_days_ago_seconds:
        return True
    else:
        return False


def generate_project_metadata_html_table(project_metadata_list):
    html_table = "<table border='1' cellspacing='0'>"
    html_table += "<tr>"
    html_table += "<td>number</td>"
    html_table += "<td>path</td>"
    html_table += "<td>commits</td>"
    html_table += "<td>branches</td>"
    html_table += "<td>tags</td>"
    html_table += "<td>contributors</td>"
    html_table += "<td>forks</td>"
    html_table += "<td>repository size</td>"
    html_table += "<td>last activity date</td>"
    html_table += "</tr>"
    for i, project_metadata in enumerate(project_metadata_list):
        number = i + 1
        html_table += "<tr>"
        html_table += "<td>%s</td>" % number
        path_with_link = "<a href='%s'>%s</a>" % (project_metadata.http_url_to_repo,
                                                  project_metadata.path_with_namespace)
        html_table += "<td>%s</td>" % path_with_link
        if project_metadata.commit_count > 10000:
            green_str = "<font color='green'>%d</font>" % project_metadata.commit_count
            html_table += "<td>%s</td>" % green_str
        else:
            html_table += "<td>%d</td>" % project_metadata.commit_count
        if project_metadata.branch_count > 100:
            error_str = "<font color='red'>%d</font>" % project_metadata.branch_count
            html_table += "<td>%s</td>" % error_str
        else:
            html_table += "<td>%d</td>" % project_metadata.branch_count
        html_table += "<td>%d</td>" % project_metadata.tag_count
        html_table += "<td>%d</td>" % project_metadata.contributors_count
        html_table += "<td>%d</td>" % project_metadata.forks_count
        repository_size_m = format(float(project_metadata.repository_size) / float(1024 * 1024), '.1f')
        html_table += "<td>%sM</td>" % repository_size_m
        last_activity_at = last_activity_at_convert(project_metadata.last_activity_at)
        last_activity_at_date = last_activity_at[:10]
        if date_compare_with_thirty_days_ago(last_activity_at_date):
            tips_str = "<font color='blue'>%s</font>" % last_activity_at_date
            html_table += "<td>%s</td>" % tips_str
        else:
            html_table += "<td>%s</td>" % last_activity_at_date
        html_table += "</tr>"
    html_table += "</table>"
    return html_table


def main():
    all_project_metadata = get_all_project_metadata()
    all_project_metadata = sorted(all_project_metadata, key=lambda metadata: metadata.repository_size,
                                  reverse=True)
    top_100_project_metadata = all_project_metadata[:100]

    logger.info("top 100:")
    for project_metadata in top_100_project_metadata:
        print project_metadata
    html_table = generate_project_metadata_html_table(top_100_project_metadata)
    os.system('echo "%s" > gitlab-ranking-list.html' % html_table)


if __name__ == "__main__":
    main()
