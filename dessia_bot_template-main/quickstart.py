import os
import sys
from typing import Tuple
import shutil
import subprocess

from pathlib import Path
parent_folder = Path(os.getcwd()).parent



base_folder = input("Select folder in which the project will be generated (default: {}): ".format(parent_folder))
if not base_folder:
    base_folder = parent_folder
print('Project will be created in folder {}'.format(base_folder))



def has_special_char(string: str) -> Tuple[bool, str]:
    for char in ['&', 'é', '~', '"', ',', "'", '{', '(', '£',
                 ',', '-', '|', 'è', "`", 'ç', '^', ';', '$',
                 'à', '@', ')', ']', '°', '=', '}', ':', 'µ'
                 '+', '*', '/', '.', '\\', '?', '!', '%', 'ù']:
        if char in string:
            return True, char
    return False, ''


def enter_valid_name(target: str, default: str = None):
    valid_name = False
    n_retries = 0
    while not valid_name and n_retries < 10:
        if default is None:
            prompt = 'Enter {} name : '.format(target)
        else:
            prompt = 'Enter {} name (default : {}) : '.format(target, default)
        name = input(prompt)
        has_special, special_char = has_special_char(name)
        if not name and default is not None:
            name = default

        valid_name = (len(name) > 3 and name.islower() and not has_special)
        if not valid_name:
            n_retries += 1
            msg = '{} name is not valid.\n'.format(target)
            msg += ' It must not contain caps nor special characters '
            msg += 'and must be longer than 3 characters.\n'
            msg += 'Please retry. ({}/10)'.format(n_retries)
            print(msg)
    if not valid_name:
        msg = 'Maximum retries exceeded, {} name is not valid'.format(target)
        raise ValueError(msg)
    return name


package_name = enter_valid_name('Package')
project_path = os.path.join(base_folder, package_name)
if os.path.exists(project_path):
    confirm = input('the folder {} already exists. Confirm to use existing folder (y/N): '.format(project_path))
    if confirm.lower() not in ['y', 'yes']:
        raise ValueError('Aborting in using existing folder')
else:
    os.mkdir(project_path)

package_path = os.path.join(project_path, package_name)

if not os.path.exists(package_path):
    os.mkdir(package_path)

assets_path = os.path.join(package_path, 'assets')
if not os.path.exists(assets_path):
    os.mkdir(assets_path)

shutil.copyfile('logo.png', os.path.join(assets_path, 'logo.png'))


setup_path = os.path.join(project_path, 'setup.py')
scripts_path = os.path.join(project_path, 'scripts')


module_name = enter_valid_name('Module', 'core')
if not module_name:
    module_name = 'core'


shutil.copyfile('setup_template.py', setup_path)

if not os.path.exists(scripts_path):
    os.mkdir(scripts_path)

init_path = os.path.join(package_path, '__init__.py')
if not os.path.exists(init_path):
    init_file = open(init_path, 'x+')
    init_file.write("from .{} import *".format(module_name))
else:
    print('__init__.py already exists, skipping creation') 


module_path = os.path.join(package_path, '{}.py'.format(module_name)) 
if not os.path.exists(module_path):
    module_file = open(module_path, 'x+')
    module_file.write("is_created = True")
else:
    print('base python module already exists, skipping creation') 

short_description = input('Enter a short description : ')
author_name = input('Enter your name : ')
author_mail = input('Enter your e-mail : ')
requirements = input("Enter required packages, separated by a coma (default : ['dessia_common'])")
python_version = input('Enter Python version (default : >=3.8) : ')
if not requirements:
    requirements = ['dessia_common']
else:
    requirements = requirements.split(',')

if not python_version:
    python_version = ">=3.8"

from_git_tags = input('Do you want to enable version from git tags? (Y/n): ')

# Writing file
setup_str = "\n\nsetup(\n"
if from_git_tags == 'N':
    setup_str += "\tversion='0.0.1',\n"
else:
    setup_str += "\tversion=get_version(),\n"

setup_str += "\tname='{}',\n".format(package_name)
setup_str += "\tdescription='{}',\n".format(short_description)
setup_str += "\tlong_description=readme(),\n"
setup_str += "\tauthor='{}',\n".format(author_name)
setup_str += "\tauthor_email='{}',\n".format(author_mail)
setup_str += "\tinstall_requires={},\n".format(requirements)
setup_str += "\tpython_requires='{}',\n".format(python_version)
setup_str += "\tpackages=find_packages(),\n"
setup_str += ")"

setup_file = open(setup_path, 'a+')
setup_file.write(setup_str)


print('Project generated to {}'.format(project_path))
