
import os

for script_name in os.listdir('scripts'):
    script = os.path.join('scripts', script_name)
    print('\n## Executing script {}'.format(script))
    exec(open(script).read())
