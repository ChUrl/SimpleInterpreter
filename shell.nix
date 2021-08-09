{ pkgs ? import <nixpkgs> {} }:

with pkgs;

let myPython = python39.buildEnv.override {
      extraLibs = with python39Packages; [
        # Common Libs
        rich
        # numpy
        # matplotlib
        # scipy
        # pytorch
        # notbook
        
        # Doom Emacs Libs
        black
        pyflakes
        isort
        nose
        pytest

        # DynLang
        rply
      ];
    };
in

mkShell {
  buildInputs = [
    myPython
    nodePackages.pyright # LSP
    pipenv # Doom
    jetbrains.pycharm-professional
  ];
}
