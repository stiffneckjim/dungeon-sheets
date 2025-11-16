pipx ensurepath

autoload -U compinit && compinit

eval "$(starship init zsh)"
eval "$(register-python-argcomplete pipx)"
eval "$(fnm env --shell zsh)"
