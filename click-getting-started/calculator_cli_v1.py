import operator
import click

@click.command()
@click.argument("a", type=click.INT)
@click.argument("b", type=click.INT)
@click.option(
    "--operation", "--op",
    type=click.Choice(["add", "subtract", "multiply", "divide"]),
    default="add",
    help="Operation to perform on the operands, default: add")
def cli(a: int, b: int, operation: str):
    """
    This is an implementation of a basic calculator.

    By default this adds the two operands A and B.
    You can change that using the --operation parameter.
    """

    operation_sign_mapping = {"add": "+", "subtract": "-",
                              "multiply": "*", "divide": "/"}

    operation_callable_mapping = {
        "add": operator.add, "subtract": operator.sub,
        "multiply": operator.mul, "divide": operator.truediv,
    }

    result_of_operation = operation_callable_mapping[operation](a,b)
    sign = operation_sign_mapping[operation]

    click.echo(f"{a} {sign} {b} = {result_of_operation}")

if __name__ == "__main__":
    cli()
