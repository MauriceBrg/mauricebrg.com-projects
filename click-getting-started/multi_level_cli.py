"""This demonstrates a multi-level cli structure"""
import click

@click.group("first-level")
def cli():
    """Top level"""

@cli.group("second-level-1")
def second_level_1():
    """Second level 1"""

@cli.group("second-level-2")
def second_level_2():
    """Second level 2"""

@second_level_1.command()
def third_level_command_1():
    """Third level command under 2nd level 1"""

@second_level_1.command()
def third_level_command_2():
    """Third level command under 2nd level 1"""

@second_level_2.command()
def third_level_command_3():
    """Third level command under 2nd level 2"""

if __name__ == "__main__":
    cli()
