# I don't know how to python properly, don't take this as an example just yet!

import os
import shutil
import datetime

from invoke import Collection, task
from shutil import which
from pathlib import Path
from subprocess import call

ROOT_DIR = os.path.dirname(__file__)
REVIEW_SOURCE_DIR = "/home/manu/notes/resources/books/reviews"
CONTENT_DIR = "./content"

@task
def check_zola(ctx):
    zola = which('zola')
    if not zola:
        msg = ("Couldn’t find `zola`, please install it first!")
        raise SystemExit(msg)

@task
def check_fzf(ctx):
    fzf = which('fzf')
    if not fzf:
        msg = ("Couldn’t find `fzf`, please install it first!")
        raise SystemExit(msg)

@task
def check_browser(ctx):
    browser = which(os.environ['BROWSER'])
    if not browser:
        msg = ("Please set your browser in $BROWSER!")
        raise SystemExit(msg)
    which_browser = which(browser)
    if not which_browser:
        msg = ("Browser defined in $BROWSER not found")
        raise SystemExit(msg)

@task
def check_editor(ctx):
    editor = which(os.environ['EDITOR'])
    if not editor:
        msg = ("Please set your editor in $EDITOR!")
        raise SystemExit(msg)
    which_editor = which(editor)
    if not which_editor:
        msg = ("Editor defined in $EDITOR not found!")
        raise SystemExit(msg)

@task
def reviews(ctx):
    """Copy reviews to content"""
    with ctx.cd(ROOT_DIR):
        ctx.run("rsync -a {} {} --delete".format(REVIEW_SOURCE_DIR, CONTENT_DIR))

@task(pre=[check_zola])
def build(ctx):
    """Build the website"""
    with ctx.cd(ROOT_DIR):
        ctx.run("zola build")

@task(pre=[check_zola,check_browser])
def serve(ctx):
    """Build and serve preview"""
    ctx.run("$BROWSER http://localhost:1111/")
    print(">>> You might have to refresh the page once before seeing the result!")
    with ctx.cd(ROOT_DIR):
        ctx.run("zola serve")

@task
def clean(ctx):
    """Clean generated files"""
    public_path = Path('public')
    with ctx.cd(ROOT_DIR):
        if public_path.exists() and public_path.is_dir():
            print("Removing public directory...")
            shutil.rmtree(public_path)

@task(pre=[check_editor])
def config(ctx):
    """Edit config file"""
    config_file = ROOT_DIR + "/config.toml"
    config_path = Path(config_file)
    if not config_path.exists():
        msg = ("Config file not found!")
        raise SystemExit(msg)
    editor = which(os.environ['EDITOR'])
    call([editor, config_file])

@task(pre=[check_fzf,check_editor])
def edit(ctx):
    """Edit content"""
    with ctx.cd(ROOT_DIR):
        result = ctx.run("find ./content -name \"*.md\" | fzf")
        file = result.stdout
        file = file[:-1]
        editor = which(os.environ['EDITOR'])
        call([editor, file])
