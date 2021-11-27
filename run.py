import click
from bot import get_bot


@click.command()
@click.option("--use-color", "--use-colour", "-c", type=bool, default=True)
def main(use_color: bool):
    bot, token = get_bot(use_colour=use_color)
    bot.run(token)


if __name__ == "__main__":
    main()