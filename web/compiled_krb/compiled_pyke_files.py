# compiled_pyke_files.py

from pyke import target_pkg

pyke_version = '1.1.1'
compiler_version = 1
target_pkg_version = 1

try:
    loader = __loader__
except NameError:
    loader = None

def get_target_pkg():
    return target_pkg.target_pkg(__name__, __file__, pyke_version, loader, {
         ('', '', 'ca_rules_questions.krb'):
           [1622971837.330402, 'ca_rules_questions_bc.py'],
         ('', '', 'questions.kqb'):
           [1622971837.3450036, 'questions.qbc'],
         ('', '', 'pyke\\krb_compiler\\compiler.krb'):
           [1622971837.4011953, 'compiler_bc.py'],
        },
        compiler_version)

