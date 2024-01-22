import os

for script_name in os.listdir('scripts'):
    if script_name.endswith('.py'):
        script = os.path.join('scripts', script_name)
        print('\n## Executing script {}'.format(script))

        with open(script, "r") as script_file:
            try:
                exec(script_file.read())
            except Exception as e:
                print('Error executing script {}: {}'.format(script, e))
                raise e

