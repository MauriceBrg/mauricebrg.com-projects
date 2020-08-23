import click

if __name__ == "__main__":
    click.echo("This is unstyled text")
    click.echo(
        click.style("Red ", fg= "red") +
        click.style("Green ", fg="green") +
        click.style("Blue ", fg="blue", dim=True) +
        "Unstyled"
    )

    click.secho("BOLD yellow text", fg="yellow", bold=True)
    click.secho("Underlined magenta text", fg="magenta", underline=True)
    click.secho("BOLD underlined cyan text", fg="cyan", bold=True, underline=True)

    click.secho("BOLD white foreground with ugly cyan background", bold=True, bg="cyan")
