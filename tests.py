import os

list_script = [script_name for script_name in os.listdir('scripts') if script_name.endswith('.py')]


for script_name in list_script:
    print(f"\n## Executing script '{script_name}'.")
    script = os.path.join('scripts', script_name)
    with open(script, "r") as script_file:
        try:
            exec(script_file.read())
            print(f"Script '{script_name}' successful.")
        except Exception as e:
            raise Exception('Error executing script {}: {}'.format(script, e))

