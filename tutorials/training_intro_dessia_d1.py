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
        :param question_file_name_shared: Give the exact name of one of the input data files shared with you.
        :type question_file_name_shared: str
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
                 question_file_name_shared: str,
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
        self.question_file_name_shared = question_file_name_shared
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
        if self.question_object_name_in_library in list_objects:
            print("OK - The object name you gave is actually in the database in the specified location.")
            score += 1
        else:
            print("NOK - The object name you gave is either not exact or does not correspond to an object present in "
                  "the specified location in the database. Please check the Library page and select in the filtering "
                  "menu: dessia_common / workflow / core / Workflow.")
            error += 1

        # Monitor name of an input data file in My Files
        list_files = ["Excel_file_demo_1.xlsx", "Knapsack_10kg.step", "Step_file_demo_1.step"]
        if self.question_file_name_shared in list_files:
            print("OK - The file name you gave is actually in the file database.")
            score += 1
        else:
            print(
                "NOK - The file name you gave is either not exact, has not its extension provided or does not "
                "correspond to a file present in the database. Please check the My Files page.")
            error += 1

        # Monitor status of the first calculation on the platform
        if self.question_first_task_status == "SUCCESS":
            print("OK - The status you gave for Task #1 is actually the good one.")
            score += 1
        else:
            print("NOK - The status you gave for Task #1 is not the good one. Please check the Tasks page and navigate "
                  "to the last page with Task #1.")
            error += 1

        # Monitor admin useful pages
        if self.question_admin_useful_page == "Config":
            print("OK - Page Config is actually a secondary page since it is not use in User nor Developing mode.")
            score += 1
        elif self.question_admin_useful_page == "Applications":
            print("NOK - The page Applications you provided is actually a very useful page for Developing mode since "
                  "it allows a developer to change its packages/libraries/applications versions when some features "
                  "are added.")
            error += 1
        elif self.question_admin_useful_page == "Actions":
            print("NOK - The page Actions you provided is actually a very useful page for Developing mode since it "
                  "allows a user or developer to reboot the platform after a package change for example.")
            error += 1
        elif self.question_admin_useful_page == "Systems Logs":
            print("NOK - The page Systems Logs you provided is actually a very useful page for Developing mode since "
                  "it allows a developer to have more information about the platform processes, tasks and errors.")
            error += 1
        else:
            raise Exception("There is an error in the answers concerning the Admin Part.")

        # Results
        print(f'Your final score is: \n > {score} correct answers \n > {error} wrong answers.')
        if error != 0:
            print("Try launching again the Workshop in order to improve your score!")
        else:
            print("Congratulations! \n "
                  "You did an amazing job! \n "
                  "You are ready to listen to Module 2 - Run you AI-App.")
