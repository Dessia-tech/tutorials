import os

list_script = [f'scripts/{script_name}' for script_name in os.listdir('scripts') if script_name.endswith('.py')]

print('Executing scripts for CI:')
top_level_dir = os.getcwd()

for script_name in list_script:
    if not os.path.isfile(os.path.join(top_level_dir, script_name)):
        raise FileNotFoundError(f'Script {script_name} not exist in directory')

    print(f'\t* {script_name}')
    os.chdir(top_level_dir)
    if '/' in script_name:
        script_folder = '/'.join(script_name.split('/')[:-1])
        if script_folder:
            script_folder = os.path.join(top_level_dir, script_folder)
            os.chdir(script_folder)
    file_name = script_name.split('/')[-1]

    with open(file_name, 'r', encoding='utf-8') as script:
        try:
            exec(script.read())
            print(f"Script '{script_name}' successful.")
        except Exception as e:
            raise Exception('Error executing script {}: {}'.format(file_name, e))

