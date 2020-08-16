import click

@click.command()
def cli():
    """
    Prints "Hello World!" and exits.
    """
    click.echo("Hello World!")

if __name__ == "__main__":
    cli()
