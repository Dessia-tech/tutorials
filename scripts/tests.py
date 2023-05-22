
import os

for script_name in os.listdir():
    if script_name.endswith('.py'):
        print('\n## Executing script {}'.format(script_name))
        exec(open(script_name).read())
