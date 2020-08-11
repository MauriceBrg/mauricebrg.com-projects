#! /usr/bin/env python3
import click

@click.group()
def cli():
    """
    This is a first Click CLI project, which is used to demo some of the common features for click.
    """

@click.command()
@click.argument("a", type=click.INT)
@click.argument("b", type=click.INT)
def add(a: int, b: int):
    """
    Adds two integers A and B.
    """
    # This shows a very simple command with basic input validation - it will ony allow integers to be
    # passed as the values for a and b and will display a helpful error message otherwise.
    click.echo(f"{a} + {b} = {a + b}")

if __name__ == "__main__":
    cli.add_command(add)
    cli()