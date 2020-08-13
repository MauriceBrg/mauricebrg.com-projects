import math
import typing
import click

@click.group()
def cli():
    """
    This is a calculator that supports basic arithmetic operations.
    """

@cli.command()
@click.argument("minuend", type=click.INT)
@click.argument("subtrahend", type=click.INT)
def subtract(minuend: int, subtrahend: int) -> int:
    """
    Returns the difference between MINUEND and SUBTRAHEND.
    """
    click.echo(f"{minuend} - {subtrahend} = {minuend - subtrahend}")

@cli.command()
@click.argument("addends", type=click.INT, nargs=-1)
def add(addends: typing.Tuple[int]) -> int:
    """
    Returns the sum of ADDENDS.
    """
    click.echo(f'{ " + ".join([str(x) for x in addends])} = {sum(addends)}')

@cli.command()
@click.argument("factors", type=click.INT, nargs=-1)
def multiply(factors: typing.Tuple[int]) -> int:
    """Returns the product of a list of FACTORS."""

    product = math.prod(factors)

    click.echo(f'{ " * ".join([str(x) for x in factors])} = {product}')

def validate_divisor(ctx: click.core.Context, param: click.core.Argument, value: str):
    """
    Validation logic for the divisor, ensures it can be converted to an int and isn't 0
    """

    try:
        value_as_int = int(value)

        if value_as_int == 0:
            raise click.BadParameter("Can't divide by Zero!")

        return value_as_int
    except ValueError:
        raise click.BadParameter("Expected something that can be parsed to int.")

@cli.command()
@click.argument("divident", type=click.INT)
@click.argument("divisor", callback=validate_divisor)
def divide(divident: int, divisor: int) -> float:
    """Returns DIVIDENT / DIVISOR."""
    click.echo(f"{divident} / {divisor} = {divident/divisor}")


if __name__ == "__main__":
    cli()