from typing import List, Literal

from dessia_common.core import DessiaObject, PhysicalObject


class Workshop1(DessiaObject):
    """
        Class used to launch the Workshop 1 on the platform

        :param question_account_active: Is your account active?
        :type question_account_active: bool
        :param question_account_admin: Are you a platform Administrator?
        :type question_account_admin: bool
        :param question_documentation: From which website is the global documentation accessible?
        :type question_documentation: Literal
        :param question_support: What is the email used to contact Dessia's support?
        :type question_support: str
        :param question_organisation: Select the intruder answer among those provided?
        :type question_organisation: Literal
        :param question_workspace: Give the workspace exact name which has been shared with you.
        :type question_workspace: Literal
        :param question_number_workflows_in_workspace: How many workflows do you see in the shared Workspace?
        :type question_number_workflows_in_workspace: str
        :param question_first_workflow_in_workspace: What is the exact name of the 1st workflow in the shared Workspace?
        :type question_first_workflow_in_workspace: str
        :param question_object_name_in_library: Give the exact name of one object instance of
        dessia_common.workflow.core.Workflow present in the database.
        :type question_object_name_in_library: str
        :param question_first_file_name_shared: Give the exact name of the 1st input data file shared with you.
        :type question_first_file_name_shared: str
        :param question_first_task_status: What is the status of the very first Task done on the platform?
        :type question_first_task_status: Literal
        :param question_admin_useful_page: Among the proposed pages, which one is not a mainly used page?
        :type question_admin_useful_page: Literal
        :param name: Object name
        :type name: str

        """
    _standalone_in_db = True

    def __init__(self,
                 question_account_active: bool,
                 question_account_admin: bool,
                 question_documentation: Literal["https://doc.dessia.io",
                                                 "https://dessia.io",
                                                 "https://documentation.dessia.io",
                                                 "https://support.dessia.io"],
                 question_support: str,
                 question_organisation: Literal["An organization is mandatory to create a Workspace",
                                                "An organization gives rights in the inherited workspaces",
                                                "An organization is mandatory to use the platform"],
                 question_workspace: Literal["Training_Workspace",
                                             "Base_de_donnees_Formateurs",
                                             "Overview of all my bots"],
                 question_number_workflows_in_workspace: int,
                 question_first_workflow_in_workspace: str,
                 question_object_name_in_library: str,
                 question_first_file_name_shared: str,
                 question_first_task_status: Literal["SUCCESS", "FAILURE", "COMPUTING", "PENDING", "LOST"],
                 question_admin_useful_page: Literal["Applications", "Actions", "Config", "Systems Logs"],
                 name: str):

        self.question_account_active = question_account_active
        self.question_account_admin = question_account_admin
        self.question_documentation = question_documentation
        self.question_support = question_support
        self.question_organisation = question_organisation
        self.question_workspace = question_workspace
        self.question_number_workflows_in_workspace = question_number_workflows_in_workspace
        self.question_first_workflow_in_workspace = question_first_workflow_in_workspace
        self.question_object_name_in_library = question_object_name_in_library
        self.question_first_file_name_shared = question_first_file_name_shared
        self.question_first_task_status = question_first_task_status
        self.question_admin_useful_page = question_admin_useful_page
        DessiaObject.__init__(self, name=name)

    def check_answers(self):
        """

        :return:
        """

        score = 0
        error = 0
        # Monitor account activation
        if self.question_account_active:
            print("OK - Your account is active.")
            score += 1
        else:
            print("NOK - Ask a platform administrator to activate your account.")
            error += 1

        # Monitor account administration
        if self.question_account_admin:
            print("OK - Your account is an administrator one.")
            score += 1
        else:
            print("NOK - Ask a platform administrator to provide you administrator rights.")
            error += 1

        # Monitor documentation URL provided by the user
        if self.question_documentation == "https://documentation.dessia.io":
            print("OK - https://documentation.dessia.io is the correct URL address to go "
                  "to Dessia's global documentation .")
            score += 1
        else:
            print("NOK - The given URL is not the correct one to go to Dessia's documentation."
                  "Check the Documentation button and the redirection URL page.")
            error += 1

        # Monitor support email address provided by the user
        if self.question_support == "support@dessia.io":
            print("OK - support@dessia.io is the correct email address to write to Dessia's support.")
            score += 1
        else:
            print("NOK - The given email address is not the correct one to write to Dessia's support. "
                  "Check the Issue page")
            error += 1

        # Monitor organizations rights
        if self.question_organisation == "An organization is mandatory to use the platform":
            print("OK - Being part of an organization is not mandatory to use the platform.")
            score += 1
        elif self.question_organisation == "An organization is mandatory to create a Workspace":
            print("NOK - It is mandatory to have an organization to create a Workspace.")
            error += 1
        elif self.question_organisation == "An organization gives rights in the inherited workspaces":
            print("NOK - Being an organization admin gives automatic admin rights to the inherited Workspaces.")
            error += 1
        else:
            raise Exception("There is an error in the answers concerning the Organization Part.")

        # Monitor workspace names
        if self.question_workspace == "Training_Workspace":
            print("OK - This Workspace is the one that has been shared to you.")
            score += 1
        elif self.question_workspace == "Base_de_donnees_Formateurs":
            print("NOK - This Workspace has not been shared to you. Please, check your Bot Store page.")
            error += 1
        elif self.question_workspace == "Overview of all my bots":
            print("NOK - This Workspace has not been shared to you. It is the initial Workspace you automatically got "
                  "with your account creation. Please, check your Bot Store page.")
            error += 1
        else:
            raise Exception("There is an error in the answers concerning the Workspace Part.")

        # Monitor number of workflows in Workspace
        if self.question_number_workflows_in_workspace == 7:
            print("OK - There are 7 AI-Apps in the shared Workspace.")
            score += 1
        else:
            print("NOK - The number of AI-Apps provided is not correct. Check the Bot Store page")
            error += 1

        # Monitor name of 1st workflow in Workspace
        if self.question_first_workflow_in_workspace == 'KNAPSACK PROBLEM':
            print("OK - The first AI-App name in the shared Workspace is 'KNAPSACK PROBLEM'.")
            score += 1
        else:
            print("NOK - The given name is note the correct one. Check the Bot Store page.")
            error += 1

        # Monitor name of object in Library
        list_objects = ["KNAPSACK PROBLEM", "WORKSHOP 4.1 - a", "WORKSHOP 4.1 - b", "WORKSHOP 4.1 - c", "WORKSHOP 4.2",
                        "Knapsack Generation from Step", "WORKSHOP 1"]
        if self.question_object_name_in_library == 'KNAPSACK PROBLEM':
            print("OK - The first AI-App name in the shared Workspace is 'KNAPSACK PROBLEM'.")
            score += 1
        else:
            print("NOK - The given name is note the correct one. Check the Bot Store page.")
            error += 1


