# About

Bash and Zsh completion for [Walrus CLI](https://docs.walrus.site/usage/client-cli.html)

Detects commands, subcommands and flags by parsing the CLI output. A whitelist is used to select the target CLIs.

Python Walrus CLI for easy usage.

Uses walrus cli in a user-friendly way. For requirements it depends on the walrus binary and python 3 to run.

# Installation

Bash:

```sh
wget https://raw.githubusercontent.com/StakinOfficial/walrus-completion/refs/heads/main/walrus_completion.sh -O ~/walrus_completion.sh && echo "source ~/walrus_completion.sh" >> ~/.bashrc

```

Zsh:

```sh
wget https://raw.githubusercontent.com/StakinOfficial/walrus-completion/refs/heads/main/walrus_completion.zsh -O ~/walrus_completion.zsh && echo "source ~/walrus_completion.zsh" >> ~/.zshrc
```

Walrus Python CLI:
```
wget https://raw.githubusercontent.com/StakinOfficial/walrus-completion/refs/heads/main/walrus.py
```

# Usage

Walrus Python CLI

```
python3 walrus.py
```
# License

MIT


