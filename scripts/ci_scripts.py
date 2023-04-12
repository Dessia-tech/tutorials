import os

for script_name in os.listdir():
    if script_name.endswith('.py') and script_name != 'ci_scripts.py':
        script = os.path.join(script_name)
        print('\n## Executing script {}'.format(script))
        exec(open(script).read())

