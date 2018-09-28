#!/usr/bin/env python3
"""
Configure python development environment.
Only work for linux that use bash!
And python3.6+ is required.
"""
import os
import re
from pathlib import Path


FILES = ALIAS_FILE, *_ = [
    ".bash_aliases",
    ".pipenv_install_while_lock_at_another_process.py",
    ".switch_source_pipenv.py",
    ".mg.py",
    ".vimrc",
]

PACKAGES = "pipenv ipython django pylint flake8 white black"


def main():
    home = Path.home()
    aliases_path = home / ALIAS_FILE
    if aliases_path.exists():
        a = input(f"`{aliases_path}` exists. Continue and replace it?[y/(n)] ")
        if not a.lower().strip().startswith("y"):
            return
    try:
        repo = Path(__file__).parent.resolve()
    except NameError:
        repo = Path(".").resolve()
    for fn in FILES:
        os.system(f"cp {repo / fn} {home}")
    s = aliases_path.read_text()
    ss = re.sub(r'(rstrip=")(.*)"', rf'\1{repo/"rstrip.py"}"', s)
    with os.popen("alias") as fp:
        if "alias vi=" not in fp.read():
            ss += "alias vi=vim\n"
    if s != ss:
        aliases_path.write_text(ss)
    # auto complete for command `mg`
    mg_completion_path = home / ".mg_completion.bash"
    if not mg_completion_path.exists():
        fname = "django_manage_completion.bash"
        sys_completion_path = Path("/etc/bash_completion.d")
        if sys_completion_path.exists():
            if not sys_completion_path.joinpath(fname).exists():
                os.system(f"sudo cp {repo/fname} {sys_completion_path}")
        else:
            os.system(f"cp {repo/fname} {mg_completion_path}")
    # append mg and git completion activate alias to aliases file
    if mg_completion_path.exists():
        a = f"source {mg_completion_path}"
    else:
        a = f"source {sys_completion_path/fname}"
    git_completion_path = Path("/etc/bash_completion.d/git-completion.bash")
    if git_completion_path.exists():
        a += f"&&source {git_completion_path}"
    if a not in aliases_path.read_text():
        os.system(f"echo 'alias activate_completion=\"{a}\"'>>{aliases_path}")
    # activate aliases at .bashrc
    bashrc = home / ".bashrc"
    if ALIAS_FILE not in bashrc.read_text():
        with bashrc.open("a") as fp:
            fp.write(f"[[ -f ~/{ALIAS_FILE} ]] && . ~/{ALIAS_FILE}")
    # switch pip source to aliyun
    swith_pip_source = repo / "pip_conf.py"
    os.system(f"{swith_pip_source}")
    os.system("sudo cp -r ~/.pip /home/root/")
    # git push auto fill in username and password after input once
    os.system("git config --global credential.helper store")
    # Install some useful python modules
    if os.system(f"python3 -m pip install --upgrade --user {PACKAGES}") != 0:
        if os.system(f"sudo pip3 install -U {PACKAGES}") != 0:
            print("Please install python3-pip and then rerun this script.")
            return
    # make sure pipenv work
    if os.system("pipenv --version") != 0:
        with os.popen("which python3") as p:
            cmd = f"{p.read()} -m pipenv"
        os.system(f"echo 'alias pipenv=\"{cmd}\"'>>{aliases_path}")
    # add pipenv auto complete to user profile
    a = 'eval "$(pipenv --completion)"'
    ps = home.glob(".*profile")
    for p in ps:
        if p.name not in (".profile", ".bash_profile"):
            continue
        if a in p.read_text():
            print(f"`{a}` already in {p}")
            continue
        cmd = f"echo '{a}'>>{p}"
        os.system(cmd)
        print(cmd)
        os.system(f"bash {p}")
        print(f"`{p}` activated")
        break
    else:
        p = bashrc
        os.system(f". {bashrc}")
        print(f"`{bashrc}` activated")
    if mg_completion_path.exists():
        if mg_completion_path.name not in p.read_text():
            os.system(f"echo '# django manage completion'>>{p}")
            a = f"[[ -f {mg_completion_path} ]] && . {mg_completion_path}"
            os.system(f"echo '{a}' >> {p}")
    print("Done!")


if __name__ == "__main__":
    main()
