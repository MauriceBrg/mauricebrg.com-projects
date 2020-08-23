import time
import click

@click.group()
def cli():
    """Demonstrations of different progress bars."""

@cli.command("iterable")
def progress_over_iterable():
    """
    Demonstrates how a progress bar can be tied to processing of an iterable.
    """

    # Could be a list, tuple and a whole bunch of other containers
    iterable = range(256)

    label_text = "Processing items in the iterable..."

    with click.progressbar(iterable, label=label_text) as items:
        for item in items:
            # Do some processing
            time.sleep(0.023) # This is really hard work

@cli.command("iterable-with-colors")
def progress_over_iterable_with_colors():
    """
    Demonstrates how a progress bar can be tied to processing of an iterable.
    """

    # Could be a list, tuple and a whole bunch of other containers
    iterable = range(256)

    fill_char = click.style("#", fg="green")
    empty_char = click.style("-", fg="white", dim=True)
    label_text = "Processing items in the iterable..."

    with click.progressbar(
            iterable=iterable,
            label=label_text,
            fill_char=fill_char,
            empty_char=empty_char
        ) as items:
        for item in items:
            # Do some processing
            time.sleep(0.023) # This is really hard work

@cli.command("progress-without-iterable")
def progress_bar_without_iterable() -> None:
    """
    Demonstrates a progress bar without an iterable to
    iterate over.
    """

    with click.progressbar(label="Processing",
                           length=100,
                           show_eta=False) as progress_bar:
        click.echo("Starting progress bar")
        progress_bar.update(0)
        time.sleep(1.01)
        progress_bar.update(25)
        time.sleep(1.25)
        progress_bar.update(25)
        time.sleep(2)
        progress_bar.update(25)
        time.sleep(3)
        progress_bar.update(25)

if __name__ == "__main__":
    cli()
