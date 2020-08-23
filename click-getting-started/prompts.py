import click

@click.group()
def cli() -> None:
    """Demos for various prompts"""

@cli.command()
def confirm_as_variable() -> None:
    """Asks the user for confirmation and stores the response in a variable"""

    confirmed = click.confirm("Are you sure you want to drop the users table?")
    status = click.style("yes", fg="green") if confirmed else click.style("no", fg="red")
    click.echo("Drop table confirmed?: " + status)

@cli.command()
def confirm_with_abort() -> None:
    """Asks the user for confirmation and aborts if that doesn't happen."""

    click.confirm(
        "Are you sure you want to drop the users table?",
        abort=True
    )

    click.echo("We have gotten to this point, so the user has confirmed.")

@cli.command()
def prompt() -> None:
    """Shows examples for the use of click.prompt"""

    username = click.prompt(
        text="Please enter a username",
        type=click.STRING
    )
    password = click.prompt(
        text="Please enter a new password",
        hide_input=True,
        confirmation_prompt=True
    )
    newsletter_subscription = click.prompt(
        text="Would you like to subscribe to our newsletter?",
        default=False,
        type=click.BOOL
    )
    favorite_color=click.prompt(
        text="What is your favorite color?",
        type=click.Choice(["blue", "green", "yellow"], case_sensitive=False)
    )

    click.echo(
        f"Username: {username} | Password: {'*' * len(password)} | "
        + f"Newsletter: {newsletter_subscription} | Favorite color: "
        + click.style(favorite_color, fg=favorite_color)
    )

@cli.command()
@click.option("--username", prompt=True)
@click.password_option()
@click.option("--age", prompt="How old are you?", type=click.INT)
def option_prompt(username, password, age) -> None:
    
    click.echo(f"Username: {username}")
    click.echo(f"Password: { '*' * len(password)}")
    click.echo(f"Age: {age}")

if __name__ == "__main__":
    cli()